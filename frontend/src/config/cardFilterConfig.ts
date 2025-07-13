import { EntityFilterConfig, GenericFilter } from '../types/filter';

// Card filter configuration with custom filter building logic
export const cardFilterConfig: EntityFilterConfig = {
  entityName: 'Cards',
  
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
    { value: 'anime_name', label: 'filterConfig.animeName', type: 'string' },
    { value: 'anime_link', label: 'filterConfig.animeLink', type: 'string' },
    { value: 'author', label: 'filterConfig.author', type: 'string' },
    { value: 'image', label: 'filterConfig.imagePath', type: 'string' },
    { value: 'mp4', label: 'filterConfig.mp4Path', type: 'string' },
    { value: 'webm', label: 'filterConfig.webmPath', type: 'string' },
    { value: 'created_at', label: 'filterConfig.createdDate', type: 'datetime' },
    { value: 'updated_at', label: 'filterConfig.updatedDate', type: 'datetime' },
    { value: 'stats_count', label: 'filterConfig.statsCount', type: 'number' }
  ],

  shortFilterFields: [
    {
      key: 'name',
      type: 'text',
      placeholder: 'filterConfig.cardNameOrId'
    },
    {
      key: 'anime_name',
      type: 'text',
      placeholder: 'filterConfig.animeNamePlaceholder'
    },
    {
      key: 'rank',
      type: 'select',
      placeholder: 'filterConfig.allRanks',
      options: [
        { value: 'ass', label: 'ranks.ass' },
        { value: 's', label: 'ranks.s' },
        { value: 'a', label: 'ranks.a' },
        { value: 'b', label: 'ranks.b' },
        { value: 'c', label: 'ranks.c' },
        { value: 'd', label: 'ranks.d' },
        { value: 'e', label: 'ranks.e' }
      ]
    }
  ],

  // Custom filter building logic for cards
  buildShortFilter: (values: Record<string, string>): GenericFilter | null => {
    const filters: GenericFilter[] = [];

    // Handle name filter (can be card name or ID)
    if (values.name && values.name.trim()) {
      const nameFilterConditions: GenericFilter[] = [
        {
          name: {
            icontains: values.name.trim()
          }
        }
      ];
      
      // Only add card_id filter if nameFilter is a valid number
      const cardIdNumber = parseInt(values.name.trim());
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

    // Handle anime name filter (searches both anime_name and anime_link)
    if (values.anime_name && values.anime_name.trim()) {
      filters.push({
        or: [
          {
            anime_name: {
              icontains: values.anime_name.trim()
            }
          },
          {
            anime_link: {
              icontains: values.anime_name.trim()
            }
          }
        ]
      });
    }

    // Handle rank filter
    if (values.rank && values.rank.trim()) {
      filters.push({
        rank: {
          eq: values.rank.trim()
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
  },

  sortOptions: [
    { value: "card_id asc", label: 'filterConfig.cardIdAscending' },
    { value: "card_id desc", label: 'filterConfig.cardIdDescending' },
    { value: "name asc", label: 'filterConfig.nameAZ' },
    { value: "name desc", label: 'filterConfig.nameZA' },
    { value: "rank asc", label: 'filterConfig.rankLowToHigh' },
    { value: "rank desc", label: 'filterConfig.rankHighToLow' },
    { value: "anime_name asc", label: 'filterConfig.animeNameAZ' },
    { value: "anime_name desc", label: 'filterConfig.animeNameZA' },
    { value: 'created_at desc', label: 'filterConfig.newestFirst' },
    { value: 'created_at asc', label: 'filterConfig.oldestFirst' },
    { value: 'updated_at desc', label: 'filterConfig.recentlyUpdated' },
    { value: 'updated_at asc', label: 'filterConfig.leastRecentlyUpdated' },
  ],

  defaults: {
    sort: 'created_at desc',
    filterMode: 'short'
  },

  ui: {
    title: 'cards.title',
    showModeToggle: true,
    className: 'cards-filter'
  }
};

// Legacy exports for backward compatibility
export const cardFieldOptions = cardFilterConfig.fieldOptions;
export const cardShortFilterFields = cardFilterConfig.shortFilterFields;
export const cardSortOptions = cardFilterConfig.sortOptions; 