import React, { useEffect, useRef } from 'react';
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
  const nameInputRef = useRef<HTMLInputElement>(null);
  const animeNameInputRef = useRef<HTMLInputElement>(null);

  const adjustInputWidth = (input: HTMLInputElement, value: string) => {
    // Create a temporary span to measure text width
    const span = document.createElement('span');
    span.style.visibility = 'hidden';
    span.style.position = 'absolute';
    span.style.fontSize = '14px';
    span.style.fontFamily = getComputedStyle(input).fontFamily;
    span.style.padding = '0 10px';
    span.textContent = value || input.placeholder;
    
    document.body.appendChild(span);
    const textWidth = span.offsetWidth;
    document.body.removeChild(span);
    
    // Set minimum width to 120px and add some padding
    const newWidth = Math.max(120, textWidth + 20);
    input.style.width = `${newWidth}px`;
  };

  useEffect(() => {
    if (nameInputRef.current) {
      adjustInputWidth(nameInputRef.current, nameFilter);
    }
  }, [nameFilter]);

  useEffect(() => {
    if (animeNameInputRef.current) {
      adjustInputWidth(animeNameInputRef.current, animeNameFilter);
    }
  }, [animeNameFilter]);
  return (
    <div className="short-filter">
      <form onSubmit={onSearch} className="compact-form">
        <div className="filter-group">
          <input
            type="text"
            value={nameFilter}
            onChange={(e) => {
              onNameFilterChange(e.target.value);
            }}
            placeholder="Card name or ID"
            className="compact-input"
            ref={nameInputRef}
          />
          
          <input
            type="text"
            value={animeNameFilter}
            onChange={(e) => {
              onAnimeNameFilterChange(e.target.value);
            }}
            placeholder="Anime name"
            className="compact-input"
            ref={animeNameInputRef}
          />
          
          <select
            value={rankFilter}
            onChange={(e) => {
              onRankFilterChange(e.target.value);
            }}
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