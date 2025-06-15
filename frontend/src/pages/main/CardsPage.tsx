import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { createAuthenticatedClient } from '../../utils/apiClient';
import { CardApi, CardSchema, CardType, CardQuery, CardQueryOrderByEnum, CardFilter } from '../../client';
import '../../styles/Cards.css';
import ShortFilter from '../../components/ShortFilter';
import AdvancedFilter from '../../components/AdvancedFilter';
import Card from '../../components/Card';

const CardsPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { isAuthenticated } = useAuth();
  const [cards, setCards] = useState<CardSchema[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [totalPages, setTotalPages] = useState(1);
  const [perPage] = useState(63);
  
  // Get values from URL parameters
  const page = parseInt(searchParams.get('page') || '1');
  const nameFilter = searchParams.get('name') || '';
  const animeNameFilter = searchParams.get('anime') || '';
  const rankFilter = searchParams.get('rank') || '';
  const filterMode = (searchParams.get('mode') as 'short' | 'advanced') || 'short';
  
  // Filter mode
  const [showAdvancedFilter, setShowAdvancedFilter] = useState(false);
  
  // Advanced filter state
  const [advancedFilter, setAdvancedFilter] = useState<CardFilter | null>(null);

  useEffect(() => {
    if (isAuthenticated) {
      setCards([]);
      setLoading(true);
      fetchCards();
    }
  }, [isAuthenticated, page, nameFilter, animeNameFilter, rankFilter, advancedFilter, filterMode]);

  const buildFilter = (): CardFilter | null => {
    if (filterMode === 'advanced') {
      return advancedFilter;
    }

    // Short filter logic
    const filters: CardFilter[] = [];

    if (nameFilter) {
      filters.push({
        or: [
          {
            name: {
              ilike: `%${nameFilter}%`
            }
          }, {
            card_id: {
              eq: parseInt(nameFilter)
            }
          }
        ]
      });
    }

    if (animeNameFilter) {
      filters.push({or: [{
        anime_name: {
          ilike: `%${animeNameFilter}%`
        }
      }, {
        anime_link: {
          ilike: `%${animeNameFilter}%`
        }
      }]});
    }

    if (rankFilter) {
      filters.push({
        rank: {
          eq: rankFilter as CardType
        }
      });
    }

    if (filters.length === 0) {
      return null;
    }

    if (filters.length === 1) {
      return filters[0];
    }

    return { and: filters };
  };

  const fetchCards = async () => {
    try {
      const cardApi = createAuthenticatedClient(CardApi);
      
      const cardQuery: CardQuery = {
        page,
        per_page: perPage,
        filter: buildFilter(),
        order_by: CardQueryOrderByEnum.Id
      };

      const response = await cardApi.getCardsApiCardPost(cardQuery);
      
      setCards(response.data.items);
      setTotalPages(response.data.total_pages);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching cards:', err);
      setError('Failed to fetch cards. Please try again later.');
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

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    updateSearchParams({ page: '1' });
  };

  const handlePageChange = (newPage: number) => {
    if (newPage > 0 && newPage <= totalPages) {
      updateSearchParams({ page: newPage.toString() });
    }
  };

  const handleNameFilterChange = (value: string) => {
    updateSearchParams({ name: value, page: '1' });
  };

  const handleAnimeNameFilterChange = (value: string) => {
    updateSearchParams({ anime: value, page: '1' });
  };

  const handleRankFilterChange = (value: string) => {
    updateSearchParams({ rank: value, page: '1' });
  };

  const handleFilterModeToggle = () => {
    if (filterMode === 'short') {
      updateSearchParams({ mode: 'advanced', page: '1' });
      setShowAdvancedFilter(true);
    } else {
      updateSearchParams({ mode: 'short', page: '1' });
      setShowAdvancedFilter(false);
      setAdvancedFilter(null);
    }
  };

  const handleAdvancedFilterChange = (filter: CardFilter | null) => {
    setAdvancedFilter(filter);
    updateSearchParams({ page: '1' });
  };

  const handleAdvancedFilterClose = () => {
    setShowAdvancedFilter(false);
    if (!advancedFilter) {
      updateSearchParams({ mode: 'short' });
    }
  };



  return (
    <div className="cards-container">
      <div className="cards-header">
        <h1>Anime Cards</h1>
        
        <div className="filter-mode-selector">
          <button 
            onClick={handleFilterModeToggle}
            className={`filter-mode-button ${filterMode === 'short' ? 'active' : ''}`}
          >
            {filterMode === 'short' ? 'Switch to Advanced Filter' : 'Switch to Short Filter'}
          </button>
        </div>
      </div>

      {filterMode === 'short' && (
        <ShortFilter
          nameFilter={nameFilter}
          animeNameFilter={animeNameFilter}
          rankFilter={rankFilter}
          onNameFilterChange={handleNameFilterChange}
          onAnimeNameFilterChange={handleAnimeNameFilterChange}
          onRankFilterChange={handleRankFilterChange}
          onSearch={handleSearch}
        />
      )}

      {showAdvancedFilter && (
        <AdvancedFilter
          onFilterChange={handleAdvancedFilterChange}
          onClose={handleAdvancedFilterClose}
        />
      )}

      {loading ? (
        <div className="loading">Loading cards...</div>
      ) : error ? (
        <div className="error-message">{error}</div>
      ) : (
        <>
          <div className="cards-grid">
            {cards.length > 0 ? cards.map((card) => (
              <Card key={card.id} card={card} />
            )) : (
              <div className="no-cards">No cards found matching your criteria.</div>
            )}
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button 
                onClick={() => handlePageChange(page - 1)} 
                disabled={page <= 1}
              >
                Previous
              </button>
              
              <span>Page {page} of {totalPages}</span>
              
              <button 
                onClick={() => handlePageChange(page + 1)} 
                disabled={page >= totalPages}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default CardsPage; 