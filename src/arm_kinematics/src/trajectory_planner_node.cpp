#include <algorithm>
#include <cmath>
#include <memory>
#include <mutex>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>

#include <control_msgs/action/follow_joint_trajectory.hpp>
#include <Eigen/Dense>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <kdl/chain.hpp>
#include <kdl/chainfksolverpos_recursive.hpp>
#include <kdl/chainiksolverpos_nr_jl.hpp>
#include <kdl/chainiksolvervel_pinv.hpp>
#include <kdl/chainjnttojacsolver.hpp>
#include <kdl/frames.hpp>
#include <kdl/jacobian.hpp>
#include <kdl/jntarray.hpp>
#include <kdl_parser/kdl_parser.hpp>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/joint_state.hpp>
#include <trajectory_msgs/msg/joint_trajectory.hpp>
#include <trajectory_msgs/msg/joint_trajectory_point.hpp>

#include "arm_interfaces/srv/get_fk.hpp"
#include "arm_interfaces/srv/move_to_pose.hpp"
#include "arm_interfaces/srv/solve_ik.hpp"

namespace
{

using GetFk = arm_interfaces::srv::GetFk;
using MoveToPose = arm_interfaces::srv::MoveToPose;
using SolveIk = arm_interfaces::srv::SolveIk;

constexpr double kDefaultDuration = 4.0;

KDL::Frame poseToFrame(const geometry_msgs::msg::Pose & pose)
{
  return KDL::Frame(
    KDL::Rotation::Quaternion(
      pose.orientation.x,
      pose.orientation.y,
      pose.orientation.z,
      pose.orientation.w),
    KDL::Vector(pose.position.x, pose.position.y, pose.position.z));
}

geometry_msgs::msg::Pose frameToPose(const KDL::Frame & frame)
{
  geometry_msgs::msg::Pose pose;
  pose.position.x = frame.p.x();
  pose.position.y = frame.p.y();
  pose.position.z = frame.p.z();
  frame.M.GetQuaternion(
    pose.orientation.x,
    pose.orientation.y,
    pose.orientation.z,
    pose.orientation.w);
  return pose;
}

builtin_interfaces::msg::Duration secondsToDuration(double seconds)
{
  seconds = std::max(0.0, seconds);
  builtin_interfaces::msg::Duration duration;
  duration.sec = static_cast<int32_t>(std::floor(seconds));
  duration.nanosec =
    static_cast<uint32_t>((seconds - static_cast<double>(duration.sec)) * 1e9);
  return duration;
}

std::string formatJoints(const KDL::JntArray & joints)
{
  std::ostringstream stream;
  stream << "[";
  for (unsigned int i = 0; i < joints.rows(); ++i) {
    if (i > 0) {
      stream << ", ";
    }
    stream << joints(i);
  }
  stream << "]";
  return stream.str();
}

}  // namespace

class TrajectoryPlannerNode : public rclcpp::Node
{
public:
  TrajectoryPlannerNode()
  : Node("trajectory_planner_node")
  {
    base_link_ = declare_parameter<std::string>("base_link", "base_link");
    tip_link_ = declare_parameter<std::string>("tip_link", "tool0");
    joint_state_topic_ = declare_parameter<std::string>("joint_state_topic", "/joint_states");
    trajectory_topic_ =
      declare_parameter<std::string>("trajectory_topic", "/arm_controller/joint_trajectory");
    fk_topic_ = declare_parameter<std::string>("fk_topic", "/end_effector_pose");
    planning_steps_ = declare_parameter<int>("planning_steps", 100);
    ik_max_iterations_ = declare_parameter<int>("ik_max_iterations", 100);
    ik_tolerance_ = declare_parameter<double>("ik_tolerance", 1e-5);
    position_only_ik_max_iterations_ =
      declare_parameter<int>("position_only_ik_max_iterations", 300);
    position_only_ik_tolerance_ = declare_parameter<double>("position_only_ik_tolerance", 1e-4);
    position_only_ik_damping_ = declare_parameter<double>("position_only_ik_damping", 0.02);
    joint_names_ = declare_parameter<std::vector<std::string>>(
      "joint_names",
      {
        "shoulder_pan_joint",
        "shoulder_lift_joint",
        "elbow_joint",
        "wrist_1_joint",
        "wrist_2_joint",
        "wrist_3_joint",
      });
    joint_min_limits_ = declare_parameter<std::vector<double>>(
      "joint_min_limits",
      {-6.283185307, -6.283185307, -3.141592654, -6.283185307, -6.283185307, -6.283185307});
    joint_max_limits_ = declare_parameter<std::vector<double>>(
      "joint_max_limits",
      {6.283185307, 6.283185307, 3.141592654, 6.283185307, 6.283185307, 6.283185307});

    if (!configureKdl()) {
      throw std::runtime_error("Failed to configure KDL chain");
    }

    fk_solver_ = std::make_unique<KDL::ChainFkSolverPos_recursive>(chain_);
    ik_vel_solver_ = std::make_unique<KDL::ChainIkSolverVel_pinv>(chain_);
    jac_solver_ = std::make_unique<KDL::ChainJntToJacSolver>(chain_);
    ik_solver_ = std::make_unique<KDL::ChainIkSolverPos_NR_JL>(
      chain_,
      joint_min_,
      joint_max_,
      *fk_solver_,
      *ik_vel_solver_,
      ik_max_iterations_,
      ik_tolerance_);

    joint_state_sub_ = create_subscription<sensor_msgs::msg::JointState>(
      joint_state_topic_,
      10,
      std::bind(&TrajectoryPlannerNode::onJointState, this, std::placeholders::_1));
    fk_pub_ = create_publisher<geometry_msgs::msg::PoseStamped>(fk_topic_, 10);
    trajectory_pub_ =
      create_publisher<trajectory_msgs::msg::JointTrajectory>(trajectory_topic_, 10);

    fk_service_ = create_service<GetFk>(
      "compute_fk",
      std::bind(
        &TrajectoryPlannerNode::onComputeFk,
        this,
        std::placeholders::_1,
        std::placeholders::_2));
    ik_service_ = create_service<SolveIk>(
      "solve_ik",
      std::bind(
        &TrajectoryPlannerNode::onSolveIk,
        this,
        std::placeholders::_1,
        std::placeholders::_2));
    move_service_ = create_service<MoveToPose>(
      "move_to_pose",
      std::bind(
        &TrajectoryPlannerNode::onMoveToPose,
        this,
        std::placeholders::_1,
        std::placeholders::_2));

    RCLCPP_INFO(
      get_logger(),
      "KDL motion pipeline ready: %s -> %s, trajectory topic %s",
      base_link_.c_str(),
      tip_link_.c_str(),
      trajectory_topic_.c_str());
  }

private:
  bool configureKdl()
  {
    const std::string robot_description = declare_parameter<std::string>("robot_description", "");
    if (robot_description.empty()) {
      RCLCPP_ERROR(get_logger(), "Parameter 'robot_description' is empty");
      return false;
    }

    KDL::Tree tree;
    if (!kdl_parser::treeFromString(robot_description, tree)) {
      RCLCPP_ERROR(get_logger(), "Failed to parse robot_description into a KDL tree");
      return false;
    }

    if (!tree.getChain(base_link_, tip_link_, chain_)) {
      RCLCPP_ERROR(
        get_logger(),
        "Failed to build KDL chain from '%s' to '%s'",
        base_link_.c_str(),
        tip_link_.c_str());
      return false;
    }

    const unsigned int joint_count = chain_.getNrOfJoints();
    if (joint_names_.size() != joint_count) {
      RCLCPP_ERROR(
        get_logger(),
        "joint_names has %zu entries, but KDL chain has %u joints",
        joint_names_.size(),
        joint_count);
      return false;
    }

    if (joint_min_limits_.size() != joint_count || joint_max_limits_.size() != joint_count) {
      RCLCPP_ERROR(get_logger(), "Joint limit parameter sizes must match the KDL joint count");
      return false;
    }

    joint_min_.resize(joint_count);
    joint_max_.resize(joint_count);
    for (unsigned int i = 0; i < joint_count; ++i) {
      joint_min_(i) = joint_min_limits_[i];
      joint_max_(i) = joint_max_limits_[i];
    }

    return true;
  }

  void onJointState(const sensor_msgs::msg::JointState::SharedPtr msg)
  {
    std::lock_guard<std::mutex> lock(joint_mutex_);
    latest_joint_positions_.clear();
    for (std::size_t i = 0; i < msg->name.size() && i < msg->position.size(); ++i) {
      latest_joint_positions_[msg->name[i]] = msg->position[i];
    }
    have_joint_state_ = true;

    KDL::JntArray joints;
    if (currentJointsNoLock(joints)) {
      publishFk(joints, msg->header.stamp);
    }
  }

  bool currentJoints(KDL::JntArray & joints)
  {
    std::lock_guard<std::mutex> lock(joint_mutex_);
    return currentJointsNoLock(joints);
  }

  bool currentJointsNoLock(KDL::JntArray & joints)
  {
    if (!have_joint_state_) {
      return false;
    }

    joints.resize(joint_names_.size());
    for (std::size_t i = 0; i < joint_names_.size(); ++i) {
      const auto found = latest_joint_positions_.find(joint_names_[i]);
      if (found == latest_joint_positions_.end()) {
        return false;
      }
      joints(static_cast<unsigned int>(i)) = found->second;
    }
    return true;
  }

  bool requestSeed(const std::vector<double> & seed, KDL::JntArray & joints, std::string & message)
  {
    if (!seed.empty()) {
      if (seed.size() != joint_names_.size()) {
        message = "Seed joint count does not match the arm joint count";
        return false;
      }
      joints.resize(joint_names_.size());
      for (std::size_t i = 0; i < seed.size(); ++i) {
        joints(static_cast<unsigned int>(i)) = seed[i];
      }
      return true;
    }

    if (currentJoints(joints)) {
      return true;
    }

    joints.resize(joint_names_.size());
    for (unsigned int i = 0; i < joints.rows(); ++i) {
      joints(i) = 0.0;
    }
    message = "No current joint state available; using zero seed";
    return true;
  }

  bool checkFrame(const geometry_msgs::msg::PoseStamped & pose, std::string & message) const
  {
    if (!pose.header.frame_id.empty() && pose.header.frame_id != base_link_) {
      message =
        "target_pose.header.frame_id must be empty or '" + base_link_ +
        "'. TF transforms are intentionally not hidden inside this KDL service.";
      return false;
    }
    return true;
  }

  bool computeFk(const KDL::JntArray & joints, KDL::Frame & frame, std::string & message)
  {
    if (joints.rows() != chain_.getNrOfJoints()) {
      message = "Joint count does not match KDL chain";
      return false;
    }

    const int status = fk_solver_->JntToCart(joints, frame);
    if (status < 0) {
      message = "KDL FK solver failed with code " + std::to_string(status);
      return false;
    }
    return true;
  }

  bool solveIk(
    const geometry_msgs::msg::PoseStamped & target_pose,
    const std::vector<double> & seed,
    KDL::JntArray & solution,
    std::string & message)
  {
    if (!checkFrame(target_pose, message)) {
      return false;
    }

    KDL::JntArray seed_joints;
    std::string seed_message;
    if (!requestSeed(seed, seed_joints, seed_message)) {
      message = seed_message;
      return false;
    }

    solution.resize(joint_names_.size());
    const int status = ik_solver_->CartToJnt(seed_joints, poseToFrame(target_pose.pose), solution);
    if (status >= 0) {
      message = seed_message.empty() ? "IK solved" : seed_message + "; IK solved";
      return true;
    }

    const std::string full_pose_error =
      "KDL full-pose IK failed with code " + std::to_string(status) +
      ". Seed was " + formatJoints(seed_joints);
    if (solvePositionOnlyIk(poseToFrame(target_pose.pose).p, seed_joints, solution, message)) {
      message = full_pose_error + "; position-only IK fallback solved";
      return true;
    }

    message = full_pose_error + "; " + message;
    return false;
  }

  bool solvePositionOnlyIk(
    const KDL::Vector & target_position,
    const KDL::JntArray & seed,
    KDL::JntArray & solution,
    std::string & message)
  {
    solution = seed;
    KDL::Frame current_frame;
    KDL::Jacobian jacobian(chain_.getNrOfJoints());

    for (int iteration = 0; iteration < position_only_ik_max_iterations_; ++iteration) {
      const int fk_status = fk_solver_->JntToCart(solution, current_frame);
      if (fk_status < 0) {
        message = "Position-only IK FK step failed with code " + std::to_string(fk_status);
        return false;
      }

      Eigen::Vector3d error(
        target_position.x() - current_frame.p.x(),
        target_position.y() - current_frame.p.y(),
        target_position.z() - current_frame.p.z());
      if (error.norm() < position_only_ik_tolerance_) {
        return true;
      }

      const int jac_status = jac_solver_->JntToJac(solution, jacobian);
      if (jac_status < 0) {
        message = "Position-only IK Jacobian step failed with code " + std::to_string(jac_status);
        return false;
      }

      Eigen::MatrixXd linear_jacobian(3, chain_.getNrOfJoints());
      for (unsigned int column = 0; column < chain_.getNrOfJoints(); ++column) {
        linear_jacobian(0, column) = jacobian.data(0, column);
        linear_jacobian(1, column) = jacobian.data(1, column);
        linear_jacobian(2, column) = jacobian.data(2, column);
      }

      const Eigen::Matrix3d damping =
        position_only_ik_damping_ * position_only_ik_damping_ * Eigen::Matrix3d::Identity();
      const Eigen::VectorXd delta =
        linear_jacobian.transpose() *
        (linear_jacobian * linear_jacobian.transpose() + damping).ldlt().solve(error);

      for (unsigned int joint = 0; joint < solution.rows(); ++joint) {
        const double step = std::clamp(delta(static_cast<Eigen::Index>(joint)), -0.15, 0.15);
        solution(joint) = std::clamp(solution(joint) + step, joint_min_(joint), joint_max_(joint));
      }
    }

    message = "Position-only IK did not converge";
    return false;
  }

  trajectory_msgs::msg::JointTrajectory planJointTrajectory(
    const KDL::JntArray & start,
    const KDL::JntArray & goal,
    double duration) const
  {
    trajectory_msgs::msg::JointTrajectory trajectory;
    trajectory.header.stamp = now();
    trajectory.joint_names = joint_names_;

    const int steps = std::max(2, planning_steps_);
    const double total_duration = duration > 0.0 ? duration : kDefaultDuration;
    trajectory.points.reserve(static_cast<std::size_t>(steps));

    for (int step = 1; step <= steps; ++step) {
      const double ratio = static_cast<double>(step) / static_cast<double>(steps);
      trajectory_msgs::msg::JointTrajectoryPoint point;
      point.positions.resize(joint_names_.size());
      point.velocities.assign(joint_names_.size(), 0.0);

      for (std::size_t joint = 0; joint < joint_names_.size(); ++joint) {
        const unsigned int index = static_cast<unsigned int>(joint);
        point.positions[joint] = start(index) + ratio * (goal(index) - start(index));
      }
      point.time_from_start = secondsToDuration(total_duration * ratio);
      trajectory.points.push_back(point);
    }

    return trajectory;
  }

  void publishFk(const KDL::JntArray & joints, const rclcpp::Time & stamp)
  {
    KDL::Frame frame;
    std::string message;
    if (!computeFk(joints, frame, message)) {
      RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 2000, "%s", message.c_str());
      return;
    }

    geometry_msgs::msg::PoseStamped pose;
    pose.header.stamp = stamp;
    pose.header.frame_id = base_link_;
    pose.pose = frameToPose(frame);
    fk_pub_->publish(pose);
  }

  void onComputeFk(
    const std::shared_ptr<GetFk::Request> request,
    std::shared_ptr<GetFk::Response> response)
  {
    KDL::JntArray joints;
    std::string message;
    if (!request->joints.empty()) {
      if (request->joints.size() != joint_names_.size()) {
        response->success = false;
        response->message = "Request joint count does not match the arm joint count";
        return;
      }
      joints.resize(joint_names_.size());
      for (std::size_t i = 0; i < request->joints.size(); ++i) {
        joints(static_cast<unsigned int>(i)) = request->joints[i];
      }
    } else if (!currentJoints(joints)) {
      response->success = false;
      response->message = "No joints in request and no /joint_states received yet";
      return;
    }

    KDL::Frame frame;
    response->success = computeFk(joints, frame, response->message);
    if (response->success) {
      response->message = "FK solved";
      response->pose.header.stamp = now();
      response->pose.header.frame_id = base_link_;
      response->pose.pose = frameToPose(frame);
    }
  }

  void onSolveIk(
    const std::shared_ptr<SolveIk::Request> request,
    std::shared_ptr<SolveIk::Response> response)
  {
    KDL::JntArray solution;
    response->success = solveIk(request->target_pose, request->seed, solution, response->message);
    if (!response->success) {
      return;
    }

    response->joints.resize(joint_names_.size());
    for (std::size_t i = 0; i < joint_names_.size(); ++i) {
      response->joints[i] = solution(static_cast<unsigned int>(i));
    }

    KDL::Frame solved_frame;
    if (computeFk(solution, solved_frame, response->message)) {
      response->solved_pose.header.stamp = now();
      response->solved_pose.header.frame_id = base_link_;
      response->solved_pose.pose = frameToPose(solved_frame);
    }
  }

  void onMoveToPose(
    const std::shared_ptr<MoveToPose::Request> request,
    std::shared_ptr<MoveToPose::Response> response)
  {
    RCLCPP_INFO(
      get_logger(),
      "move_to_pose request: frame='%s', xyz=(%.3f, %.3f, %.3f), duration=%.3f, execute=%s",
      request->target_pose.header.frame_id.c_str(),
      request->target_pose.pose.position.x,
      request->target_pose.pose.position.y,
      request->target_pose.pose.position.z,
      request->duration,
      request->execute ? "true" : "false");

    KDL::JntArray start;
    if (!currentJoints(start) && !request->seed.empty()) {
      std::string seed_message;
      if (!requestSeed(request->seed, start, seed_message)) {
        response->success = false;
        response->message = seed_message;
        RCLCPP_WARN(get_logger(), "move_to_pose rejected: %s", response->message.c_str());
        return;
      }
    } else if (start.rows() == 0) {
      response->success = false;
      response->message = "No current joint state available; cannot plan trajectory start";
      RCLCPP_WARN(get_logger(), "move_to_pose rejected: %s", response->message.c_str());
      return;
    }

    KDL::JntArray goal;
    response->success = solveIk(request->target_pose, request->seed, goal, response->message);
    if (!response->success) {
      RCLCPP_WARN(get_logger(), "move_to_pose IK failed: %s", response->message.c_str());
      return;
    }

    response->joints.resize(joint_names_.size());
    for (std::size_t i = 0; i < joint_names_.size(); ++i) {
      response->joints[i] = goal(static_cast<unsigned int>(i));
    }

    response->trajectory = planJointTrajectory(start, goal, request->duration);
    if (request->execute) {
      trajectory_pub_->publish(response->trajectory);
      response->message += "; trajectory published to " + trajectory_topic_;
    } else {
      response->message += "; trajectory planned but not published because execute=false";
    }
    RCLCPP_INFO(get_logger(), "move_to_pose result: %s", response->message.c_str());
  }

  std::string base_link_;
  std::string tip_link_;
  std::string joint_state_topic_;
  std::string trajectory_topic_;
  std::string fk_topic_;
  int planning_steps_{100};
  int ik_max_iterations_{100};
  int position_only_ik_max_iterations_{300};
  double ik_tolerance_{1e-5};
  double position_only_ik_tolerance_{1e-4};
  double position_only_ik_damping_{0.02};
  std::vector<std::string> joint_names_;
  std::vector<double> joint_min_limits_;
  std::vector<double> joint_max_limits_;

  KDL::Chain chain_;
  KDL::JntArray joint_min_;
  KDL::JntArray joint_max_;
  std::unique_ptr<KDL::ChainFkSolverPos_recursive> fk_solver_;
  std::unique_ptr<KDL::ChainIkSolverVel_pinv> ik_vel_solver_;
  std::unique_ptr<KDL::ChainIkSolverPos_NR_JL> ik_solver_;
  std::unique_ptr<KDL::ChainJntToJacSolver> jac_solver_;

  std::mutex joint_mutex_;
  bool have_joint_state_{false};
  std::unordered_map<std::string, double> latest_joint_positions_;

  rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr joint_state_sub_;
  rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr fk_pub_;
  rclcpp::Publisher<trajectory_msgs::msg::JointTrajectory>::SharedPtr trajectory_pub_;
  rclcpp::Service<GetFk>::SharedPtr fk_service_;
  rclcpp::Service<SolveIk>::SharedPtr ik_service_;
  rclcpp::Service<MoveToPose>::SharedPtr move_service_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<TrajectoryPlannerNode>());
  rclcpp::shutdown();
  return 0;
}
