import { FieldOption } from '../types/filter';

export const userFieldOptions: FieldOption[] = [
  { value: 'id', label: 'filterConfig.userId', type: 'number' },
  { value: 'username', label: 'filterConfig.username', type: 'string' },
  { value: 'email', label: 'filterConfig.email', type: 'string' },
  { 
    value: 'is_active', 
    label: 'filterConfig.isActive', 
    type: 'boolean'
  },
  { 
    value: 'role', 
    label: 'filterConfig.role', 
    type: 'enum',
    enumOptions: [
      { value: 'admin', label: 'filterConfig.administrator' },
      { value: 'user', label: 'filterConfig.regularUser' },
      { value: 'moderator', label: 'filterConfig.moderator' }
    ]
  },
  { value: 'created_at', label: 'filterConfig.registrationDate', type: 'datetime' },
  { value: 'last_login', label: 'filterConfig.lastLogin', type: 'datetime' }
]; 