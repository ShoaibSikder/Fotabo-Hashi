
import { Suspense } from 'react';
import { Outlet } from 'react-router-dom';
import { PublicContentSkeleton } from '../ui/RouteLoadingSkeleton.jsx';
import PublicHeader from './PublicHeader.jsx';
import PublicFooter from './PublicFooter.jsx';

export default function PublicLayout() {
  return <div className="flex min-h-screen flex-col"><PublicHeader /><main className="flex-1"><Suspense fallback={<div role="status" aria-label="Loading page" aria-live="polite"><PublicContentSkeleton /></div>}><Outlet /></Suspense></main><PublicFooter /></div>;
}
