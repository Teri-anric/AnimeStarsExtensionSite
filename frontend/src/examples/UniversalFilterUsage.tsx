// Example usage of UniversalFilter component with different entity types

import React, { useState } from 'react';
import AdvancedFilter from '../components/AdvancedFilter';
import { GenericFilter } from '../types/filter';
import { cardFieldOptions } from '../config/cardFilterConfig';
import { userFieldOptions } from '../config/userFilterConfig';
import { deckFieldOptions } from '../config/deckFilterConfig';

// Example 1: Using UniversalFilter for Cards
export const CardFilterExample: React.FC = () => {
  const [filter, setFilter] = useState<GenericFilter | null>(null);
  const [showFilter, setShowFilter] = useState(false);

  const handleFilterChange = (newFilter: GenericFilter | null) => {
    setFilter(newFilter);
    console.log('Card filter applied:', newFilter);
    // Here you would typically call your API with the filter
    // fetchCards({ filter: newFilter });
  };

  return (
    <div>
      <button onClick={() => setShowFilter(true)}>
        Open Card Filter
      </button>
      
      {showFilter && (
        <AdvancedFilter
          onFilterChange={handleFilterChange}
          onClose={() => setShowFilter(false)}
          fieldOptions={cardFieldOptions}
          title="Filter Cards"
          initialFilter={filter}
        />
      )}
    </div>
  );
};

// Example 2: Using UniversalFilter for Users
export const UserFilterExample: React.FC = () => {
  const [filter, setFilter] = useState<GenericFilter | null>(null);
  const [showFilter, setShowFilter] = useState(false);

  const handleFilterChange = (newFilter: GenericFilter | null) => {
    setFilter(newFilter);
    console.log('User filter applied:', newFilter);
    // fetchUsers({ filter: newFilter });
  };

  return (
    <div>
      <button onClick={() => setShowFilter(true)}>
        Open User Filter
      </button>
      
      {showFilter && (
        <AdvancedFilter
          onFilterChange={handleFilterChange}
          onClose={() => setShowFilter(false)}
          fieldOptions={userFieldOptions}
          title="Filter Users"
          initialFilter={filter}
        />
      )}
    </div>
  );
};

// Example 3: Using UniversalFilter for Decks
export const DeckFilterExample: React.FC = () => {
  const [filter, setFilter] = useState<GenericFilter | null>(null);
  const [showFilter, setShowFilter] = useState(false);

  const handleFilterChange = (newFilter: GenericFilter | null) => {
    setFilter(newFilter);
    console.log('Deck filter applied:', newFilter);
    // fetchDecks({ filter: newFilter });
  };

  return (
    <div>
      <button onClick={() => setShowFilter(true)}>
        Open Deck Filter
      </button>
      
      {showFilter && (
        <AdvancedFilter
          onFilterChange={handleFilterChange}
          onClose={() => setShowFilter(false)}
          fieldOptions={deckFieldOptions}
          title="Filter Decks"
          initialFilter={filter}
        />
      )}
    </div>
  );
};

// Example 4: Custom Entity Filter Configuration
// You can easily create filters for any entity by defining the field options

import { FieldOption } from '../types/filter';

const customEntityFieldOptions: FieldOption[] = [
  { value: 'title', label: 'Title', type: 'string' },
  { value: 'priority', label: 'Priority', type: 'enum', enumOptions: [
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' }
  ]},
  { value: 'is_completed', label: 'Completed', type: 'boolean' },
  { value: 'due_date', label: 'Due Date', type: 'datetime' },
];

export const CustomEntityFilterExample: React.FC = () => {
  const [filter, setFilter] = useState<GenericFilter | null>(null);
  const [showFilter, setShowFilter] = useState(false);

  const handleFilterChange = (newFilter: GenericFilter | null) => {
    setFilter(newFilter);
    console.log('Custom entity filter applied:', newFilter);
  };

  return (
    <div>
      <button onClick={() => setShowFilter(true)}>
        Open Custom Entity Filter
      </button>
      
      {showFilter && (
        <AdvancedFilter
          onFilterChange={handleFilterChange}
          onClose={() => setShowFilter(false)}
          fieldOptions={customEntityFieldOptions}
          title="Filter Custom Entity"
          initialFilter={filter}
        />
      )}
    </div>
  );
};

/*
Usage Guidelines:

1. **Define Field Options**: Create an array of FieldOption objects that describe your entity's filterable fields
2. **Import UniversalFilter**: Use the generic UniversalFilter component
3. **Configure Props**: Pass your field options and other required props
4. **Handle Filter Changes**: Implement the onFilterChange callback to process filters

Benefits of this approach:
- ✅ Reusable across all entity types
- ✅ Consistent UI/UX for all filters
- ✅ Type-safe with proper TypeScript support
- ✅ Easy to maintain and extend
- ✅ No hardcoded entity-specific logic in the filter component
- ✅ Supports all field types: string, number, enum, datetime, boolean
- ✅ Configurable enum options per field
- ✅ Flexible operator support based on field types

Example Filter Output:
{
  "and": [
    {
      "name": { "icontains": "anime" }
    },
    {
      "or": [
        { "rank": { "eq": "s" } },
        { "rank": { "eq": "a" } }
      ]
    }
  ]
}
*/ 