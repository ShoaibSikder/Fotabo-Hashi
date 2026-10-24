import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.notifications.models import Notification, NotificationEvent
from apps.notifications.services import notify_administrators


@pytest.mark.django_db
def test_notification_list_is_private_and_read_actions_work():
    recipient = User.objects.create_user(
        email="member@example.com", password="MemberPassword123!"
    )
    other = User.objects.create_user(
        email="other@example.com", password="OtherPassword123!"
    )
    notification = Notification.objects.create(
        recipient=recipient,
        event_type=NotificationEvent.REQUEST_UPDATED,
        payload={"status": "FULFILLED"},
        action_url="/requests/7",
    )
    Notification.objects.create(
        recipient=other,
        event_type=NotificationEvent.ANNOUNCEMENT,
    )
    client = APIClient()
    client.force_authenticate(user=recipient)

    response = client.get("/api/v1/notifications/")
    assert response.status_code == 200
    rows = response.data["data"]["results"]
    assert [row["id"] for row in rows] == [notification.id]
    assert rows[0]["is_read"] is False

    marked = client.post(f"/api/v1/notifications/{notification.id}/read/")
    assert marked.status_code == 200
    assert marked.data["is_read"] is True


@pytest.mark.django_db
def test_mark_all_read_only_changes_current_user_notifications():
    recipient = User.objects.create_user(
        email="member@example.com", password="MemberPassword123!"
    )
    other = User.objects.create_user(
        email="other@example.com", password="OtherPassword123!"
    )
    own = Notification.objects.create(
        recipient=recipient, event_type=NotificationEvent.ANNOUNCEMENT
    )
    foreign = Notification.objects.create(
        recipient=other, event_type=NotificationEvent.ANNOUNCEMENT
    )
    client = APIClient()
    client.force_authenticate(user=recipient)

    response = client.post("/api/v1/notifications/read-all/")
    assert response.status_code == 200
    own.refresh_from_db()
    foreign.refresh_from_db()
    assert own.read_at is not None
    assert foreign.read_at is None


@pytest.mark.django_db
def test_admin_events_are_fanned_out_to_active_administrators():
    admin = User.objects.create_user(
        email="admin@example.com", password="AdminPassword123!", role="ADMIN"
    )
    User.objects.create_user(
        email="inactive-admin@example.com",
        password="AdminPassword123!",
        role="ADMIN",
        is_active=False,
    )

    notify_administrators(
        event_type=NotificationEvent.NEW_ACCOUNT,
        payload={"email": "new@example.com"},
    )

    assert Notification.objects.filter(recipient=admin).count() == 1
    assert Notification.objects.count() == 1
