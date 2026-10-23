from django.urls import path

from .audit_views import AuditLogAdminListView
from .donation_review_views import (
    AdminDonationCountReviewActionView,
    AdminDonationCountReviewListView,
)
from .donation_views import (
    AdminUserDonationDetailView,
    AdminUserDonationListCreateView,
)
from .system_views import (
    AdminBloodRequestDetailView,
    AdminBloodRequestListCreateView,
    AdminOverviewView,
    AdminUserDetailView,
    AdminUserListView,
)
from .views import (
    FoundingMemberAdminDetailView,
    FoundingMemberAdminListCreateView,
    NoticeAdminDetailView,
    NoticeAdminListCreateView,
)

app_name = "administration"

urlpatterns = [
    path("overview/", AdminOverviewView.as_view(), name="overview"),
    path(
        "donation-reviews/",
        AdminDonationCountReviewListView.as_view(),
        name="donation-count-review-list",
    ),
    path(
        "donation-reviews/<int:pk>/<str:action>/",
        AdminDonationCountReviewActionView.as_view(),
        name="donation-count-review-action",
    ),
    path("users/", AdminUserListView.as_view(), name="user-list"),
    path("users/<int:pk>/", AdminUserDetailView.as_view(), name="user-detail"),
    path(
        "users/<int:user_pk>/donations/",
        AdminUserDonationListCreateView.as_view(),
        name="user-donation-list-create",
    ),
    path(
        "users/<int:user_pk>/donations/<int:pk>/",
        AdminUserDonationDetailView.as_view(),
        name="user-donation-detail",
    ),
    path(
        "blood-requests/",
        AdminBloodRequestListCreateView.as_view(),
        name="blood-request-list-create",
    ),
    path(
        "blood-requests/<int:pk>/",
        AdminBloodRequestDetailView.as_view(),
        name="blood-request-detail",
    ),
    path("audit/", AuditLogAdminListView.as_view(), name="audit-list"),
    path(
        "public-content/members/",
        FoundingMemberAdminListCreateView.as_view(),
        name="public-member-list-create",
    ),
    path(
        "public-content/members/<int:pk>/",
        FoundingMemberAdminDetailView.as_view(),
        name="public-member-detail",
    ),
    path(
        "public-content/notices/",
        NoticeAdminListCreateView.as_view(),
        name="public-notice-list-create",
    ),
    path(
        "public-content/notices/<int:pk>/",
        NoticeAdminDetailView.as_view(),
        name="public-notice-detail",
    ),
]
