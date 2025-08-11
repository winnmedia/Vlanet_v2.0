'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, 
  User, 
  Tag,
  Filter as FilterIcon,
  RotateCcw,
  ChevronDown,
  Check,
  Calendar as CalendarIcon,
  Hash
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { cn } from '@/lib/cn';
import { useProjectFilters } from '@/store/project.store';
import type { ProjectStatus, ProjectFilters as ProjectFiltersType } from '@/types';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';

// ========================================
//  
// ========================================

export interface ProjectFiltersProps {
  className?: string;
  onClose?: () => void;
  showCloseButton?: boolean;
}

interface FilterOptionProps<T> {
  value: T;
  label: string;
  count?: number;
  color?: string;
}

// ========================================
//  
// ========================================

const statusFilters: FilterOptionProps<ProjectStatus>[] = [
  { 
    value: 'planning', 
    label: ' ', 
    color: 'bg-blue-100 text-blue-800 border-blue-200',
    count: 0 
  },
  { 
    value: 'production', 
    label: ' ', 
    color: 'bg-orange-100 text-orange-800 border-orange-200',
    count: 0 
  },
  { 
    value: 'review', 
    label: ' ', 
    color: 'bg-purple-100 text-purple-800 border-purple-200',
    count: 0 
  },
  { 
    value: 'completed', 
    label: '', 
    color: 'bg-green-100 text-green-800 border-green-200',
    count: 0 
  },
];

const ownerFilters: FilterOptionProps<number>[] = [
  { value: 1, label: ' ', count: 0 },
  { value: 2, label: ' ', count: 0 },
];

// ========================================
//  
// ========================================

interface FilterSectionProps {
  title: string;
  icon: React.ComponentType<any>;
  children: React.ReactNode;
  collapsible?: boolean;
}

const FilterSection: React.FC<FilterSectionProps> = ({
  title,
  icon: Icon,
  children,
  collapsible = false,
}) => {
  const [isExpanded, setIsExpanded] = React.useState(true);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon className="w-4 h-4 text-gray-500" />
          <h3 className="text-sm font-medium text-gray-900">{title}</h3>
        </div>
        
        {collapsible && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 hover:bg-gray-100 rounded transition-colors"
          >
            <ChevronDown 
              className={cn(
                'w-4 h-4 text-gray-400 transition-transform',
                !isExpanded && 'transform rotate-180'
              )}
            />
          </button>
        )}
      </div>
      
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

interface CheckboxFilterProps<T> {
  options: FilterOptionProps<T>[];
  selectedValues: T[];
  onChange: (values: T[]) => void;
  multiple?: boolean;
}

const CheckboxFilter = <T extends string | number>({
  options,
  selectedValues,
  onChange,
  multiple = true,
}: CheckboxFilterProps<T>) => {
  const handleToggle = (value: T) => {
    if (multiple) {
      const newValues = selectedValues.includes(value)
        ? selectedValues.filter(v => v !== value)
        : [...selectedValues, value];
      onChange(newValues);
    } else {
      onChange(selectedValues.includes(value) ? [] : [value]);
    }
  };

  return (
    <div className="space-y-2">
      {options.map((option) => {
        const isSelected = selectedValues.includes(option.value);
        
        return (
          <label
            key={option.value}
            className={cn(
              'flex items-center gap-3 p-2 rounded-lg cursor-pointer transition-colors',
              'hover:bg-gray-50',
              isSelected && 'bg-blue-50'
            )}
          >
            <div className="relative">
              <input
                type="checkbox"
                checked={isSelected}
                onChange={() => handleToggle(option.value)}
                className="sr-only"
              />
              <div className={cn(
                'w-4 h-4 border rounded transition-colors',
                isSelected 
                  ? 'bg-blue-600 border-blue-600' 
                  : 'border-gray-300 bg-white'
              )}>
                {isSelected && (
                  <Check className="w-3 h-3 text-white absolute top-0.5 left-0.5" />
                )}
              </div>
            </div>
            
            <div className="flex-1 flex items-center justify-between">
              <span className={cn(
                'text-sm',
                isSelected ? 'text-blue-900 font-medium' : 'text-gray-700'
              )}>
                {option.label}
              </span>
              
              {option.count !== undefined && (
                <span className="text-xs text-gray-500">
                  {option.count}
                </span>
              )}
            </div>
          </label>
        );
      })}
    </div>
  );
};

interface DateRangeFilterProps {
  startDate?: string;
  endDate?: string;
  onChange: (dateRange: { start: string; end: string } | undefined) => void;
}

const DateRangeFilter: React.FC<DateRangeFilterProps> = ({
  startDate,
  endDate,
  onChange,
}) => {
  const [localStart, setLocalStart] = React.useState(startDate || '');
  const [localEnd, setLocalEnd] = React.useState(endDate || '');

  const handleApply = () => {
    if (localStart && localEnd) {
      onChange({ start: localStart, end: localEnd });
    } else {
      onChange(undefined);
    }
  };

  const handleClear = () => {
    setLocalStart('');
    setLocalEnd('');
    onChange(undefined);
  };

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="block text-xs text-gray-500 mb-1"></label>
          <Input
            type="date"
            value={localStart}
            onChange={(e) => setLocalStart(e.target.value)}
            className="text-sm"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1"></label>
          <Input
            type="date"
            value={localEnd}
            onChange={(e) => setLocalEnd(e.target.value)}
            className="text-sm"
          />
        </div>
      </div>
      
      <div className="flex gap-2">
        <Button
          size="sm"
          variant="outline"
          onClick={handleClear}
          className="flex-1 text-xs"
        >
          
        </Button>
        <Button
          size="sm"
          onClick={handleApply}
          className="flex-1 text-xs"
          disabled={!localStart || !localEnd}
        >
          
        </Button>
      </div>
    </div>
  );
};

interface TagFilterProps {
  selectedTags: string[];
  onChange: (tags: string[]) => void;
}

const TagFilter: React.FC<TagFilterProps> = ({
  selectedTags,
  onChange,
}) => {
  const [inputValue, setInputValue] = React.useState('');
  const [suggestions] = React.useState([
    '', '', '', '', '', '', 
    '', '', '', ''
  ]);

  const filteredSuggestions = suggestions.filter(tag => 
    tag.toLowerCase().includes(inputValue.toLowerCase()) &&
    !selectedTags.includes(tag)
  );

  const handleAddTag = (tag: string) => {
    if (!selectedTags.includes(tag)) {
      onChange([...selectedTags, tag]);
    }
    setInputValue('');
  };

  const handleRemoveTag = (tag: string) => {
    onChange(selectedTags.filter(t => t !== tag));
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && inputValue.trim()) {
      e.preventDefault();
      handleAddTag(inputValue.trim());
    }
  };

  return (
    <div className="space-y-3">
      <div className="relative">
        <Input
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder=" ..."
          className="text-sm"
        />
        
        {inputValue && filteredSuggestions.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-40 overflow-y-auto">
            {filteredSuggestions.slice(0, 5).map(tag => (
              <button
                key={tag}
                onClick={() => handleAddTag(tag)}
                className="w-full text-left px-3 py-2 hover:bg-gray-50 text-sm"
              >
                {tag}
              </button>
            ))}
          </div>
        )}
      </div>

      {/*   */}
      {selectedTags.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {selectedTags.map(tag => (
            <span
              key={tag}
              className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs"
            >
              <Hash className="w-3 h-3" />
              {tag}
              <button
                onClick={() => handleRemoveTag(tag)}
                className="ml-1 hover:text-blue-600"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
        </div>
      )}

      {/*   */}
      {selectedTags.length === 0 && (
        <div>
          <p className="text-xs text-gray-500 mb-2"> </p>
          <div className="flex flex-wrap gap-1">
            {suggestions.slice(0, 6).map(tag => (
              <button
                key={tag}
                onClick={() => handleAddTag(tag)}
                className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs hover:bg-gray-200 transition-colors"
              >
                <Hash className="w-3 h-3" />
                {tag}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

interface ActiveFiltersProps {
  filters: ProjectFiltersType;
  onRemoveFilter: (key: keyof ProjectFiltersType) => void;
  onClearAll: () => void;
}

const ActiveFilters: React.FC<ActiveFiltersProps> = ({
  filters,
  onRemoveFilter,
  onClearAll,
}) => {
  const activeFilterCount = Object.values(filters).filter(Boolean).length;
  
  if (activeFilterCount === 0) {
    return null;
  }

  return (
    <div className="p-4 bg-blue-50 border-b border-blue-200">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-medium text-blue-900">
            ({activeFilterCount})
        </h4>
        <Button
          size="sm"
          variant="ghost"
          onClick={onClearAll}
          className="text-blue-600 hover:text-blue-700 hover:bg-blue-100"
        >
           
        </Button>
      </div>
      
      <div className="flex flex-wrap gap-2">
        {filters.search && (
          <FilterChip
            label={`: "${filters.search}"`}
            onRemove={() => onRemoveFilter('search')}
          />
        )}
        
        {filters.status && filters.status.length > 0 && (
          <FilterChip
            label={`: ${filters.status.map(s => statusFilters.find(f => f.value === s)?.label).join(', ')}`}
            onRemove={() => onRemoveFilter('status')}
          />
        )}
        
        {filters.owner && filters.owner.length > 0 && (
          <FilterChip
            label={`: ${filters.owner.length}`}
            onRemove={() => onRemoveFilter('owner')}
          />
        )}
        
        {filters.dateRange && (
          <FilterChip
            label={`: ${format(new Date(filters.dateRange.start), 'yyyy/MM/dd', { locale: ko })} ~ ${format(new Date(filters.dateRange.end), 'yyyy/MM/dd', { locale: ko })}`}
            onRemove={() => onRemoveFilter('dateRange')}
          />
        )}
        
        {filters.tags && filters.tags.length > 0 && (
          <FilterChip
            label={`: ${filters.tags.join(', ')}`}
            onRemove={() => onRemoveFilter('tags')}
          />
        )}
      </div>
    </div>
  );
};

interface FilterChipProps {
  label: string;
  onRemove: () => void;
}

const FilterChip: React.FC<FilterChipProps> = ({ label, onRemove }) => {
  return (
    <span className="inline-flex items-center gap-1 px-2 py-1 bg-white border border-blue-300 text-blue-700 rounded-full text-xs">
      {label}
      <button
        onClick={onRemove}
        className="ml-1 hover:text-blue-900"
      >
        <X className="w-3 h-3" />
      </button>
    </span>
  );
};

// ========================================
//  
// ========================================

export const ProjectFilters: React.FC<ProjectFiltersProps> = ({
  className,
  onClose,
  showCloseButton = true,
}) => {
  const {
    activeFilters,
    updateFilters,
    clearFilters,
    hasActiveFilters,
  } = useProjectFilters();

  //   
  const handleRemoveFilter = (key: keyof ProjectFiltersType) => {
    const { [key]: removed, ...rest } = activeFilters;
    updateFilters(rest);
  };

  //   
  const handleStatusChange = (statuses: ProjectStatus[]) => {
    updateFilters({ 
      ...activeFilters,
      status: statuses.length > 0 ? statuses : undefined 
    });
  };

  //   
  const handleOwnerChange = (owners: number[]) => {
    updateFilters({ 
      ...activeFilters,
      owner: owners.length > 0 ? owners : undefined 
    });
  };

  //    
  const handleDateRangeChange = (dateRange: { start: string; end: string } | undefined) => {
    updateFilters({ 
      ...activeFilters,
      dateRange 
    });
  };

  //   
  const handleTagsChange = (tags: string[]) => {
    updateFilters({ 
      ...activeFilters,
      tags: tags.length > 0 ? tags : undefined 
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className={cn(
        'bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden',
        className
      )}
    >
      {/*  */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <FilterIcon className="w-5 h-5 text-gray-500" />
          <h2 className="text-lg font-semibold text-gray-900"></h2>
        </div>
        
        <div className="flex items-center gap-2">
          {hasActiveFilters && (
            <Button
              size="sm"
              variant="ghost"
              onClick={clearFilters}
              className="text-gray-500 hover:text-gray-700"
            >
              <RotateCcw className="w-4 h-4 mr-1" />
              
            </Button>
          )}
          
          {showCloseButton && onClose && (
            <Button
              size="sm"
              variant="ghost"
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              <X className="w-4 h-4" />
            </Button>
          )}
        </div>
      </div>

      {/*    */}
      <ActiveFilters
        filters={activeFilters}
        onRemoveFilter={handleRemoveFilter}
        onClearAll={clearFilters}
      />

      {/*   */}
      <div className="p-4 space-y-6 max-h-96 overflow-y-auto">
        {/*   */}
        <FilterSection
          title=" "
          icon={FilterIcon}
        >
          <CheckboxFilter
            options={statusFilters}
            selectedValues={activeFilters.status || []}
            onChange={handleStatusChange}
          />
        </FilterSection>

        {/*   */}
        <FilterSection
          title=" "
          icon={User}
        >
          <CheckboxFilter
            options={ownerFilters}
            selectedValues={activeFilters.owner || []}
            onChange={handleOwnerChange}
          />
        </FilterSection>

        {/*    */}
        <FilterSection
          title=" "
          icon={CalendarIcon}
        >
          <DateRangeFilter
            startDate={activeFilters.dateRange?.start}
            endDate={activeFilters.dateRange?.end}
            onChange={handleDateRangeChange}
          />
        </FilterSection>

        {/*   */}
        <FilterSection
          title=""
          icon={Tag}
        >
          <TagFilter
            selectedTags={activeFilters.tags || []}
            onChange={handleTagsChange}
          />
        </FilterSection>
      </div>

      {/*  ( / ) */}
      <div className="p-4 border-t border-gray-200 bg-gray-50 md:hidden">
        <div className="flex gap-3">
          <Button
            variant="outline"
            className="flex-1"
            onClick={onClose}
          >
            
          </Button>
          <Button
            className="flex-1"
            onClick={onClose}
          >
            
          </Button>
        </div>
      </div>
    </motion.div>
  );
};