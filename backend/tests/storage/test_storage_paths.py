from apps.content.models import FoundingMember, SliderItem
from apps.profiles.models import Profile
from infrastructure.storage.paths import (
    FOUNDING_MEMBER_PATH,
    PROFILE_PATH,
    SLIDER_PATH,
    founding_member_upload_path,
    profile_upload_path,
    slider_upload_path,
)


def test_profile_upload_paths_are_unique_and_do_not_trust_user_filenames():
    first = profile_upload_path(Profile(), "../../my photo.PNG")
    second = profile_upload_path(Profile(), "../../my photo.PNG")

    assert first.startswith(f"{PROFILE_PATH}/")
    assert first.endswith(".png")
    assert first != second
    assert "my photo" not in first
    assert ".." not in first


def test_content_upload_paths_use_their_expected_prefixes():
    founding_path = founding_member_upload_path(FoundingMember(), "member.webp")
    slider_path = slider_upload_path(SliderItem(), "slider.jpeg")

    assert founding_path.startswith(f"{FOUNDING_MEMBER_PATH}/")
    assert slider_path.startswith(f"{SLIDER_PATH}/")
