from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import UserRole
from infrastructure.database.rls.context import temporary_admin_context

from .models import Notification


@transaction.atomic
def create_notification(*, recipient, event_type, action_url="", payload=None):
    with temporary_admin_context():
        return Notification.objects.create(
            recipient=recipient,
            event_type=event_type,
            action_url=action_url,
            payload=payload or {},
        )


def notify_administrators(*, event_type, action_url="", payload=None):
    """Create an individually readable notification for every active admin."""
    User = get_user_model()
    with temporary_admin_context():
        recipients = list(
            User.objects.filter(role=UserRole.ADMIN, is_active=True).only("id")
        )
        Notification.objects.bulk_create(
            [
                Notification(
                    recipient=user,
                    event_type=event_type,
                    action_url=action_url,
                    payload=payload or {},
                )
                for user in recipients
            ]
        )


def notify_users(*, event_type, action_url="", payload=None):
    """Fan out a notification to active non-admin accounts in bounded batches."""
    User = get_user_model()
    batch = []
    with temporary_admin_context():
        recipients = User.objects.filter(role=UserRole.USER, is_active=True).only("id")
        for recipient in recipients.iterator(chunk_size=500):
            batch.append(
                Notification(
                    recipient_id=recipient.id,
                    event_type=event_type,
                    action_url=action_url,
                    payload=payload or {},
                )
            )
            if len(batch) == 500:
                Notification.objects.bulk_create(batch, batch_size=500)
                batch.clear()
        if batch:
            Notification.objects.bulk_create(batch, batch_size=500)


def mark_notification_read(*, notification):
    if notification.read_at is None:
        notification.read_at = timezone.now()
        notification.save(update_fields=["read_at"])
    return notification
