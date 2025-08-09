'use client';

import React from 'react';
import { Clock } from 'lucide-react';

interface Activity {
  time: string;
  action: string;
}

interface ActivityTimelineProps {
  activities?: Activity[];
}

const ActivityTimeline: React.FC<ActivityTimelineProps> = ({ activities }) => {
  const defaultActivities = [
    { time: '10분 전', action: '김영희님이 "브랜드 홍보 영상"에 피드백을 남겼습니다.' },
    { time: '30분 전', action: '새 프로젝트 "유튜브 썸네일 디자인"이 생성되었습니다.' },
    { time: '1시간 전', action: '"제품 소개 애니메이션" 프로젝트가 피드백 단계로 이동했습니다.' },
    { time: '3시간 전', action: '박철수님이 팀에 합류했습니다.' },
  ];

  const activityList = activities || defaultActivities;

  return (
    <div className="mt-6 bg-white rounded-lg border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">최근 활동</h2>
      </div>
      <div className="p-6">
        <div className="space-y-4">
          {activityList.map((activity, index) => (
            <div key={index} className="flex items-start gap-3">
              <Clock className="h-4 w-4 text-gray-400 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm text-gray-700">{activity.action}</p>
                <p className="text-xs text-gray-500 mt-1">{activity.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ActivityTimeline;