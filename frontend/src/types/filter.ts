// Generic filter types for universal filtering system

export type FilterOperator = 
  // String operators
  | 'eq' | 'ne' | 'contains' | 'icontains' | 'not_contains' | 'is_null'
  // Number operators
  | 'in' | 'not_in'
  // Date operators
  | 'today' | 'yesterday' | 'this_week' | 'last_week' 
  | 'this_month' | 'last_month' | 'this_year' | 'last_year'
  | 'last_n_days' | 'older_than_days' | 'before' | 'after';

export type FieldType = 'string' | 'number' | 'enum' | 'datetime' | 'boolean';

export interface FieldOption {
  value: string;
  label: string;
  type: FieldType;
  enumOptions?: Array<{ value: string; label: string }>;
}

export interface FilterCondition {
  [operator: string]: any;
}

export interface GenericFilter {
  [field: string]: FilterCondition | GenericFilter | GenericFilter[] | undefined;
  and?: GenericFilter[];
  or?: GenericFilter[];
}

export interface FilterRule {
  id: string;
  field: string;
  operator: FilterOperator;
  value: string;
}

export interface FilterGroup {
  id: string;
  logicalOperator: 'and' | 'or';
  rules: FilterRule[];
}

export interface UniversalFilterProps<T = GenericFilter> {
  onFilterChange: (filter: T | null) => void;
  onClose: () => void;
  initialFilter?: T | null;
  fieldOptions: FieldOption[];
  title?: string;
}

// Extended configuration types
export interface ShortFilterField {
  key: string;
  type: 'text' | 'select';
  placeholder?: string;
  options?: Array<{ value: string; label: string }>;
}

export interface SortOption {
  value: string;
  label: string;
}

// Unified entity filter configuration
export interface EntityFilterConfig<T = GenericFilter> {
  // Basic entity information
  entityName: string;
  
  // Field options for advanced filter
  fieldOptions: FieldOption[];
  
  // Short filter configuration
  shortFilterFields: ShortFilterField[];
  
  // Custom filter building logic for short filters
  buildShortFilter?: (values: Record<string, string>) => T | null;
  
  // Sort options
  sortOptions: SortOption[];
  
  // Default values
  defaults: {
    sort: string;
    filterMode: 'short' | 'advanced';
    shortFilterValues?: Record<string, string>;
  };
  
  // Optional UI configuration
  ui?: {
    title?: string;
    showModeToggle?: boolean;
    className?: string;
  };
} 