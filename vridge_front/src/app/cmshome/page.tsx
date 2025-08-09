'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/auth.store';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { useToast } from '@/contexts/toast.context';

export default function CmsHomePage() {
  const router = useRouter();
  const { success } = useToast();
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);
  const user = useAuthStore(state => state.user);
  const logout = useAuthStore(state => state.logout);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p>로딩 중...</p>
        </div>
      </div>
    );
  }

  const handleLogout = async () => {
    await logout();
    success('로그아웃되었습니다.');
    router.push('/login');
  };

  return (
    <DashboardLayout>
      <div className="p-4 md:p-6">
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-6 gap-4">
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900">
            대시보드
          </h1>
          <div className="flex items-center space-x-4">
            <span className="text-gray-700">
              {user?.nickname || user?.email}님 환영합니다
            </span>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              로그아웃
            </button>
          </div>
        </div>
          <div className="max-w-7xl mx-auto">
            {/* 통계 카드 */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium text-gray-500">전체 프로젝트</h3>
                  <span className="text-2xl">📁</span>
                </div>
                <p className="text-3xl font-bold text-gray-900">5</p>
                <p className="text-xs text-gray-600 mt-1">활성 프로젝트</p>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium text-gray-500">진행 중</h3>
                  <span className="text-2xl">⚡</span>
                </div>
                <p className="text-3xl font-bold text-blue-600">3</p>
                <p className="text-xs text-gray-600 mt-1">작업 중인 프로젝트</p>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium text-gray-500">새 피드백</h3>
                  <span className="text-2xl">💬</span>
                </div>
                <p className="text-3xl font-bold text-green-600">7</p>
                <p className="text-xs text-gray-600 mt-1">확인 필요</p>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-medium text-gray-500">팀 멤버</h3>
                  <span className="text-2xl">👥</span>
                </div>
                <p className="text-3xl font-bold text-purple-600">12</p>
                <p className="text-xs text-gray-600 mt-1">활성 멤버</p>
              </div>
            </div>

            {/* 프로젝트 진행 현황 위젯 */}
            <div className="bg-white rounded-lg shadow p-6 mb-8">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                📊 프로젝트 진행 현황
              </h2>
              <div className="space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-gray-50 rounded-lg gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                      🎬
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">광고 캠페인 A</h3>
                      <p className="text-sm text-gray-500">영상 제작</p>
                    </div>
                  </div>
                  <div className="text-left sm:text-right">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="w-24 sm:w-20 bg-gray-200 rounded-full h-2">
                        <div className="bg-blue-600 h-2 rounded-full" style={{width: '75%'}}></div>
                      </div>
                      <span className="text-sm font-medium text-blue-600">75%</span>
                    </div>
                    <p className="text-xs text-gray-500">편집 단계</p>
                  </div>
                </div>
                
                <div className="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-gray-50 rounded-lg gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                      📺
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">브랜드 홍보 영상</h3>
                      <p className="text-sm text-gray-500">기획 단계</p>
                    </div>
                  </div>
                  <div className="text-left sm:text-right">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="w-24 sm:w-20 bg-gray-200 rounded-full h-2">
                        <div className="bg-green-600 h-2 rounded-full" style={{width: '30%'}}></div>
                      </div>
                      <span className="text-sm font-medium text-green-600">30%</span>
                    </div>
                    <p className="text-xs text-gray-500">기획 검토 중</p>
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-gray-50 rounded-lg gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                      🎥
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">제품 소개 영상</h3>
                      <p className="text-sm text-gray-500">촬영 완료</p>
                    </div>
                  </div>
                  <div className="text-left sm:text-right">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="w-24 sm:w-20 bg-gray-200 rounded-full h-2">
                        <div className="bg-purple-600 h-2 rounded-full" style={{width: '90%'}}></div>
                      </div>
                      <span className="text-sm font-medium text-purple-600">90%</span>
                    </div>
                    <p className="text-xs text-gray-500">최종 검토</p>
                  </div>
                </div>
              </div>
            </div>

            {/* 알림 및 초대 현황 */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-6 mb-8">
              {/* 피드백/코멘트 알림 */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <div className="relative">
                    💬
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">3</span>
                  </div>
                  새 피드백
                </h2>
                <div className="space-y-3">
                  <div className="p-3 bg-red-50 border-l-4 border-red-500 rounded">
                    <div className="flex justify-between items-start mb-1">
                      <p className="text-sm font-medium text-gray-900">김대리님</p>
                      <span className="text-xs text-gray-500">10분 전</span>
                    </div>
                    <p className="text-sm text-gray-700">"로고 크기를 조금 더 키워주세요"</p>
                    <p className="text-xs text-gray-500 mt-1">광고 캠페인 A</p>
                  </div>
                  
                  <div className="p-3 bg-blue-50 border-l-4 border-blue-500 rounded">
                    <div className="flex justify-between items-start mb-1">
                      <p className="text-sm font-medium text-gray-900">박과장님</p>
                      <span className="text-xs text-gray-500">1시간 전</span>
                    </div>
                    <p className="text-sm text-gray-700">"음향 효과가 좋네요!"</p>
                    <p className="text-xs text-gray-500 mt-1">제품 소개 영상</p>
                  </div>
                  
                  <div className="p-3 bg-green-50 border-l-4 border-green-500 rounded">
                    <div className="flex justify-between items-start mb-1">
                      <p className="text-sm font-medium text-gray-900">이부장님</p>
                      <span className="text-xs text-gray-500">3시간 전</span>
                    </div>
                    <p className="text-sm text-gray-700">"컨셉이 잘 잡혔습니다"</p>
                    <p className="text-xs text-gray-500 mt-1">브랜드 홍보 영상</p>
                  </div>
                </div>
                <button className="w-full mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm">
                  모든 피드백 보기
                </button>
              </div>

              {/* 초대 현황 위젯 */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  👥 팀 초대 현황
                </h2>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-gray-900">홍길동</p>
                      <p className="text-xs text-gray-500">hong@example.com</p>
                    </div>
                    <span className="px-2 py-1 bg-yellow-200 text-yellow-800 text-xs rounded-full">
                      대기 중
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-gray-900">김영희</p>
                      <p className="text-xs text-gray-500">kim@example.com</p>
                    </div>
                    <span className="px-2 py-1 bg-green-200 text-green-800 text-xs rounded-full">
                      수락됨
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-gray-900">박철수</p>
                      <p className="text-xs text-gray-500">park@example.com</p>
                    </div>
                    <span className="px-2 py-1 bg-blue-200 text-blue-800 text-xs rounded-full">
                      활성
                    </span>
                  </div>
                </div>
                <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">전체 멤버:</span>
                    <span className="font-medium">12명</span>
                  </div>
                  <div className="flex justify-between text-sm mt-1">
                    <span className="text-gray-600">활성 멤버:</span>
                    <span className="font-medium text-green-600">10명</span>
                  </div>
                </div>
              </div>

              {/* 빠른 작업 카드 */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold mb-4">빠른 작업</h2>
                <div className="space-y-3">
                  <button
                    onClick={() => router.push('/projects/create')}
                    className="w-full px-4 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all text-sm"
                  >
                    🎬 새 프로젝트 만들기
                  </button>
                  <button
                    onClick={() => router.push('/videoplanning')}
                    className="w-full px-4 py-3 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-lg hover:from-purple-600 hover:to-purple-700 transition-all text-sm"
                  >
                    📝 영상 기획 시작하기
                  </button>
                  <button
                    onClick={() => router.push('/feedback')}
                    className="w-full px-4 py-3 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg hover:from-green-600 hover:to-green-700 transition-all text-sm"
                  >
                    💬 피드백 확인하기
                  </button>
                  <button
                    onClick={() => router.push('/teams/invite')}
                    className="w-full px-4 py-3 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-lg hover:from-orange-600 hover:to-orange-700 transition-all text-sm"
                  >
                    👥 팀원 초대하기
                  </button>
                </div>
              </div>
            </div>

            {/* 최근 활동 */}
            <div className="grid grid-cols-1 gap-6">
              {/* 최근 활동 */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  🕐 최근 활동
                </h2>
                <div className="space-y-4">
                  <div className="flex items-start space-x-3 p-3 border-l-4 border-blue-500 bg-blue-50 rounded">
                    <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      🎬
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">새 프로젝트 '광고 캠페인 A' 생성</p>
                      <p className="text-xs text-gray-500">2시간 전 • 김대리님</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3 p-3 border-l-4 border-green-500 bg-green-50 rounded">
                    <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                      ✅
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">피드백 3건 처리 완료</p>
                      <p className="text-xs text-gray-500">5시간 전 • 편집팀</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3 p-3 border-l-4 border-purple-500 bg-purple-50 rounded">
                    <div className="flex-shrink-0 w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                      👥
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">팀원 2명 새로 합류</p>
                      <p className="text-xs text-gray-500">어제 • HR팀</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3 p-3 border-l-4 border-orange-500 bg-orange-50 rounded">
                    <div className="flex-shrink-0 w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
                      📹
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">제품 소개 영상 촬영 완료</p>
                      <p className="text-xs text-gray-500">2일 전 • 촬영팀</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3 p-3 border-l-4 border-indigo-500 bg-indigo-50 rounded">
                    <div className="flex-shrink-0 w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
                      📊
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">월간 리포트 업데이트</p>
                      <p className="text-xs text-gray-500">3일 전 • 관리팀</p>
                    </div>
                  </div>
                </div>
                <button className="w-full mt-4 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm">
                  전체 활동 보기
                </button>
              </div>
            </div>
          </div>
      </div>
    </DashboardLayout>
  );
}