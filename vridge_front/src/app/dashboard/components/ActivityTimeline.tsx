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
    { time: '10 ', action: ' "  "  .' },
    { time: '30 ', action: '  "  " .' },
    { time: '1 ', action: '"  "    .' },
    { time: '3 ', action: '  .' },
  ];

  const activityList = activities || defaultActivities;

  return (
    <div className="mt-6 bg-white rounded-lg border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900"> </h2>
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