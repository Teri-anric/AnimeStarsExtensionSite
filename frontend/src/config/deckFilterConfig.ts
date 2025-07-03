import { EntityFilterConfig, GenericFilter } from '../types/filter';

export const deckFilterConfig: EntityFilterConfig = {
  entityName: 'Anime Decks',
  
  fieldOptions: [
    { value: 'anime_name', label: 'Anime Name', type: 'string' },
    { value: 'anime_link', label: 'Anime Link', type: 'string' },
    { value: 'card_count', label: 'Number of Cards', type: 'number' },
  ],

  shortFilterFields: [
    {
      key: 'query',
      type: 'text',
      placeholder: 'Anime name or link'
    }
  ],

  buildShortFilter: (values: Record<string, string>): GenericFilter | null => {
    const filters: GenericFilter[] = [];

    if (values.query && values.query.trim()) {
      filters.push({
        or: [
          { anime_name: { icontains: values.query.trim() } },
          { anime_link: { icontains: values.query.trim() } }
        ]
      });
    }

    if (filters.length === 0) {
      return null;
    }

    if (filters.length === 1) {
      return filters[0];
    }

    return { and: filters };
  },

  sortOptions: [
    { value: 'anime_name asc', label: 'Anime Name (A-Z)' },
    { value: 'anime_name desc', label: 'Anime Name (Z-A)' },
    { value: 'card_count desc', label: 'Most Cards' },
    { value: 'card_count asc', label: 'Least Cards' },
  ],

  defaults: {
    sort: 'anime_name asc',
    filterMode: 'short'
  },

  ui: {
    title: 'Anime Decks',
    showModeToggle: true,
    className: 'decks-filter'
  }
};

// Legacy exports for backward compatibility
export const deckFieldOptions = deckFilterConfig.fieldOptions;
export const deckShortFilterFields = deckFilterConfig.shortFilterFields;
export const deckSortOptions = deckFilterConfig.sortOptions; 