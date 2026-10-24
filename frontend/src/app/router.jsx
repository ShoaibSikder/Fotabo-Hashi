import { lazy, Suspense } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { useAuthCtx } from '../contexts/AuthContext.jsx';
import PublicLayout from '../components/layout/PublicLayout.jsx';
import DashboardLayout from '../components/layout/DashboardLayout.jsx';
import AdminLayout from '../components/layout/AdminLayout.jsx';
import RouteLoadingSkeleton from '../components/ui/RouteLoadingSkeleton.jsx';

const HomePage = lazy(() => import('../features/public/pages/HomePage.jsx'));
const LoginPage = lazy(() => import('../features/authentication/pages/LoginPage.jsx'));
const RegisterPage = lazy(() => import('../features/authentication/pages/RegisterPage.jsx'));
const ForgotPasswordPage = lazy(() => import('../features/authentication/pages/ForgotPasswordPage.jsx'));
const ResetPasswordPage = lazy(() => import('../features/authentication/pages/ResetPasswordPage.jsx'));
const DashboardPage = lazy(() => import('../features/dashboard/pages/DashboardPage.jsx'));
const DonorSearchPage = lazy(() => import('../features/donors/pages/DonorSearchPage.jsx'));
const RequestsPage = lazy(() => import('../features/blood-requests/pages/RequestsPage.jsx'));
const CreateRequestPage = lazy(() => import('../features/blood-requests/pages/CreateRequestPage.jsx'));
const RequestDetailsPage = lazy(() => import('../features/blood-requests/pages/RequestDetailsPage.jsx'));
const LeaderboardPage = lazy(() => import('../features/leaderboard/pages/LeaderboardPage.jsx'));
const ProfilePage = lazy(() => import('../features/profile/pages/ProfilePage.jsx'));
const SettingsPage = lazy(() => import('../features/settings/pages/SettingsPage.jsx'));
const AdminDashboardPage = lazy(() => import('../features/administration/pages/AdminDashboardPage.jsx'));
const AdminUsersPage = lazy(() => import('../features/administration/pages/AdminUsersPage.jsx'));
const DonationReviewsPage = lazy(() => import('../features/administration/pages/DonationReviewsPage.jsx'));
const AdminRequestsPage = lazy(() => import('../features/administration/pages/AdminRequestsPage.jsx'));
const AdminPublicContentPage = lazy(() => import('../features/administration/pages/AdminPublicContentPage.jsx'));
const AdministrationPage = lazy(() => import('../features/administration/pages/AdministrationPage.jsx'));

function RequireAuth() {
  const { user, loading } = useAuthCtx();
  if (loading) return <DashboardLayout loading />;
  if (!user) return <Navigate to="/login" replace />;
  if (user.role === 'ADMIN') return <Navigate to="/admin/dashboard" replace />;
  return <DashboardLayout />;
}

function RequireAdmin() {
  const { user, loading } = useAuthCtx();
  if (loading) return <AdminLayout loading />;
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== 'ADMIN') return <Navigate to="/dashboard" replace />;
  return <AdminLayout />;
}

export default function Router() {
  return <Suspense fallback={<RouteLoadingSkeleton />}><Routes>
    <Route element={<PublicLayout />}>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />
    </Route>
    <Route element={<RequireAuth />}>
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/donors" element={<DonorSearchPage />} />
      <Route path="/requests" element={<RequestsPage />} />
      <Route path="/requests/new" element={<CreateRequestPage />} />
      <Route path="/requests/:id" element={<RequestDetailsPage />} />
      <Route path="/leaderboard" element={<LeaderboardPage />} />
      <Route path="/profile" element={<ProfilePage />} />
      <Route path="/settings" element={<SettingsPage />} />
    </Route>
    <Route element={<RequireAdmin />}>
      <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />
      <Route path="/admin/dashboard" element={<AdminDashboardPage />} />
      <Route path="/admin/users" element={<AdminUsersPage />} />
      <Route path="/admin/donation-reviews" element={<DonationReviewsPage />} />
      <Route path="/admin/requests" element={<AdminRequestsPage />} />
      <Route path="/admin/public-content" element={<AdminPublicContentPage />} />
      <Route path="/admin/audit" element={<AdministrationPage />} />
    </Route>
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes></Suspense>;
}
