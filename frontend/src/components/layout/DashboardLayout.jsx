
import { Outlet } from 'react-router-dom';
import { Suspense } from 'react';
import AppHeader from './AppHeader.jsx';
import Sidebar from './Sidebar.jsx';
import MobileNavigation from './MobileNavigation.jsx';
import PublicFooter from './PublicFooter.jsx';
import { DashboardContentSkeleton } from '../ui/RouteLoadingSkeleton.jsx';

export default function DashboardLayout({ loading = false }) {
  return <div className="flex min-h-screen flex-col bg-[#f5f5f7]"><AppHeader /><div className="mx-auto flex w-full max-w-[1600px] flex-1 items-start gap-6 px-4 py-5 sm:px-6 sm:py-7 lg:gap-8 lg:px-8"><Sidebar /><main className="min-w-0 flex-1 pb-24 xl:pb-8">{loading ? <DashboardContentSkeleton /> : <Suspense fallback={<DashboardContentSkeleton />}><Outlet /></Suspense>}</main></div><div className="pb-24 xl:pb-0"><PublicFooter /></div><MobileNavigation /></div>;
}
