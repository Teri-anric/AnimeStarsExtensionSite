import { FieldOption } from '../types/filter';

export const userFieldOptions: FieldOption[] = [
  { value: 'id', label: 'User ID', type: 'number' },
  { value: 'username', label: 'Username', type: 'string' },
  { value: 'email', label: 'Email', type: 'string' },
  { 
    value: 'is_active', 
    label: 'Is Active', 
    type: 'boolean'
  },
  { 
    value: 'role', 
    label: 'Role', 
    type: 'enum',
    enumOptions: [
      { value: 'admin', label: 'Administrator' },
      { value: 'user', label: 'Regular User' },
      { value: 'moderator', label: 'Moderator' }
    ]
  },
  { value: 'created_at', label: 'Registration Date', type: 'datetime' },
  { value: 'last_login', label: 'Last Login', type: 'datetime' }
]; 