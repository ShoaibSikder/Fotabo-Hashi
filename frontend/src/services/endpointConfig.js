
const DEFAULT_DEV_API_ROOT = 'http://127.0.0.1:8000/api/v1';
const configuredApiRoot = import.meta.env.VITE_API_BASE_URL?.trim();
const API_ROOT = (configuredApiRoot || (import.meta.env.DEV ? DEFAULT_DEV_API_ROOT : '')).replace(/\/+$/, '');

if (!API_ROOT) {
  throw new Error('VITE_API_BASE_URL must be set for production builds.');
}

if (import.meta.env.PROD && !API_ROOT.startsWith('https://')) {
  throw new Error('VITE_API_BASE_URL must use HTTPS in production.');
}

export const API_ENDPOINTS = {
  csrf: `${API_ROOT}/auth/csrf/`,
  login: `${API_ROOT}/auth/login/`,
  register: `${API_ROOT}/auth/register/`,
  refresh: `${API_ROOT}/auth/refresh/`,
  logout: `${API_ROOT}/auth/logout/`,
  me: `${API_ROOT}/auth/me/`,
  passwordReset: `${API_ROOT}/auth/password-reset/`,
  passwordResetConfirm: `${API_ROOT}/auth/password-reset/confirm/`,
  passwordChange: `${API_ROOT}/auth/password-change/`,
  profile: `${API_ROOT}/profile/me/`,
  donors: `${API_ROOT}/donors/`,
  requests: `${API_ROOT}/blood-requests/`,
  myRequestSummary: `${API_ROOT}/blood-requests/mine/summary/`,
  requestDetail: (id) => `${API_ROOT}/blood-requests/${id}/`,
  requestFulfill: (id) => `${API_ROOT}/blood-requests/${id}/fulfill/`,
  requestCancel: (id) => `${API_ROOT}/blood-requests/${id}/cancel/`,
  leaderboard: `${API_ROOT}/leaderboard/`,
  organization: `${API_ROOT}/content/organization/`,
  notices: `${API_ROOT}/content/notices/`,
  activeMembers: `${API_ROOT}/content/active-members/`,
  adminOverview: `${API_ROOT}/admin/overview/`,
  adminDonationReviews: `${API_ROOT}/admin/donation-reviews/`,
  adminDonationCountReviewAction: (id, action) => `${API_ROOT}/admin/donation-reviews/${id}/${action}/`,
  adminUsers: `${API_ROOT}/admin/users/`,
  adminUserDetail: (id) => `${API_ROOT}/admin/users/${id}/`,
  adminUserDonations: (id) => `${API_ROOT}/admin/users/${id}/donations/`,
  adminUserDonationDetail: (userId, donationId) => `${API_ROOT}/admin/users/${userId}/donations/${donationId}/`,
  adminBloodRequests: `${API_ROOT}/admin/blood-requests/`,
  adminBloodRequestDetail: (id) => `${API_ROOT}/admin/blood-requests/${id}/`,
  adminAudit: `${API_ROOT}/admin/audit/`,
  adminMembers: `${API_ROOT}/admin/public-content/members/`,
  adminMemberDetail: (id) => `${API_ROOT}/admin/public-content/members/${id}/`,
  adminNotices: `${API_ROOT}/admin/public-content/notices/`,
  adminNoticeDetail: (id) => `${API_ROOT}/admin/public-content/notices/${id}/`,
  notifications: `${API_ROOT}/notifications/`,
  notificationReadAll: `${API_ROOT}/notifications/read-all/`,
  notificationRead: (id) => `${API_ROOT}/notifications/${id}/read/`,
  health: `${API_ROOT}/health/ready/`,
  apiDocs: `${API_ROOT}/docs/`,
};
