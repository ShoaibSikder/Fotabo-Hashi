import logging
from html import escape
from urllib.parse import quote, urlencode

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.notifications.models import NotificationEvent
from apps.notifications.services import create_notification, notify_administrators
from apps.profiles.models import Profile
from infrastructure.database.rls.context import temporary_admin_context

logger = logging.getLogger(__name__)
RESEND_EMAILS_ENDPOINT = "https://api.resend.com/emails"
PASSWORD_RESET_SENT = "sent"
PASSWORD_RESET_UNKNOWN_ACCOUNT = "unknown_account"
PASSWORD_RESET_DELIVERY_FAILED = "delivery_failed"


@transaction.atomic
def register_user(*, email, password, name, phone, blood_group, request):
    """Create a regular account/profile and record its creation."""
    with temporary_admin_context():
        user = get_user_model().objects.create_user(email=email, password=password)
        Profile.objects.filter(user=user).update(
            name=name,
            phone=phone,
            blood_group=blood_group,
        )

    create_audit_log(
        actor=user,
        action=AuditAction.CREATE,
        resource_type="User",
        resource_id=user.pk,
        description="A new user account was registered.",
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )
    notify_administrators(
        event_type=NotificationEvent.NEW_ACCOUNT,
        action_url=f"/admin/users?search={quote(user.email, safe='')}",
        payload={"email": user.email},
    )
    create_notification(
        recipient=user,
        event_type=NotificationEvent.NEW_ACCOUNT,
        action_url="/profile",
    )
    with temporary_admin_context():
        refresh = RefreshToken.for_user(user)
    return user, str(refresh.access_token), str(refresh)


def send_password_reset(*, email):
    """Send a reset link and return a safe outcome for the API layer."""
    with temporary_admin_context():
        user = (
            get_user_model().objects.filter(email__iexact=email, is_active=True).first()
        )
    if user is None:
        return PASSWORD_RESET_UNKNOWN_ACCOUNT

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    query = urlencode({"uid": uid, "token": token})
    frontend_url = settings.FRONTEND_BASE_URL.rstrip("/")
    reset_url = f"{frontend_url}/reset-password?{query}"
    text_body = (
        "A password reset was requested for your Fotabo Hashi account.\n\n"
        f"Use this link to choose a new password: {reset_url}\n\n"
        "If you did not request this, you can ignore this email."
    )

    if not settings.RESEND_API_KEY:
        if settings.DEBUG:
            # Keep local development useful before the developer configures Resend.
            sent = bool(
                send_mail(
                    subject="Reset your Fotabo Hashi password",
                    message=text_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            )
            return PASSWORD_RESET_SENT if sent else PASSWORD_RESET_DELIVERY_FAILED
        logger.error("Password reset email not sent: RESEND_API_KEY is not configured.")
        return PASSWORD_RESET_DELIVERY_FAILED

    payload = {
        "from": settings.RESEND_FROM_EMAIL,
        "to": [user.email],
        "subject": "Reset your Fotabo Hashi password",
        "text": text_body,
        "html": (
            "<p>A password reset was requested for your Fotabo Hashi account.</p>"
            f'<p><a href="{escape(reset_url, quote=True)}">Reset your password</a></p>'
            "<p>If you did not request this, you can ignore this email.</p>"
        ),
    }
    try:
        response = requests.post(
            RESEND_EMAILS_ENDPOINT,
            json=payload,
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=settings.RESEND_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return PASSWORD_RESET_SENT
    except requests.RequestException:
        logger.exception("Password reset email delivery through Resend failed.")
        return PASSWORD_RESET_DELIVERY_FAILED


@transaction.atomic
def reset_user_password(*, user, new_password):
    with temporary_admin_context():
        user.set_password(new_password)
        user.save(update_fields=["password", "updated_at"])
        for outstanding in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=outstanding)


@transaction.atomic
def change_user_password(*, user, new_password):
    """Change the authenticated user's password and revoke existing refresh tokens."""
    reset_user_password(user=user, new_password=new_password)
