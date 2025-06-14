import React from 'react';
import '../styles/ShortFilter.css';

interface ShortFilterProps {
  nameFilter: string;
  animeNameFilter: string;
  rankFilter: string;
  onNameFilterChange: (value: string) => void;
  onAnimeNameFilterChange: (value: string) => void;
  onRankFilterChange: (value: string) => void;
  onSearch: (e: React.FormEvent) => void;
}

const ShortFilter: React.FC<ShortFilterProps> = ({
  nameFilter,
  animeNameFilter,
  rankFilter,
  onNameFilterChange,
  onAnimeNameFilterChange,
  onRankFilterChange,
  onSearch
}) => {
  return (
    <div className="short-filter">
      <form onSubmit={onSearch} className="compact-form">
        <div className="filter-group">
          <input
            type="text"
            value={nameFilter}
            onChange={(e) => onNameFilterChange(e.target.value)}
            placeholder="Card name or ID"
            className="compact-input"
          />
          
          <input
            type="text"
            value={animeNameFilter}
            onChange={(e) => onAnimeNameFilterChange(e.target.value)}
            placeholder="Anime name"
            className="compact-input"
          />
          
          <select
            value={rankFilter}
            onChange={(e) => onRankFilterChange(e.target.value)}
            className="compact-select"
          >
            <option value="">All Ranks</option>
            <option value="ass">ASS</option>
            <option value="s">S</option>
            <option value="a">A</option>
            <option value="b">B</option>
            <option value="c">C</option>
            <option value="d">D</option>
            <option value="e">E</option>
          </select>
          
          <button type="submit" className="search-button">
            Search
          </button>
        </div>
      </form>
    </div>
  );
};

export default ShortFilter; 