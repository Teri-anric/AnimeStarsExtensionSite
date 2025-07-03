import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import FilterQuery from './FilterQuery';
import { EntityFilterConfig, GenericFilter } from '../types/filter';
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
  
  // State management
  const [items, setItems] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  
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
      setError(`Failed to fetch ${filterConfig.entityName.toLowerCase()}. Please try again later.`);
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
    setCurrentFilter(filter);
    // Reset to first page when filter changes
    updateSearchParams({ page: '1' });
  };

  const handleSearch = () => {
    // Reset to first page when searching
    updateSearchParams({ page: '1' });
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
          Previous
        </button>
        
        <div className="pagination-info">
          {showPaginationInfo && (
            <span className="pagination-text">
              {paginationInfoTemplate 
                ? paginationInfoTemplate(page, totalPages, total)
                : `Page ${page} of ${totalPages} (${total} total)`
              }
            </span>
          )}
        </div>
        
        <button 
          onClick={() => handlePageChange(page + 1)} 
          disabled={page >= totalPages}
          className="pagination-button"
        >
          Next
        </button>
      </div>
    );
  };

  const renderContent = () => {
    if (loading) {
      return loadingComponent || (
        <div className="pagination-page-loading">
          Loading {filterConfig.entityName.toLowerCase()}...
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
          No {filterConfig.entityName.toLowerCase()} found matching your criteria.
        </div>
      );
    }

    return renderItems(items);
  };

  return (
    <div className={`pagination-page ${className}`}>
      <div className="pagination-page-header">
        <div className="pagination-page-title-section">
          {title && <h1 className="pagination-page-title">{title}</h1>}
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