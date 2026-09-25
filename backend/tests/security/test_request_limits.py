from django.conf import settings


def test_application_request_and_file_limits_are_explicit():
    assert settings.DATA_UPLOAD_MAX_MEMORY_SIZE == 10 * 1024 * 1024
    assert settings.FILE_UPLOAD_MAX_MEMORY_SIZE == 5 * 1024 * 1024
