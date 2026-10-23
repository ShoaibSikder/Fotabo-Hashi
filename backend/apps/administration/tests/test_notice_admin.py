import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User, UserRole
from apps.audit.models import AuditLog
from apps.content.models import FoundingMember, Notice
from apps.notifications.models import Notification, NotificationEvent


@pytest.mark.django_db
class TestAdminNoticeManagement:
    def setup_method(self):
        self.admin = User.objects.create_user(
            email="notice-admin@example.com",
            password="AdminPassword123!",
            role=UserRole.ADMIN,
        )
        self.user = User.objects.create_user(
            email="notice-user@example.com", password="UserPassword123!"
        )
        self.client = APIClient()

    def test_only_admin_can_manage_notices(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get("/api/v1/admin/public-content/notices/")

        assert response.status_code == 403

    def test_admin_can_create_and_publish_notice(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            "/api/v1/admin/public-content/notices/",
            {
                "title": "Community blood drive",
                "content": "Join us this Friday.",
                "is_published": True,
            },
            format="json",
        )

        assert response.status_code == 201
        notice = Notice.objects.get()
        assert notice.is_published is True
        assert notice.published_at is not None
        assert AuditLog.objects.filter(resource_type="Notice", action="CREATE").exists()
        notification = Notification.objects.get(recipient=self.user)
        assert notification.event_type == NotificationEvent.ANNOUNCEMENT
        assert notification.payload == {"notice_title": notice.title}
        assert notification.action_url == "/#notices"

    def test_admin_can_edit_unpublish_and_delete_notice(self):
        self.client.force_authenticate(user=self.admin)
        notice = Notice.objects.create(
            title="Draft", content="Draft content", is_published=False
        )

        published = self.client.patch(
            f"/api/v1/admin/public-content/notices/{notice.pk}/",
            {"is_published": True},
            format="json",
        )
        assert published.status_code == 200
        notice.refresh_from_db()
        assert notice.published_at is not None

        unpublished = self.client.patch(
            f"/api/v1/admin/public-content/notices/{notice.pk}/",
            {"is_published": False},
            format="json",
        )
        assert unpublished.status_code == 200
        notice.refresh_from_db()
        assert notice.published_at is None

        deleted = self.client.delete(
            f"/api/v1/admin/public-content/notices/{notice.pk}/"
        )
        assert deleted.status_code == 204
        assert not Notice.objects.filter(pk=notice.pk).exists()


@pytest.mark.django_db
class TestAdminActiveMemberManagement:
    def setup_method(self):
        self.admin = User.objects.create_user(
            email="member-admin@example.com",
            password="AdminPassword123!",
            role=UserRole.ADMIN,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_admin_can_create_reorder_and_unpublish_active_members(self):
        second = self.client.post(
            "/api/v1/admin/public-content/members/",
            {
                "name": "Second Member",
                "social_url": "https://example.com/second",
                "display_order": 2,
                "is_published": True,
            },
            format="json",
        )
        first = self.client.post(
            "/api/v1/admin/public-content/members/",
            {
                "name": "First Member",
                "social_url": "https://example.com/first",
                "display_order": 1,
                "is_published": True,
            },
            format="json",
        )

        assert first.status_code == 201
        assert second.status_code == 201
        public = self.client.get("/api/v1/content/active-members/")
        assert [member["name"] for member in public.data] == [
            "First Member",
            "Second Member",
        ]

        unpublished = self.client.patch(
            f"/api/v1/admin/public-content/members/{first.data['id']}/",
            {"is_published": False, "display_order": 3},
            format="json",
        )
        assert unpublished.status_code == 200
        public = self.client.get("/api/v1/content/active-members/")
        assert [member["name"] for member in public.data] == ["Second Member"]
        assert FoundingMember.objects.get(pk=first.data["id"]).display_order == 3

    def test_member_photo_upload_is_optional_and_stored_under_member_media_path(self):
        from io import BytesIO
        from tempfile import TemporaryDirectory

        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test import override_settings
        from PIL import Image

        image_bytes = BytesIO()
        Image.new("RGB", (40, 40), color="red").save(image_bytes, format="PNG")
        upload = SimpleUploadedFile(
            "member.png", image_bytes.getvalue(), content_type="image/png"
        )

        with TemporaryDirectory() as media_root:
            with override_settings(
                MEDIA_ROOT=media_root,
                STORAGES={
                    "default": {
                        "BACKEND": "infrastructure.storage.backends.LocalMediaStorage"
                    },
                    "staticfiles": {
                        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
                    },
                },
            ):
                response = self.client.post(
                    "/api/v1/admin/public-content/members/",
                    {
                        "name": "Member With Photo",
                        "social_url": "https://example.com/member",
                        "display_order": 0,
                        "is_published": True,
                        "image": upload,
                    },
                    format="multipart",
                )

        assert response.status_code == 201
        member = FoundingMember.objects.get(name="Member With Photo")
        assert member.image.name.startswith("founding-members/")
