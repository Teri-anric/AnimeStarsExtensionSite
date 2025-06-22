import React from 'react';
import '../styles/SortOptions.css';

export interface SortOption {
  value: string;
  label: string;
}

interface SortOptionsProps {
  options: SortOption[];
  currentValue: string;
  onChange: (value: string) => void;
  className?: string;
}

const SortOptions: React.FC<SortOptionsProps> = ({
  options,
  currentValue,
  onChange,
  className = ''
}) => {
  return (
    <div className={`sort-options ${className}`}>
      <label className="sort-label">
        Sort by:
        <select
          value={currentValue}
          onChange={(e) => onChange(e.target.value)}
          className="sort-select"
        >
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
};

export default SortOptions; 