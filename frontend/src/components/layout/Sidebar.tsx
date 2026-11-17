import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  Search,
  Clock,
  Settings,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useState } from 'react';

const sidebarLinks = [
  { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { label: 'My Resume', href: '/resume', icon: FileText },
  { label: 'Analyze Job', href: '/analyze', icon: Search },
  { label: 'History', href: '/history', icon: Clock },
  { label: 'Settings', href: '/settings', icon: Settings },
];

export default function Sidebar() {
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={cn(
        'hidden lg:flex flex-col border-r border-slate-200 bg-white transition-all duration-300 h-[calc(100vh-64px)] sticky top-16',
        collapsed ? 'w-16' : 'w-60'
      )}
    >
      <div className="flex-1 py-4">
        <nav className="space-y-1 px-2">
          {sidebarLinks.map((link) => {
            const isActive =
              location.pathname === link.href ||
              (link.href !== '/dashboard' && location.pathname.startsWith(link.href));
            const Icon = link.icon;

            return (
              <Link
                key={link.href}
                to={link.href}
                title={collapsed ? link.label : undefined}
                className={cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group relative',
                  isActive
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                )}
              >
                {isActive && (
                  <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-primary-600 rounded-r" />
                )}
                <Icon className={cn('w-5 h-5 flex-shrink-0', isActive ? 'text-primary-600' : 'text-slate-400 group-hover:text-slate-600')} />
                {!collapsed && <span>{link.label}</span>}
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="border-t border-slate-200 p-2">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex items-center justify-center w-full p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-50 transition-colors"
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>
    </aside>
  );
}
