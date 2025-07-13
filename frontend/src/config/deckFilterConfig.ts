import { EntityFilterConfig, GenericFilter } from '../types/filter';

export const deckFilterConfig: EntityFilterConfig = {
  entityName: 'Anime Decks',
  
  fieldOptions: [
    { value: 'anime_name', label: 'filterConfig.animeName', type: 'string' },
    { value: 'anime_link', label: 'filterConfig.animeLink', type: 'string' },
    { value: 'card_count', label: 'filterConfig.numberOfCards', type: 'number' },
    { 
      value: 'cards', 
      label: 'filterConfig.cards', 
      type: 'array',
      subEntityConfig: {
        entityName: 'Cards',
        supportedOperators: ['any', 'all', 'length'],
        fieldOptions: [
          { value: 'name', label: 'filterConfig.cardName', type: 'string' },
          { value: 'card_id', label: 'filterConfig.cardId', type: 'number' },
          { 
            value: 'rank', 
            label: 'filterConfig.rank', 
            type: 'enum',
            enumOptions: [
              { value: 'ass', label: 'ranks.ass' },
              { value: 's', label: 'ranks.s' },
              { value: 'a', label: 'ranks.a' },
              { value: 'b', label: 'ranks.b' },
              { value: 'c', label: 'ranks.c' },
              { value: 'd', label: 'ranks.d' },
              { value: 'e', label: 'ranks.e' }
            ]
          },
          { value: 'anime_name', label: 'filterConfig.cardAnimeName', type: 'string' },
          { value: 'anime_link', label: 'filterConfig.cardAnimeLink', type: 'string' },
          { value: 'author', label: 'filterConfig.cardAuthor', type: 'string' },
          { value: 'created_at', label: 'filterConfig.cardCreatedDate', type: 'datetime' },
          { value: 'updated_at', label: 'filterConfig.cardUpdatedDate', type: 'datetime' }
        ]
      }
    }
  ],

  shortFilterFields: [
    {
      key: 'query',
      type: 'text',
      placeholder: 'filterConfig.animeNameOrLink'
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
    { value: 'anime_name asc', label: 'filterConfig.animeNameAZ' },
    { value: 'anime_name desc', label: 'filterConfig.animeNameZA' },
    { value: 'card_count desc', label: 'filterConfig.mostCards' },
    { value: 'card_count asc', label: 'filterConfig.leastCards' },
  ],

  defaults: {
    sort: 'anime_name asc',
    filterMode: 'short'
  },

  ui: {
    title: 'decks.title',
    showModeToggle: true,
    className: 'decks-filter'
  }
};

// Legacy exports for backward compatibility
export const deckFieldOptions = deckFilterConfig.fieldOptions;
export const deckShortFilterFields = deckFilterConfig.shortFilterFields;
export const deckSortOptions = deckFilterConfig.sortOptions; 