import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { createAuthenticatedClient } from '../../utils/apiClient';
import { CardApi, CardSchema, CardType, CardQuery, CardFilter } from '../../client';
import '../../styles/Cards.css';
import ShortFilter from '../../components/ShortFilter';
import AdvancedFilter from '../../components/AdvancedFilter';
import Card from '../../components/Card';
import CardInfoPanel from '../../components/CardInfoPanel';
import SortOptions, { SortOption } from '../../components/SortOptions';

const CardsPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { isAuthenticated } = useAuth();
  const [cards, setCards] = useState<CardSchema[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [totalPages, setTotalPages] = useState(1);
  const [perPage] = useState(63);

  // Sort options for cards
  const cardSortOptions: SortOption[] = [
    { value: "card_id asc", label: 'Card ID (Ascending)' },
    { value: "card_id desc", label: 'Card ID (Descending)' },
    { value: "name asc", label: 'Name (A-Z)' },
    { value: "name desc", label: 'Name (Z-A)' },
    { value: "rank asc", label: 'Rank (Low to High)' },
    { value: "rank desc", label: 'Rank (High to Low)' },
    { value: "anime_name asc", label: 'Anime Name (A-Z)' },
    { value: "anime_name desc", label: 'Anime Name (Z-A)' },
    { value: 'created_at desc', label: 'Newest First' },
    { value: 'created_at asc', label: 'Oldest First' },
    { value: 'updated_at desc', label: 'Recently Updated' },
    { value: 'updated_at asc', label: 'Least Recently Updated' },
  ];
  
  // Card info panel state
  const [selectedCard, setSelectedCard] = useState<CardSchema | null>(null);
  const [isCardInfoOpen, setIsCardInfoOpen] = useState(false);
  
  // Get values from URL parameters
  const page = parseInt(searchParams.get('page') || '1');
  const nameFilter = searchParams.get('name') || '';
  const animeNameFilter = searchParams.get('anime') || '';
  const rankFilter = searchParams.get('rank') || '';
  const filterMode = (searchParams.get('mode') as 'short' | 'advanced') || 'short';
  const advancedFilterParam = searchParams.get('filter');
  const sortBy = searchParams.get('sort') || "created_at desc";
  
  // Filter mode
  const [showAdvancedFilter, setShowAdvancedFilter] = useState(filterMode === 'advanced');
  
  // Advanced filter state - parse from URL parameter
  const [advancedFilter, setAdvancedFilter] = useState<CardFilter | null>(() => {
    if (advancedFilterParam) {
      try {
        return JSON.parse(decodeURIComponent(advancedFilterParam));
      } catch (e) {
        console.error('Failed to parse advanced filter from URL:', e);
        return null;
      }
    }
    return null;
  });

  useEffect(() => {
    if (isAuthenticated) {
      setCards([]);
      setLoading(true);
      fetchCards();
    }
  }, [isAuthenticated, page, nameFilter, animeNameFilter, rankFilter, advancedFilter, filterMode, advancedFilterParam, sortBy]);

  useEffect(() => {
    setShowAdvancedFilter(filterMode === 'advanced');
  }, [filterMode]);

  useEffect(() => {
    if (advancedFilterParam) {
      try {
        const parsedFilter = JSON.parse(decodeURIComponent(advancedFilterParam));
        setAdvancedFilter(parsedFilter);
      } catch (e) {
        console.error('Failed to parse advanced filter from URL:', e);
        setAdvancedFilter(null);
      }
    } else {
      setAdvancedFilter(null);
    }
  }, [advancedFilterParam]);

  const buildFilter = (): CardFilter | null => {
    if (filterMode === 'advanced') {
      return advancedFilter;
    }

    // Short filter logic
    const filters: CardFilter[] = [];

    if (nameFilter) {
      const nameFilterConditions: CardFilter[] = [
        {
          name: {
            ilike: `%${nameFilter}%`
          }
        }
      ];
      
      // Only add card_id filter if nameFilter is a valid number
      const cardIdNumber = parseInt(nameFilter);
      if (!isNaN(cardIdNumber)) {
        nameFilterConditions.push({
          card_id: {
            eq: cardIdNumber
          }
        });
      }
      
      filters.push({
        or: nameFilterConditions
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
      const filter = buildFilter();
      
      console.log('Fetching cards with filter:', JSON.stringify(filter, null, 2));
      console.log('Filter mode:', filterMode);
      console.log('Name filter:', nameFilter);
      console.log('Anime filter:', animeNameFilter);
      console.log('Rank filter:', rankFilter);
      console.log('Advanced filter:', JSON.stringify(advancedFilter, null, 2));
      
      const cardQuery: CardQuery = {
        page,
        per_page: perPage,
        filter,
        order_by: sortBy
      };

      const response = await cardApi.getCardsApiCardPost(cardQuery);
      
      console.log('Server response:', {
        total: response.data.total,
        totalPages: response.data.total_pages,
        itemsCount: response.data.items.length,
        firstItem: response.data.items[0]
      });
      
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
      updateSearchParams({ mode: 'short', filter: null, page: '1' });
      setShowAdvancedFilter(false);
      setAdvancedFilter(null);
    }
  };

  const handleAdvancedFilterChange = (filter: CardFilter | null) => {
    setAdvancedFilter(filter);
    const filterParam = filter ? encodeURIComponent(JSON.stringify(filter)) : null;
    updateSearchParams({ filter: filterParam, page: '1' });
  };

  const handleAdvancedFilterClose = () => {
    setShowAdvancedFilter(false);
    if (!advancedFilter) {
      updateSearchParams({ mode: 'short', filter: null });
    }
  };

  const handleSortChange = (value: string) => {
    updateSearchParams({ sort: value, page: '1' });
  };

  const handleCardClick = (card: CardSchema) => {
    setSelectedCard(card);
    setIsCardInfoOpen(true);
  };

  const handleCardInfoClose = () => {
    setIsCardInfoOpen(false);
    setSelectedCard(null);
  };



  return (
    <div className={`cards-container ${isCardInfoOpen ? 'with-panel' : ''}`}>
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

      <div className="cards-controls">
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
            initialFilter={advancedFilter}
          />
        )}

        <SortOptions
          options={cardSortOptions}
          currentValue={sortBy}
          onChange={handleSortChange}
          className="cards-sort"
        />
      </div>

      {loading ? (
        <div className="loading">Loading cards...</div>
      ) : error ? (
        <div className="error-message">{error}</div>
      ) : (
        <>
          <div className="cards-grid">
            {cards.length > 0 ? cards.map((card) => (
              <Card 
                key={card.id} 
                card={card} 
                onClick={() => handleCardClick(card)}
              />
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
      
      {/* Card Info Panel */}
      <CardInfoPanel
        card={selectedCard}
        isOpen={isCardInfoOpen}
        onClose={handleCardInfoClose}
      />
    </div>
  );
};

export default CardsPage; 