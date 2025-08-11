'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { 
  Calendar, 
  Users, 
  MoreVertical, 
  Star, 
  Eye,
  Edit3,
  Trash2,
  Copy,
  ExternalLink,
  Play,
  Clock,
  CheckCircle,
  Archive
} from 'lucide-react';
import { cn } from '@/lib/cn';
import type { Project, ProjectStatus } from '@/types';
import { useProjectSelection } from '@/store/project.store';
import { formatDate } from 'date-fns';
import { ko } from 'date-fns/locale';

// ========================================
//  
// ========================================

export interface ProjectCardProps {
  project: Project;
  viewMode: 'grid' | 'list';
  showThumbnails?: boolean;
  compactMode?: boolean;
  onEdit?: (project: Project) => void;
  onDelete?: (project: Project) => void;
  onDuplicate?: (project: Project) => void;
  onToggleFavorite?: (project: Project) => void;
  onNavigate?: (project: Project) => void;
  className?: string;
}

// ========================================
//  
// ========================================

const statusConfig: Record<ProjectStatus, { 
  label: string; 
  color: string; 
  bgColor: string;
  icon: React.ComponentType<any>;
}> = {
  planning: {
    label: ' ',
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 border-blue-200',
    icon: Edit3,
  },
  production: {
    label: ' ',
    color: 'text-orange-600',
    bgColor: 'bg-orange-50 border-orange-200',
    icon: Play,
  },
  review: {
    label: ' ',
    color: 'text-purple-600',
    bgColor: 'bg-purple-50 border-purple-200',
    icon: Eye,
  },
  completed: {
    label: '',
    color: 'text-green-600',
    bgColor: 'bg-green-50 border-green-200',
    icon: CheckCircle,
  },
  archived: {
    label: '',
    color: 'text-gray-500',
    bgColor: 'bg-gray-50 border-gray-200',
    icon: Archive,
  },
};

const getProgressColor = (progress?: number) => {
  if (!progress) return 'bg-gray-200';
  if (progress < 30) return 'bg-red-500';
  if (progress < 70) return 'bg-yellow-500';
  return 'bg-green-500';
};

// ========================================
//  
// ========================================

export const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  viewMode,
  showThumbnails = true,
  compactMode = false,
  onEdit,
  onDelete,
  onDuplicate,
  onToggleFavorite,
  onNavigate,
  className,
}) => {
  const { isSelected, toggleSelection } = useProjectSelection();
  const [showDropdown, setShowDropdown] = React.useState(false);
  const dropdownRef = React.useRef<HTMLDivElement>(null);
  
  const selected = isSelected(project.id);
  const statusInfo = statusConfig[project.status];
  const StatusIcon = statusInfo.icon;

  //    
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  //   
  const handleCardClick = (e: React.MouseEvent) => {
    //    
    if (
      (e.target as Element).closest('.dropdown-trigger') ||
      (e.target as Element).closest('.project-action-button')
    ) {
      return;
    }

    onNavigate?.(project);
  };

  //   ()
  const handleSelectionToggle = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.stopPropagation();
    toggleSelection(project.id);
  };


  //  
  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    onEdit?.(project);
    setShowDropdown(false);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete?.(project);
    setShowDropdown(false);
  };

  const handleDuplicate = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDuplicate?.(project);
    setShowDropdown(false);
  };

  const handleToggleFavorite = (e: React.MouseEvent) => {
    e.stopPropagation();
    onToggleFavorite?.(project);
  };

  const handleExternalLink = (e: React.MouseEvent) => {
    e.stopPropagation();
    window.open(`/projects/${project.id}`, '_blank');
  };

  //  variants
  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.3, ease: 'easeOut' }
    },
    hover: { 
      y: -4,
      transition: { duration: 0.2, ease: 'easeOut' }
    }
  };

  //   
  if (viewMode === 'grid') {
    return (
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        whileHover="hover"
        className={cn(
          'group relative bg-white rounded-xl border border-gray-200 overflow-hidden cursor-pointer transition-all duration-200',
          'hover:border-gray-300 hover:shadow-lg',
          selected && 'ring-2 ring-blue-500 border-blue-500',
          className
        )}
        onClick={handleCardClick}
      >
        {/*   */}
        {showThumbnails && (
          <div className={cn(
            'relative overflow-hidden',
            compactMode ? 'h-32' : 'h-40'
          )}>
            {project.thumbnail ? (
              <img
                src={project.thumbnail}
                alt={project.title}
                className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
              />
            ) : (
              <div className="w-full h-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                <Play className="w-8 h-8 text-gray-400" />
              </div>
            )}
            
            {/*   */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              <div className="absolute bottom-3 left-3 right-3">
                {project.progress !== undefined && (
                  <div className="flex items-center gap-2 text-white text-sm">
                    <Clock className="w-3 h-3" />
                    <span>{project.progress}% </span>
                  </div>
                )}
              </div>
            </div>

            {/*   */}
            <div className="absolute top-3 left-3">
              <input
                type="checkbox"
                checked={selected}
                onChange={handleSelectionToggle}
                className="w-4 h-4 text-blue-600 bg-white border-gray-300 rounded focus:ring-blue-500"
                onClick={(e) => e.stopPropagation()}
              />
            </div>

            {/*   */}
            <button
              onClick={handleToggleFavorite}
              className="project-action-button absolute top-3 right-3 p-1 rounded-full bg-white/80 backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-200 hover:bg-white"
            >
              <Star className="w-4 h-4 text-gray-600" />
            </button>
          </div>
        )}

        {/*   */}
        <div className={cn('p-4', compactMode && 'p-3')}>
          {/*  */}
          <div className="flex items-start justify-between gap-2 mb-3">
            <div className="flex-1 min-w-0">
              <h3 className={cn(
                'font-semibold text-gray-900 line-clamp-1',
                compactMode ? 'text-sm' : 'text-base'
              )}>
                {project.title}
              </h3>
              {!compactMode && (
                <p className="text-sm text-gray-600 line-clamp-2 mt-1">
                  {project.description}
                </p>
              )}
            </div>
            
            {/*   */}
            <div className="relative" ref={dropdownRef}>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setShowDropdown(!showDropdown);
                }}
                className="dropdown-trigger p-1 rounded-full hover:bg-gray-100 transition-colors"
              >
                <MoreVertical className="w-4 h-4 text-gray-500" />
              </button>
              
              {showDropdown && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95, y: -10 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: -10 }}
                  className="absolute right-0 top-full mt-1 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-50"
                >
                  <div className="py-1">
                    <button
                      onClick={handleEdit}
                      className="flex items-center gap-3 w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    >
                      <Edit3 className="w-4 h-4" />
                      
                    </button>
                    <button
                      onClick={handleDuplicate}
                      className="flex items-center gap-3 w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    >
                      <Copy className="w-4 h-4" />
                      
                    </button>
                    <button
                      onClick={handleExternalLink}
                      className="flex items-center gap-3 w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    >
                      <ExternalLink className="w-4 h-4" />
                        
                    </button>
                    <hr className="my-1" />
                    <button
                      onClick={handleDelete}
                      className="flex items-center gap-3 w-full px-3 py-2 text-sm text-red-600 hover:bg-red-50"
                    >
                      <Trash2 className="w-4 h-4" />
                      
                    </button>
                  </div>
                </motion.div>
              )}
            </div>
          </div>

          {/*    */}
          <div className="flex items-center gap-2 mb-3">
            <div className={cn(
              'inline-flex items-center gap-1 px-2 py-1 rounded-full border text-xs font-medium',
              statusInfo.bgColor,
              statusInfo.color
            )}>
              <StatusIcon className="w-3 h-3" />
              {statusInfo.label}
            </div>
            
            {project.progress !== undefined && (
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                    <div
                      className={cn(
                        'h-1.5 rounded-full transition-all duration-300',
                        getProgressColor(project.progress)
                      )}
                      style={{ width: `${project.progress}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-600 font-medium">
                    {project.progress}%
                  </span>
                </div>
              </div>
            )}
          </div>

          {/*   */}
          <div className="flex items-center justify-between text-xs text-gray-500">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1">
                <Users className="w-3 h-3" />
                <span>{project.members_count || 0}</span>
              </div>
              <div className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                <span>
                  {formatDate(new Date(project.updated_at), 'MM/dd', { locale: ko })}
                </span>
              </div>
            </div>
            
            <div className="text-xs text-gray-400">
              {project.owner.nickname}
            </div>
          </div>

          {/*  () */}
          {project.tags && project.tags.length > 0 && !compactMode && (
            <div className="flex flex-wrap gap-1 mt-3">
              {project.tags.slice(0, 3).map((tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md"
                >
                  {tag}
                </span>
              ))}
              {project.tags.length > 3 && (
                <span className="text-xs text-gray-500">
                  +{project.tags.length - 3}
                </span>
              )}
            </div>
          )}
        </div>
      </motion.div>
    );
  }

  //   
  return (
    <motion.div
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      className={cn(
        'group flex items-center gap-4 p-4 bg-white rounded-lg border border-gray-200 cursor-pointer transition-all duration-200',
        'hover:border-gray-300 hover:shadow-md',
        selected && 'ring-2 ring-blue-500 border-blue-500',
        className
      )}
      onClick={handleCardClick}
    >
      {/*   */}
      <input
        type="checkbox"
        checked={selected}
        onChange={handleSelectionToggle}
        className="w-4 h-4 text-blue-600 bg-white border-gray-300 rounded focus:ring-blue-500"
        onClick={(e) => e.stopPropagation()}
      />

      {/*  */}
      {showThumbnails && (
        <div className="flex-shrink-0 w-16 h-12 bg-gray-100 rounded-lg overflow-hidden">
          {project.thumbnail ? (
            <img
              src={project.thumbnail}
              alt={project.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
              <Play className="w-4 h-4 text-gray-400" />
            </div>
          )}
        </div>
      )}

      {/*   */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <h3 className="font-semibold text-gray-900 line-clamp-1">
            {project.title}
          </h3>
          <div className={cn(
            'inline-flex items-center gap-1 px-2 py-0.5 rounded-full border text-xs font-medium',
            statusInfo.bgColor,
            statusInfo.color
          )}>
            <StatusIcon className="w-3 h-3" />
            {statusInfo.label}
          </div>
        </div>
        
        {!compactMode && (
          <p className="text-sm text-gray-600 line-clamp-1 mb-2">
            {project.description}
          </p>
        )}
        
        <div className="flex items-center gap-4 text-xs text-gray-500">
          <div className="flex items-center gap-1">
            <Users className="w-3 h-3" />
            <span>{project.members_count || 0}</span>
          </div>
          <div className="flex items-center gap-1">
            <Calendar className="w-3 h-3" />
            <span>
              {formatDate(new Date(project.updated_at), 'yyyy/MM/dd', { locale: ko })}
            </span>
          </div>
          <span>{project.owner.nickname}</span>
        </div>
      </div>

      {/*  */}
      {project.progress !== undefined && (
        <div className="flex-shrink-0 w-24">
          <div className="flex items-center gap-2">
            <div className="flex-1 bg-gray-200 rounded-full h-2">
              <div
                className={cn(
                  'h-2 rounded-full transition-all duration-300',
                  getProgressColor(project.progress)
                )}
                style={{ width: `${project.progress}%` }}
              />
            </div>
            <span className="text-xs text-gray-600 font-medium w-8 text-right">
              {project.progress}%
            </span>
          </div>
        </div>
      )}

      {/*   */}
      <div className="flex-shrink-0 flex items-center gap-1">
        <button
          onClick={handleToggleFavorite}
          className="project-action-button p-2 rounded-full hover:bg-gray-100 transition-colors"
        >
          <Star className="w-4 h-4 text-gray-400 hover:text-yellow-500" />
        </button>
        
        {/*   */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowDropdown(!showDropdown);
            }}
            className="dropdown-trigger p-2 rounded-full hover:bg-gray-100 transition-colors"
          >
            <MoreVertical className="w-4 h-4 text-gray-500" />
          </button>
          
          {showDropdown && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -10 }}
              className="absolute right-0 top-full mt-1 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-50"
            >
              <div className="py-1">
                <button
                  onClick={handleEdit}
                  className="flex items-center gap-3 w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  <Edit3 className="w-4 h-4" />
                  
                </button>
                <button
                  onClick={handleDuplicate}
                  className="flex items-center gap-3 w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  <Copy className="w-4 h-4" />
                  
                </button>
                <button
                  onClick={handleExternalLink}
                  className="flex items-center gap-3 w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  <ExternalLink className="w-4 h-4" />
                    
                </button>
                <hr className="my-1" />
                <button
                  onClick={handleDelete}
                  className="flex items-center gap-3 w-full px-3 py-2 text-sm text-red-600 hover:bg-red-50"
                >
                  <Trash2 className="w-4 h-4" />
                  
                </button>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </motion.div>
  );
};