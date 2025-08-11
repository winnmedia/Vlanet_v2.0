'use client';

import React from 'react';
import { 
  FolderOpen, 
  MessageSquare, 
  TrendingUp,
  Film,
  CheckCircle2
} from 'lucide-react';
import { cn } from '@/lib/cn';

//   
interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ElementType;
  change?: {
    value: number;
    trend: 'up' | 'down';
  };
  color?: 'blue' | 'green' | 'purple' | 'orange';
}

const StatCard: React.FC<StatCardProps> = ({ 
  title, 
  value, 
  icon: Icon, 
  change,
  color = 'blue' 
}) => {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
    orange: 'bg-orange-100 text-orange-600',
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className={cn(
          "p-3 rounded-lg",
          colorClasses[color]
        )}>
          <Icon className="h-6 w-6" />
        </div>
        {change && (
          <div className={cn(
            "flex items-center gap-1 text-sm font-medium",
            change.trend === 'up' ? 'text-green-600' : 'text-red-600'
          )}>
            <TrendingUp className={cn(
              "h-4 w-4",
              change.trend === 'down' && 'rotate-180'
            )} />
            {Math.abs(change.value)}%
          </div>
        )}
      </div>
      <div>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <p className="text-sm text-gray-500 mt-1">{title}</p>
      </div>
    </div>
  );
};

interface DashboardStatsProps {
  stats: {
    totalProjects: number;
    activeProjects: number;
    completedTasks: number;
    pendingFeedbacks: number;
  };
}

const DashboardStats: React.FC<DashboardStatsProps> = ({ stats }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <StatCard
        title=" "
        value={stats.totalProjects}
        icon={FolderOpen}
        color="blue"
        change={{ value: 12, trend: 'up' }}
      />
      <StatCard
        title=" "
        value={stats.activeProjects}
        icon={Film}
        color="green"
      />
      <StatCard
        title=" "
        value={stats.completedTasks}
        icon={CheckCircle2}
        color="purple"
        change={{ value: 8, trend: 'up' }}
      />
      <StatCard
        title=" "
        value={stats.pendingFeedbacks}
        icon={MessageSquare}
        color="orange"
        change={{ value: 5, trend: 'down' }}
      />
    </div>
  );
};

export default DashboardStats;