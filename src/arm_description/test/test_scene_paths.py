from arm_description.paths import scene_path


def test_scene_files_exist():
    assert scene_path("scene.xml").is_file()
    assert scene_path("pick_and_place.xml").is_file()
    assert scene_path("pick_and_place_tables.xml").is_file()
