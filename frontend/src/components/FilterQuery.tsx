import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
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
  
  // URL integration
  useUrlParams?: boolean; // Enable URL parameter synchronization (default: true)
  
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
  useUrlParams = true,
  onSearch,
  title,
  showModeToggle = true,
  defaultMode,
  className = ''
}: FilterQueryProps<T>) => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { t } = useTranslation();

  // Function to translate labels
  const translateLabel = (label: string): string => {
    if (label.startsWith('filterConfig.') || label.startsWith('cards.') || label.startsWith('decks.') || label.startsWith('ranks.')) {
      return t(label);
    }
    return label;
  };

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

  // URL parameter integration
  const getInitialSort = () => {
    if (useUrlParams) {
      const urlSort = searchParams.get('sort');
      if (urlSort) return urlSort;
    }
    return currentSort || entityConfig.defaults.sort;
  };

  const getInitialMode = () => {
    if (useUrlParams) {
      const urlMode = searchParams.get('mode');
      if (urlMode === 'short' || urlMode === 'advanced') return urlMode;
    }
    return entityConfig.defaults.filterMode || defaultMode || 'short';
  };

  const getInitialShortFilterValues = () => {
    if (useUrlParams) {
      // Instead of parsing shortFilter JSON, read individual URL parameters
      const values: Record<string, string> = {};
      entityConfig.shortFilterFields.forEach(field => {
        const value = searchParams.get(field.key);
        if (value) {
          values[field.key] = value;
        }
      });
      return values;
    }
    return entityConfig.defaults.shortFilterValues || {};
  };

  const [filterMode, setFilterMode] = useState<'short' | 'advanced'>(getInitialMode);
  const [showAdvancedFilter, setShowAdvancedFilter] = useState(getInitialMode() === 'advanced');
  const [shortFilterValues, setShortFilterValues] = useState<Record<string, string>>(getInitialShortFilterValues);
  const [sortValue, setSortValue] = useState(getInitialSort);
  
  // Refs for auto-resizing inputs
  const inputRefs = useRef<Record<string, HTMLInputElement | null>>({});

  // Function to update URL parameters
  const updateUrlParams = (updates: { 
    sort?: string; 
    shortFilter?: Record<string, string>; 
    advancedFilter?: GenericFilter | null;
    mode?: string 
  }) => {
    if (!useUrlParams) return;

    setSearchParams(prev => {
      const newParams = new URLSearchParams(prev);
      
      if (updates.sort !== undefined) {
        if (updates.sort) {
          newParams.set('sort', updates.sort);
        } else {
          newParams.delete('sort');
        }
      }
      
      // Handle short filter values - set individual parameters for each field
      if (updates.shortFilter !== undefined) {
        // First, remove all existing short filter parameters
        entityConfig.shortFilterFields.forEach(field => {
          newParams.delete(field.key);
        });
        
        // Then set new values for fields that have values
        Object.entries(updates.shortFilter).forEach(([key, value]) => {
          if (value && value.trim()) {
            newParams.set(key, value);
          }
        });
      }
      
      // Handle advanced filter
      if (updates.advancedFilter !== undefined) {
        if (updates.advancedFilter) {
          const filterJson = JSON.stringify(updates.advancedFilter);
          console.log('Setting filter in URL:', filterJson);
          newParams.set('filter', encodeURIComponent(filterJson));
        } else {
          newParams.delete('filter');
        }
      }
      
      if (updates.mode !== undefined) {
        if (updates.mode && updates.mode !== (defaultMode || 'short')) {
          newParams.set('mode', updates.mode);
        } else {
          newParams.delete('mode');
        }
      }
      
      return newParams;
    });
  };

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

  // Sync external currentSort with internal sortValue
  useEffect(() => {
    if (currentSort !== undefined && currentSort !== sortValue) {
      setSortValue(currentSort);
      updateUrlParams({ sort: currentSort });
    }
  }, [currentSort]);

  // Sync short filter values with URL parameters
  useEffect(() => {
    if (useUrlParams && filterMode === 'short') {
      const urlValues: Record<string, string> = {};
      entityConfig.shortFilterFields.forEach(field => {
        const value = searchParams.get(field.key);
        if (value) {
          urlValues[field.key] = value;
        }
      });
      
      // Only update if values have actually changed
      const hasChanges = Object.keys(urlValues).length !== Object.keys(shortFilterValues).length ||
        Object.entries(urlValues).some(([key, value]) => shortFilterValues[key] !== value);
      
      if (hasChanges) {
        setShortFilterValues(urlValues);
      }
    }
  }, [useUrlParams, searchParams, filterMode, entityConfig.shortFilterFields]);

  // Initialize filter from URL if in advanced mode
  useEffect(() => {
    if (useUrlParams) {
      const urlFilter = searchParams.get('filter');
      const urlMode = searchParams.get('mode');
      
      if (urlFilter && urlMode === 'advanced') {
        try {
          const parsedFilter = JSON.parse(decodeURIComponent(urlFilter));
          console.log('Parsing filter from URL:', parsedFilter);
          onFilterChange(parsedFilter as T);
          if (filterMode !== 'advanced') {
            setFilterMode('advanced');
            setShowAdvancedFilter(true);
          }
        } catch (e) {
          console.warn('Failed to parse advanced filter from URL:', e);
        }
      }
    }
  }, [useUrlParams, searchParams]);

  const handleModeToggle = () => {
    if (filterMode === 'short') {
      // Switching to advanced mode
      setFilterMode('advanced');
      setShowAdvancedFilter(true);
      updateUrlParams({ mode: 'advanced' });
      
      // If we have short filter values, convert them to advanced filter
      if (Object.keys(shortFilterValues).some(key => shortFilterValues[key])) {
        let convertedFilter: T | null = null;
        
        // Safely check for buildShortFilter
        if (entityConfig && 'buildShortFilter' in entityConfig && entityConfig.buildShortFilter) {
          convertedFilter = entityConfig.buildShortFilter(shortFilterValues);
        } else {
          // Default conversion logic
          const filters: GenericFilter[] = [];
          
          entityConfig.shortFilterFields.forEach(field => {
            const value = shortFilterValues[field.key];
            if (value && value.trim()) {
              if (field.type === 'text') {
                filters.push({
                  [field.key]: { icontains: value.trim() }
                });
              } else {
                filters.push({
                  [field.key]: { eq: value }
                });
              }
            }
          });

          if (filters.length === 1) {
            convertedFilter = filters[0] as T;
          } else if (filters.length > 1) {
            convertedFilter = { and: filters } as T;
          }
        }
        
        if (convertedFilter) {
          onFilterChange(convertedFilter);
          updateUrlParams({ advancedFilter: convertedFilter });
        }
      }
    } else {
      // Switching to short mode
      setFilterMode('short');
      setShowAdvancedFilter(false);
      onFilterChange(null);
      setShortFilterValues({});
      updateUrlParams({ mode: 'short', shortFilter: {}, advancedFilter: null });
    }
  };

  const handleShortFilterChange = (key: string, value: string) => {
    const newValues = {
      ...shortFilterValues,
      [key]: value
    };
    
    setShortFilterValues(newValues);
    updateUrlParams({ shortFilter: newValues });
  };

  const handleShortFilterSearch = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Use custom build filter function if provided, otherwise use default logic
    let resultFilter: T | null = null;
    
    // Safely check for buildShortFilter
    if (entityConfig && 'buildShortFilter' in entityConfig && entityConfig.buildShortFilter) {
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
    // Update URL with the generated filter
    updateUrlParams({ advancedFilter: resultFilter });
    if (onSearch) {
      onSearch();
    }
  };

  const handleAdvancedFilterChange = (newFilter: GenericFilter | null) => {
    onFilterChange(newFilter as T);
    updateUrlParams({ advancedFilter: newFilter });
  };

  const handleAdvancedFilterClose = () => {
    setShowAdvancedFilter(false);
    if (!filter) {
      setFilterMode('short');
    }
  };

  useEffect(() => {
    handleShortFilterSearch({ preventDefault: () => {} } as React.FormEvent);
  }, []);

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
                  placeholder={translateLabel(field.placeholder || '')}
                  className="compact-input"
                  ref={(el) => { inputRefs.current[field.key] = el; }}
                />
              ) : (
                <select
                  value={shortFilterValues[field.key] || ''}
                  onChange={(e) => handleShortFilterChange(field.key, e.target.value)}
                  className="compact-select"
                >
                  <option value="">{translateLabel(field.placeholder || t('filterQuery.all'))}</option>
                  {field.options?.map(option => (
                    <option key={option.value} value={option.value}>
                      {translateLabel(option.label)}
                    </option>
                  ))}
                </select>
              )}
            </div>
          ))}
          
          <button type="submit" className="search-button">
            {t('filterQuery.search')}
          </button>
        </div>
      </form>
    </div>
  );

  const handleSortChange = (newSort: string) => {
    setSortValue(newSort);
    updateUrlParams({ sort: newSort });
    if (onSortChange) {
      onSortChange(newSort);
    }
  };

  const renderSortOptions = () => {
    if (!entityConfig.sortOptions.length) return null;
    
    return (
      <div className="sort-options">
        <label className="sort-label">
          {t('filterQuery.sortBy')}
          <select
            value={sortValue}
            onChange={(e) => handleSortChange(e.target.value)}
            className="sort-select"
          >
            {entityConfig.sortOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {translateLabel(option.label)}
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
            {filterMode === 'short' ? t('filterQuery.switchToAdvancedFilter') : t('filterQuery.switchToShortFilter')}
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
              title={`Advanced ${translateLabel((entityConfig as any).ui?.title || entityConfig.entityName || title || 'Filter')}`}
            />
          )}
        </div>

        {renderSortOptions()}
      </div>
    </div>
  );
};

export default FilterQuery; 