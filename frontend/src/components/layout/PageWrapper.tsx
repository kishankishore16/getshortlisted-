import { ReactNode } from 'react';
import Navbar from './Navbar';
import Sidebar from './Sidebar';

interface PageWrapperProps {
  children: ReactNode;
  showSidebar?: boolean;
}

export function PageWrapper({ children, showSidebar = true }: PageWrapperProps) {
  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <div className="flex">
        {showSidebar && <Sidebar />}
        <main className="flex-1 min-h-[calc(100vh-64px)]">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
export default PageWrapper;
