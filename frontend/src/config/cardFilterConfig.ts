import { FieldOption } from '../types/filter';

export const cardFieldOptions: FieldOption[] = [
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
]; 