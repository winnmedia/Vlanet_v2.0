'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  Menu, 
  X, 
  Home, 
  FolderOpen, 
  Calendar, 
  MessageSquare, 
  User,
  Settings,
  LogOut,
  ChevronDown,
  ChevronRight,
  Video,
  Users,
  Bell,
  BarChart3,
  FileText,
  Cog,
  UserPlus
} from 'lucide-react';
import { Logo } from '@/components/ui/Logo';
import { cn } from '@/lib/cn';
import { useAuth } from '@/contexts/auth.context';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const navigationGroups = [
  {
    name: '대시보드',
    items: [
      { name: '홈', href: '/cmshome', icon: Home },
      { name: '통계', href: '/analytics', icon: BarChart3 },
    ]
  },
  {
    name: '프로젝트 관리',
    items: [
      { name: '모든 프로젝트', href: '/projects', icon: FolderOpen },
      { name: '진행중인 프로젝트', href: '/projects/active', icon: Video },
      { name: '영상 기획', href: '/video-planning', icon: FileText },
    ]
  },
  {
    name: '협업',
    items: [
      { name: '영상 피드백', href: '/video-feedback', icon: Video },
      { name: '피드백', href: '/feedbacks', icon: MessageSquare },
      { name: '팀 관리', href: '/teams', icon: Users },
      { name: '일정관리', href: '/calendar', icon: Calendar },
    ]
  }
];

const userNavigation = [
  { name: '마이페이지', href: '/mypage', icon: User },
  { name: '설정', href: '/settings', icon: Settings },
];

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [expandedGroups, setExpandedGroups] = useState<string[]>(['대시보드', '프로젝트 관리', '협업']);

  const handleLogout = async () => {
    await logout();
    window.location.href = '/login';
  };

  const toggleGroup = (groupName: string) => {
    setExpandedGroups(prev => 
      prev.includes(groupName) 
        ? prev.filter(name => name !== groupName)
        : [...prev, groupName]
    );
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* 모바일 사이드바 백드롭 */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* 사이드바 */}
      <aside className={cn(
        "fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 transform transition-transform lg:translate-x-0 lg:static lg:z-0",
        sidebarOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="flex h-full flex-col">
          {/* 로고 영역 */}
          <div className="flex h-16 items-center justify-between px-4 border-b border-gray-200">
            <Logo size="md" variant="default" />
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-2 rounded-md hover:bg-gray-100"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* 네비게이션 */}
          <nav className="flex-1 overflow-y-auto p-4">
            <div className="space-y-2">
              {navigationGroups.map((group) => {
                const isExpanded = expandedGroups.includes(group.name);
                return (
                  <div key={group.name} className="space-y-1">
                    <button
                      onClick={() => toggleGroup(group.name)}
                      className="flex w-full items-center justify-between px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
                    >
                      <span>{group.name}</span>
                      <ChevronRight className={cn(
                        "h-4 w-4 transition-transform",
                        isExpanded && "rotate-90"
                      )} />
                    </button>
                    
                    {isExpanded && (
                      <ul className="ml-2 space-y-1">
                        {group.items.map((item) => {
                          const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
                          return (
                            <li key={item.name}>
                              <Link
                                href={item.href}
                                className={cn(
                                  "flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-sm",
                                  isActive 
                                    ? "bg-blue-600 text-white shadow-sm" 
                                    : "text-gray-700 hover:bg-gray-100"
                                )}
                              >
                                <item.icon className="h-4 w-4" />
                                <span>{item.name}</span>
                              </Link>
                            </li>
                          );
                        })}
                      </ul>
                    )}
                  </div>
                );
              })}
            </div>

            <div className="mt-8 pt-8 border-t border-gray-200">
              <ul className="space-y-1">
                {userNavigation.map((item) => {
                  const isActive = pathname === item.href;
                  return (
                    <li key={item.name}>
                      <Link
                        href={item.href}
                        className={cn(
                          "flex items-center gap-3 px-3 py-2 rounded-lg transition-colors",
                          isActive 
                            ? "bg-brand-primary text-white" 
                            : "text-gray-700 hover:bg-gray-100"
                        )}
                      >
                        <item.icon className="h-5 w-5" />
                        <span className="font-medium">{item.name}</span>
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          </nav>

          {/* 사용자 정보 */}
          <div className="border-t border-gray-200 p-4">
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex w-full items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="h-8 w-8 rounded-full bg-brand-primary flex items-center justify-center text-white font-semibold">
                  {user?.name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                </div>
                <div className="flex-1 text-left">
                  <p className="text-sm font-medium text-gray-900">
                    {user?.name || user?.email || '사용자'}
                  </p>
                  <p className="text-xs text-gray-500">
                    {user?.email || ''}
                  </p>
                </div>
                <ChevronDown className={cn(
                  "h-4 w-4 text-gray-400 transition-transform",
                  userMenuOpen && "rotate-180"
                )} />
              </button>

              {userMenuOpen && (
                <div className="absolute bottom-full left-0 right-0 mb-2 bg-white border border-gray-200 rounded-lg shadow-lg">
                  <button
                    onClick={handleLogout}
                    className="flex w-full items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <LogOut className="h-4 w-4" />
                    로그아웃
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </aside>

      {/* 메인 컨텐츠 영역 */}
      <div className="flex-1 flex flex-col">
        {/* 모바일 헤더 */}
        <header className="lg:hidden flex h-16 items-center justify-between bg-white border-b border-gray-200 px-4">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 rounded-md hover:bg-gray-100"
          >
            <Menu className="h-5 w-5" />
          </button>
          <Logo size="sm" variant="default" showText={false} />
          <div className="w-9" /> {/* 균형을 위한 빈 공간 */}
        </header>

        {/* 페이지 컨텐츠 */}
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}

export default DashboardLayout;