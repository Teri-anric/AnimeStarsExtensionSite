import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import FilterQuery from './FilterQuery';
import { EntityFilterConfig, GenericFilter } from '../types/filter';
import { useTranslation } from 'react-i18next';
import '../styles/PaginationPage.css';

// Generic pagination response interface
export interface PaginationResponse<T> {
  total: number;
  page: number;
  per_page: number;
  items: T[];
  total_pages: number;
  has_next: boolean;
}

// Generic query interface
export interface PaginationQuery<F = GenericFilter> {
  page?: number;
  per_page?: number;
  filter?: F | null;
  order_by?: any;
}

export interface PaginationPageProps<T, F = GenericFilter, Q = PaginationQuery<F>> {
  // API function to fetch data
  fetchData: (query: Q) => Promise<PaginationResponse<T>>;
  
  // Filter configuration
  filterConfig: EntityFilterConfig<F>;
  
  // Function to render items
  renderItems: (items: T[]) => React.ReactNode;
  
  // Build query function (optional, for custom query building)
  buildQuery?: (page: number, perPage: number, filter: F | null, sortBy: string) => Q;
  
  // General settings
  title?: string;
  perPage?: number;
  className?: string;
  
  // Custom components
  loadingComponent?: React.ReactNode;
  errorComponent?: (error: string) => React.ReactNode;
  emptyComponent?: React.ReactNode;
  
  // Additional header content
  headerActions?: React.ReactNode;
  
  // Custom pagination info
  showPaginationInfo?: boolean;
  paginationInfoTemplate?: (current: number, total: number, itemsCount: number) => string;
}

const PaginationPage = <T, F extends GenericFilter = GenericFilter, Q extends PaginationQuery<F> = PaginationQuery<F>>({
  fetchData,
  filterConfig,
  renderItems,
  buildQuery,
  title,
  perPage = 20,
  className = '',
  loadingComponent,
  errorComponent,
  emptyComponent,
  headerActions,
  showPaginationInfo = true,
  paginationInfoTemplate
}: PaginationPageProps<T, F, Q>) => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { t } = useTranslation();

  // Function to translate labels
  const translateLabel = (label: string): string => {
    if (label.startsWith('filterConfig.') || label.startsWith('cards.') || label.startsWith('decks.') || label.startsWith('ranks.')) {
      return t(label);
    }
    return label;
  };
  
  // State management
  const [items, setItems] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
    
  // Page input state
  const [showPageInput, setShowPageInput] = useState(false);
  const [pageInputValue, setPageInputValue] = useState('');
    
  // Get values from URL parameters
  const page = parseInt(searchParams.get('page') || '1');
  const sortBy = searchParams.get('sort') || filterConfig.defaults.sort;
  const filterParam = searchParams.get('filter');
  
  // Parse filter from URL
  const [currentFilter, setCurrentFilter] = useState<F | null>(() => {
    if (filterParam) {
      try {
        return JSON.parse(decodeURIComponent(filterParam));
      } catch (e) {
        console.error('Failed to parse filter from URL:', e);
        return null;
      }
    }
    return null;
  });

  // Default query builder
  const defaultBuildQuery = (page: number, perPage: number, filter: F | null, sortBy: string): Q => {
    return {
      page,
      per_page: perPage,
      filter,
      order_by: sortBy
    } as Q;
  };

  const queryBuilder = buildQuery || defaultBuildQuery;

  // Fetch data effect
  useEffect(() => {
    fetchDataWithParams();
  }, [page, currentFilter, sortBy]);

  // Update filter state when URL changes
  useEffect(() => {
    if (filterParam) {
      try {
        const parsedFilter = JSON.parse(decodeURIComponent(filterParam));
        setCurrentFilter(parsedFilter);
      } catch (e) {
        console.error('Failed to parse filter from URL:', e);
        setCurrentFilter(null);
      }
    } else {
      setCurrentFilter(null);
    }
  }, [filterParam]);

  const fetchDataWithParams = async () => {
    try {
      setLoading(true);
      setError('');
      
      const query = queryBuilder(page, perPage, currentFilter, sortBy);
      console.log('Fetching data with query:', JSON.stringify(query, null, 2));
      
      const response = await fetchData(query);
      
      console.log('Server response:', {
        total: response.total,
        totalPages: response.total_pages,
        itemsCount: response.items.length,
        page: response.page
      });
      
      setItems(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError(t('pagination.error', { entityName: filterConfig.entityName.toLowerCase() }));
      setLoading(false);
    }
  };

  const updateSearchParams = (updates: Record<string, string | null>) => {
    const newParams = new URLSearchParams(searchParams);
    
    Object.entries(updates).forEach(([key, value]) => {
      if (value === null || value === '') {
        newParams.delete(key);
      } else {
        newParams.set(key, value);
      }
    });
    
    setSearchParams(newParams);
  };

  const handlePageChange = (newPage: number) => {
    if (newPage > 0 && newPage <= totalPages) {
      updateSearchParams({ page: newPage.toString() });
    }
  };

  const handleFilterChange = (filter: F | null) => {
    // Check if filter actually changed to avoid unnecessary page resets
    const filterChanged = JSON.stringify(currentFilter) !== JSON.stringify(filter);
    
    setCurrentFilter(filter);
    
    // Only reset to first page when filter actually changes
    if (filterChanged) {
      updateSearchParams({ page: '1' });
    }
  };

  const handleSearch = () => {
    // Reset to first page when searching
    updateSearchParams({ page: '1' });
  };

  const handlePageInputToggle = () => {
    if (showPageInput) {
      setShowPageInput(false);
      setPageInputValue('');
    } else {
      setShowPageInput(true);
      setPageInputValue(page.toString());
    }
  };

  const handlePageInputChange = (value: string) => {
    // Only allow numeric input
    if (value === '' || /^\d+$/.test(value)) {
      setPageInputValue(value);
    }
  };

  const handlePageInputSubmit = () => {
    const pageNumber = parseInt(pageInputValue);
    if (pageNumber >= 1 && pageNumber <= totalPages) {
      handlePageChange(pageNumber);
      setShowPageInput(false);
      setPageInputValue('');
    }
  };

  const handlePageInputKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handlePageInputSubmit();
    } else if (e.key === 'Escape') {
      setShowPageInput(false);
      setPageInputValue('');
    }
  };

  const renderPagination = () => {
    if (totalPages <= 1) return null;

    return (
      <div className="pagination">
        <button 
          onClick={() => handlePageChange(page - 1)} 
          disabled={page <= 1}
          className="pagination-button"
        >
          {t('pagination.previousPage')}
        </button>
        
        <div className="pagination-info">
          {showPaginationInfo && (
            <>
              {!showPageInput ? (
                <span 
                  className="pagination-text clickable-page-info" 
                  onClick={handlePageInputToggle}
                  title={t('paginationPage.clickToJumpToPage')}
                >
                  {paginationInfoTemplate 
                    ? paginationInfoTemplate(page, totalPages, total)
                    : `${t('pagination.page')} ${page} ${t('pagination.of')} ${totalPages} (${total} ${t('pagination.items')})`
                  }
                </span>
              ) : (
                <div className="page-input-container">
                  <span className="page-input-label">{t('pagination.goToPage')}:</span>
                  <input
                    type="text"
                    value={pageInputValue}
                    onChange={(e) => handlePageInputChange(e.target.value)}
                    onKeyDown={handlePageInputKeyPress}
                    onBlur={() => {
                      // Auto-submit if valid when focus is lost
                      const pageNumber = parseInt(pageInputValue);
                      if (pageNumber >= 1 && pageNumber <= totalPages) {
                        handlePageInputSubmit();
                      } else {
                        setShowPageInput(false);
                        setPageInputValue('');
                      }
                    }}
                    className="page-input"
                    placeholder={`1-${totalPages}`}
                    autoFocus
                  />
                  <button
                    onClick={handlePageInputSubmit}
                    disabled={!pageInputValue || parseInt(pageInputValue) < 1 || parseInt(pageInputValue) > totalPages}
                    className="page-input-submit"
                  >
                    {t('common.ok')}
                  </button>
                  <button
                    onClick={() => {
                      setShowPageInput(false);
                      setPageInputValue('');
                    }}
                    className="page-input-cancel"
                  >
                    ×
                  </button>
                </div>
              )}
            </>
          )}
        </div>
        
        <button 
          onClick={() => handlePageChange(page + 1)} 
          disabled={page >= totalPages}
          className="pagination-button"
        >
          {t('pagination.nextPage')}
        </button>
      </div>
    );
  };

  const renderContent = () => {
    if (loading) {
      return loadingComponent || (
        <div className="pagination-page-loading">
          {t('paginationPage.loadingEntity', { entityName: filterConfig.entityName.toLowerCase() })}
        </div>
      );
    }

    if (error) {
      return errorComponent ? errorComponent(error) : (
        <div className="pagination-page-error">
          {error}
        </div>
      );
    }

    if (items.length === 0) {
      return emptyComponent || (
        <div className="pagination-page-empty">
          {t('paginationPage.noItems')}
        </div>
      );
    }

    return renderItems(items);
  };

  return (
    <div className={`pagination-page ${className}`}>
      <div className="pagination-page-header">
        <div className="pagination-page-title-section">
          {title && <h1 className="pagination-page-title">{translateLabel(title)}</h1>}
          {headerActions && <div className="pagination-page-actions">{headerActions}</div>}
        </div>
      </div>

      <div className="pagination-page-controls">
        <FilterQuery
          config={filterConfig}
          filter={currentFilter as any}
          onFilterChange={(filter: any) => handleFilterChange(filter as F)}
          currentSort={sortBy}
          onSearch={handleSearch}
        />
      </div>

      <div className="pagination-page-content">
        {renderContent()}
      </div>

      <div className="pagination-page-footer">
        {renderPagination()}
      </div>
    </div>
  );
};      

export default PaginationPage; 