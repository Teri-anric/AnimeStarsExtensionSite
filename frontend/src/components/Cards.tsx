import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { createAuthenticatedClient } from '../utils/apiClient';
import { CardApi, CardSchema, CardType, CardQuery, CardQueryOrderByEnum, CardFilter, StringFieldFilter, EnumFliedFilterCardType } from '../client';
import '../styles/Cards.css';
import { useDomain } from '../context/DomainContext';
import ShortFilter from './ShortFilter';
import AdvancedFilter from './AdvancedFilter';

const Cards = () => {
  const { isAuthenticated } = useAuth();
  const { currentDomain } = useDomain();
  const [cards, setCards] = useState<CardSchema[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [perPage, setPerPage] = useState(64);
  
  // Filter mode
  const [filterMode, setFilterMode] = useState<'short' | 'advanced'>('short');
  const [showAdvancedFilter, setShowAdvancedFilter] = useState(false);
  
  // Short filter states
  const [nameFilter, setNameFilter] = useState('');
  const [animeNameFilter, setAnimeNameFilter] = useState('');
  const [rankFilter, setRankFilter] = useState<string>('');
  
  // Advanced filter state
  const [advancedFilter, setAdvancedFilter] = useState<CardFilter | null>(null);

  useEffect(() => {
    if (isAuthenticated) {
      setCards([]);
      setLoading(true);
      fetchCards();
    }
  }, [isAuthenticated, page, perPage, nameFilter, animeNameFilter, rankFilter, advancedFilter, filterMode]);

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

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
  };

  const handlePageChange = (newPage: number) => {
    if (newPage > 0 && newPage <= totalPages) {
      setPage(newPage);
    }
  };

  const handleRankChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setRankFilter(e.target.value);
    setPage(1);
  };

  const handleFilterModeToggle = () => {
    if (filterMode === 'short') {
      setFilterMode('advanced');
      setShowAdvancedFilter(true);
    } else {
      setFilterMode('short');
      setShowAdvancedFilter(false);
      setAdvancedFilter(null);
    }
    setPage(1);
  };

  const handleAdvancedFilterChange = (filter: CardFilter | null) => {
    setAdvancedFilter(filter);
    setPage(1);
  };

  const handleAdvancedFilterClose = () => {
    setShowAdvancedFilter(false);
    if (!advancedFilter) {
      setFilterMode('short');
    }
  };

  const getCardMediaUrl = (path: string | null) => {
    if (!path) return '';
    return `${currentDomain}${path}`;
  };

  const getRankClass = (rank: CardType) => {
    return `rank-${rank.toLowerCase()}`;
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
          onNameFilterChange={setNameFilter}
          onAnimeNameFilterChange={setAnimeNameFilter}
          onRankFilterChange={setRankFilter}
          onSearch={handleSearch}
        />
      )}

      {showAdvancedFilter && (
        <AdvancedFilter
          onFilterChange={handleAdvancedFilterChange}
          onClose={handleAdvancedFilterClose}
        />
      )}

      {filterMode === 'advanced' && advancedFilter && (
        <div className="active-advanced-filter">
          <p>Advanced filter is active</p>
          <button onClick={() => setShowAdvancedFilter(true)} className="edit-filter-button">
            Edit Filter
          </button>
          <button onClick={() => {setAdvancedFilter(null); setFilterMode('short');}} className="clear-filter-button">
            Clear Filter
          </button>
        </div>
      )}
      
      {loading ? (
        <div className="loading">Loading cards...</div>
      ) : error ? (
        <div className="error-message">{error}</div>
      ) : (
        <>
          <div className="cards-grid">
            {cards.length > 0 ? cards.map((card) => (
              <div key={card.id} className={`card-item ${getRankClass(card.rank)}`}>
                {card.image && !card.mp4 && (
                  <div className="card-image">
                    <img 
                      src={getCardMediaUrl(card.image)} 
                      alt={card.name} 
                      loading="lazy"
                    />
                  </div>
                )}
                {card.mp4 && (
                  <div className="card-video">
                    <video autoPlay loop muted playsInline>
                      <source src={getCardMediaUrl(card.mp4)} type="video/mp4" />
                      {/* {card.webm && <source src={getCardMediaUrl(card.webm)} type="video/webm" />} */}
                      Your browser does not support the video tag.
                    </video>
                  </div>
                )}
              </div>
            )) : (
              <div className="no-cards">No cards found</div>
            )}
          </div>
          
          <div className="pagination">
            <button 
              onClick={() => handlePageChange(page - 1)}
              disabled={page === 1}
            >
              Previous
            </button>
            
            <span>
              Page {page} of {totalPages}
            </span>
            
            <button 
              onClick={() => handlePageChange(page + 1)}
              disabled={page === totalPages}
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default Cards; 