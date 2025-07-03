import React from 'react';
import { CardFilter } from '../client';
import AdvancedFilter from './AdvancedFilter';
import { cardFieldOptions } from '../config/cardFilterConfig';

interface AdvancedFilterProps {
  onFilterChange: (filter: CardFilter | null) => void;
  onClose: () => void;
  initialFilter?: CardFilter | null;
}

const CardAdvancedFilter: React.FC<AdvancedFilterProps> = ({ onFilterChange, onClose, initialFilter }) => {
  const handleFilterChange = (filter: any) => {
    onFilterChange(filter as CardFilter | null);
  };

  return (
    <AdvancedFilter
      onFilterChange={handleFilterChange}
      onClose={onClose}
      initialFilter={initialFilter as any}
      fieldOptions={cardFieldOptions}
      title="Advanced Card Filter"
    />
  );
};

export default CardAdvancedFilter;