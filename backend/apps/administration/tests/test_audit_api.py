import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, UserRole
from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log


@pytest.mark.django_db
def test_audit_api_is_admin_only_and_excludes_sensitive_network_data():
    admin = User.objects.create_user(
        email="admin@example.com", password="AdminPassword123!", role=UserRole.ADMIN
    )
    member = User.objects.create_user(
        email="member@example.com", password="MemberPassword123!"
    )
    create_audit_log(
        actor=member,
        action=AuditAction.LOGIN,
        resource_type="Authentication",
        resource_id=member.pk,
        description="User signed in.",
        ip_address="192.0.2.10",
        user_agent="Private browser details",
        metadata={"private": "not exposed"},
    )
    client = APIClient()
    assert client.get("/api/v1/admin/audit/").status_code == 401
    member_token = str(RefreshToken.for_user(member).access_token)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {member_token}")
    assert client.get("/api/v1/admin/audit/").status_code == 403
    admin_token = str(RefreshToken.for_user(admin).access_token)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
    response = client.get("/api/v1/admin/audit/")
    assert response.status_code == 200
    entry = response.data["data"]["results"][0]
    assert entry["actor_email"] == member.email
    assert "ip_address" not in entry
    assert "user_agent" not in entry
    assert "metadata" not in entry


@pytest.mark.django_db
def test_recent_audit_endpoint_skips_paginated_count_response():
    admin = User.objects.create_user(
        email="recent-admin@example.com",
        password="AdminPassword123!",
        role=UserRole.ADMIN,
    )
    create_audit_log(
        actor=admin,
        action=AuditAction.LOGIN,
        resource_type="Authentication",
        resource_id=admin.pk,
        description="Recent event.",
    )
    client = APIClient()
    token = str(RefreshToken.for_user(admin).access_token)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = client.get("/api/v1/admin/audit/?recent=1")

    assert response.status_code == 200
    assert isinstance(response.data["data"], list)
    assert len(response.data["data"]) == 1
