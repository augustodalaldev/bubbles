import re

from apps.core.uploads import UploadTo


def test_upload_path_uses_folder_random_name_and_lowercase_extension():
    path = UploadTo("profile_photos")(None, "My Holiday.PNG")

    assert re.fullmatch(r"profile_photos/[0-9a-f]{32}\.png", path)


def test_upload_path_discards_original_name_and_directories():
    path = UploadTo("pics")(None, "../../etc/passwd.jpg")

    assert "passwd" not in path
    assert ".." not in path


def test_upload_paths_are_unique():
    upload_to = UploadTo("pics")

    assert upload_to(None, "a.jpg") != upload_to(None, "a.jpg")


def test_upload_to_is_serializable_by_migrations():
    path, args, kwargs = UploadTo("pics").deconstruct()

    assert path == "apps.core.uploads.UploadTo"
    assert args == ("pics",)
    assert kwargs == {}
