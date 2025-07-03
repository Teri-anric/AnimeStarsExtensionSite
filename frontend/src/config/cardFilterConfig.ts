import { EntityFilterConfig, GenericFilter } from '../types/filter';

// Card filter configuration with custom filter building logic
export const cardFilterConfig: EntityFilterConfig = {
  entityName: 'Cards',
  
  fieldOptions: [
    { value: 'name', label: 'Card Name', type: 'string' },
    { value: 'card_id', label: 'Card ID', type: 'number' },
    { 
      value: 'rank', 
      label: 'Rank', 
      type: 'enum',
      enumOptions: [
        { value: 'ass', label: 'ASS' },
        { value: 's', label: 'S' },
        { value: 'a', label: 'A' },
        { value: 'b', label: 'B' },
        { value: 'c', label: 'C' },
        { value: 'd', label: 'D' },
        { value: 'e', label: 'E' }
      ]
    },
    { value: 'anime_name', label: 'Anime Name', type: 'string' },
    { value: 'anime_link', label: 'Anime Link', type: 'string' },
    { value: 'author', label: 'Author', type: 'string' },
    { value: 'image', label: 'Image Path', type: 'string' },
    { value: 'mp4', label: 'MP4 Path', type: 'string' },
    { value: 'webm', label: 'WebM Path', type: 'string' },
    { value: 'created_at', label: 'Created Date', type: 'datetime' },
    { value: 'updated_at', label: 'Updated Date', type: 'datetime' }
  ],

  shortFilterFields: [
    {
      key: 'name',
      type: 'text',
      placeholder: 'Card name or ID'
    },
    {
      key: 'anime_name',
      type: 'text',
      placeholder: 'Anime name'
    },
    {
      key: 'rank',
      type: 'select',
      placeholder: 'All Ranks',
      options: [
        { value: 'ass', label: 'ASS' },
        { value: 's', label: 'S' },
        { value: 'a', label: 'A' },
        { value: 'b', label: 'B' },
        { value: 'c', label: 'C' },
        { value: 'd', label: 'D' },
        { value: 'e', label: 'E' }
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
  ],

  defaults: {
    sort: 'created_at desc',
    filterMode: 'short'
  },

  ui: {
    title: 'Cards',
    showModeToggle: true,
    className: 'cards-filter'
  }
};

// Legacy exports for backward compatibility
export const cardFieldOptions = cardFilterConfig.fieldOptions;
export const cardShortFilterFields = cardFilterConfig.shortFilterFields;
export const cardSortOptions = cardFilterConfig.sortOptions; 