import React, { useState, useEffect, useRef } from 'react';
import { GenericFilter, EntityFilterConfig } from '../types/filter';
import AdvancedFilter from './AdvancedFilter';
import '../styles/FilterQuery.css';

// Legacy props interface for backward compatibility
export interface FilterQueryProps<T = GenericFilter> {
  // Option 1: Use entity config (recommended)
  config?: EntityFilterConfig<T>;
  
  // Option 2: Individual props (legacy support)
  shortFilterFields?: Array<{ key: string; type: 'text' | 'select'; placeholder?: string; options?: Array<{ value: string; label: string }> }>;
  fieldOptions?: Array<{ value: string; label: string; type: 'string' | 'number' | 'enum' | 'datetime' | 'boolean'; enumOptions?: Array<{ value: string; label: string }> }>;
  sortOptions?: Array<{ value: string; label: string }>;
  
  // Filter state and callbacks
  filter: T | null;
  onFilterChange: (filter: T | null) => void;
  
  // Sorting state and callbacks
  currentSort?: string;
  onSortChange?: (value: string) => void;
  
  // Search functionality
  onSearch?: () => void;
  
  // UI configuration
  title?: string;
  showModeToggle?: boolean;
  defaultMode?: 'short' | 'advanced';
  
  // Custom styling
  className?: string;
}

const FilterQuery = <T extends GenericFilter = GenericFilter>({
  config,
  shortFilterFields,
  fieldOptions,
  sortOptions,
  filter,
  onFilterChange,
  currentSort,
  onSortChange,
  onSearch,
  title,
  showModeToggle = true,
  defaultMode,
  className = ''
}: FilterQueryProps<T>) => {
  // Extract configuration from either config object or individual props
  const entityConfig = config || {
    entityName: title || 'Entity',
    fieldOptions: fieldOptions || [],
    shortFilterFields: shortFilterFields || [],
    sortOptions: sortOptions || [],
    defaults: {
      sort: currentSort || '',
      filterMode: defaultMode || 'short',
      shortFilterValues: {}
    }
  };

  const [filterMode, setFilterMode] = useState<'short' | 'advanced'>(
    config?.defaults.filterMode || defaultMode || 'short'
  );
  const [showAdvancedFilter, setShowAdvancedFilter] = useState(
    (config?.defaults.filterMode || defaultMode || 'short') === 'advanced'
  );
  const [shortFilterValues, setShortFilterValues] = useState<Record<string, string>>(
    config?.defaults.shortFilterValues || {}
  );
  
  // Refs for auto-resizing inputs
  const inputRefs = useRef<Record<string, HTMLInputElement | null>>({});

  const adjustInputWidth = (input: HTMLInputElement, value: string, placeholder: string) => {
    const span = document.createElement('span');
    span.style.visibility = 'hidden';
    span.style.position = 'absolute';
    span.style.fontSize = '14px';
    span.style.fontFamily = getComputedStyle(input).fontFamily;
    span.style.padding = '0 10px';
    span.textContent = value || placeholder;
    
    document.body.appendChild(span);
    const textWidth = span.offsetWidth;
    document.body.removeChild(span);
    
    const newWidth = Math.max(120, textWidth + 20);
    input.style.width = `${newWidth}px`;
  };

  useEffect(() => {
    if (filterMode === 'short') {
      Object.keys(shortFilterValues).forEach(key => {
        const input = inputRefs.current[key];
        const field = entityConfig.shortFilterFields.find(f => f.key === key);
        if (input && field) {
          adjustInputWidth(input, shortFilterValues[key], field.placeholder || '');
        }
      });
    }
  }, [shortFilterValues, filterMode, entityConfig.shortFilterFields]);

  const handleModeToggle = () => {
    if (filterMode === 'short') {
      setFilterMode('advanced');
      setShowAdvancedFilter(true);
    } else {
      setFilterMode('short');
      setShowAdvancedFilter(false);
      onFilterChange(null);
    }
  };

  const handleShortFilterChange = (key: string, value: string) => {
    setShortFilterValues(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleShortFilterSearch = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Use custom build filter function if provided, otherwise use default logic
    let resultFilter: T | null = null;
    
    if (entityConfig.buildShortFilter) {
      resultFilter = entityConfig.buildShortFilter(shortFilterValues);
    } else {
      // Default filter building logic
      const filters: GenericFilter[] = [];
      
      entityConfig.shortFilterFields.forEach(field => {
        const value = shortFilterValues[field.key];
        if (value && value.trim()) {
          // For text fields, use icontains
          if (field.type === 'text') {
            filters.push({
              [field.key]: { icontains: value.trim() }
            });
          } else {
            // For select fields, use exact match
            filters.push({
              [field.key]: { eq: value }
            });
          }
        }
      });

      if (filters.length === 1) {
        resultFilter = filters[0] as T;
      } else if (filters.length > 1) {
        resultFilter = { and: filters } as T;
      }
    }

    onFilterChange(resultFilter);
    if (onSearch) {
      onSearch();
    }
  };

  const handleAdvancedFilterChange = (newFilter: GenericFilter | null) => {
    onFilterChange(newFilter as T);
  };

  const handleAdvancedFilterClose = () => {
    setShowAdvancedFilter(false);
    if (!filter) {
      setFilterMode('short');
    }
  };

  const renderShortFilter = () => (
    <div className="short-filter">
      <form onSubmit={handleShortFilterSearch} className="compact-form">
        <div className="short-filters">
          {entityConfig.shortFilterFields.map(field => (
            <div key={field.key} className="filter-field">
              {field.type === 'text' ? (
                <input
                  type="text"
                  value={shortFilterValues[field.key] || ''}
                  onChange={(e) => handleShortFilterChange(field.key, e.target.value)}
                  placeholder={field.placeholder}
                  className="compact-input"
                  ref={(el) => { inputRefs.current[field.key] = el; }}
                />
              ) : (
                <select
                  value={shortFilterValues[field.key] || ''}
                  onChange={(e) => handleShortFilterChange(field.key, e.target.value)}
                  className="compact-select"
                >
                  <option value="">{field.placeholder || 'All'}</option>
                  {field.options?.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              )}
            </div>
          ))}
          
          <button type="submit" className="search-button">
            Search
          </button>
        </div>
      </form>
    </div>
  );

  const renderSortOptions = () => {
    const effectiveCurrentSort = currentSort || entityConfig.defaults.sort;
    const effectiveOnSortChange = onSortChange;
    
    if (!entityConfig.sortOptions.length || !effectiveOnSortChange) return null;
    
    return (
      <div className="sort-options">
        <label className="sort-label">
          Sort by:
          <select
            value={effectiveCurrentSort}
            onChange={(e) => effectiveOnSortChange(e.target.value)}
            className="sort-select"
          >
            {entityConfig.sortOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </div>
    );
  };

  return (
    <div className={`filter-query ${className}`}>
      {showModeToggle && (
        <div className="filter-mode-selector">
          <button 
            onClick={handleModeToggle}
            className={`filter-mode-button ${filterMode === 'short' ? 'active' : ''}`}
          >
            {filterMode === 'short' ? 'Switch to Advanced Filter' : 'Switch to Short Filter'}
          </button>
        </div>
      )}

      <div className="filter-query-content">
        <div className="filter-section">
          {filterMode === 'short' && entityConfig.shortFilterFields.length > 0 && renderShortFilter()}

          {showAdvancedFilter && (
            <AdvancedFilter
              onFilterChange={handleAdvancedFilterChange}
              onClose={handleAdvancedFilterClose}
              initialFilter={filter}
              fieldOptions={entityConfig.fieldOptions}
              title={`Advanced ${entityConfig.ui?.title || entityConfig.entityName || title || 'Filter'}`}
            />
          )}
        </div>

        {renderSortOptions()}
      </div>
    </div>
  );
};

export default FilterQuery; 