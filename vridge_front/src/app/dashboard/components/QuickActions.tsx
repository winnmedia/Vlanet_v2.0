'use client';

import React from 'react';
import Link from 'next/link';
import { 
  FolderOpen, 
  Calendar, 
  MessageSquare, 
  Users
} from 'lucide-react';

const QuickActions: React.FC = () => {
  return (
    <div className="bg-white rounded-lg border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900"> </h2>
      </div>
      <div className="p-6 space-y-3">
        <Link
          href="/projects/create"
          className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors min-h-[48px]"
        >
          <FolderOpen className="h-5 w-5 text-gray-600" />
          <span className="text-gray-700">  </span>
        </Link>
        <Link
          href="/calendar"
          className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors min-h-[48px]"
        >
          <Calendar className="h-5 w-5 text-gray-600" />
          <span className="text-gray-700"> </span>
        </Link>
        <Link
          href="/feedbacks"
          className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors min-h-[48px]"
        >
          <MessageSquare className="h-5 w-5 text-gray-600" />
          <span className="text-gray-700"> </span>
        </Link>
        <Link
          href="/mypage"
          className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors min-h-[48px]"
        >
          <Users className="h-5 w-5 text-gray-600" />
          <span className="text-gray-700"> </span>
        </Link>
      </div>
    </div>
  );
};

export default QuickActions;