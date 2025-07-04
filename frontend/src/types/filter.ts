// Generic filter types for universal filtering system

export type FilterOperator = 
  // String operators
  | 'eq' | 'ne' | 'contains' | 'icontains' | 'not_contains' | 'is_null'
  // Number operators
  | 'in' | 'not_in' | 'gt' | 'gte' | 'lt' | 'lte'
  // Date operators
  | 'today' | 'yesterday' | 'this_week' | 'last_week' 
  | 'this_month' | 'last_month' | 'this_year' | 'last_year'
  | 'last_n_days' | 'older_than_days' | 'before' | 'after'
  // Array/Collection operators
  | 'any' | 'all' | 'length';

export type FieldType = 'string' | 'number' | 'enum' | 'datetime' | 'boolean' | 'array';

export interface FieldOption {
  value: string;
  label: string;
  type: FieldType;
  enumOptions?: Array<{ value: string; label: string }>;
  // For array/collection fields
  subEntityConfig?: SubEntityConfig;
}

// Sub-entity configuration for array fields
export interface SubEntityConfig {
  entityName: string;
  fieldOptions: FieldOption[];
  // Operators supported for this array field
  supportedOperators?: ('any' | 'all' | 'length')[];
}

export interface FilterCondition {
  [operator: string]: any;
}

// Enhanced to support array filtering
export interface GenericFilter {
  [field: string]: FilterCondition | GenericFilter | GenericFilter[] | ArrayFilter | undefined;
  and?: GenericFilter[];
  or?: GenericFilter[];
}

// Array filter structure matching backend ArrayEntryFilter
export interface ArrayFilter {
  any?: GenericFilter;
  all?: GenericFilter;
  length?: FilterCondition;
}

export interface FilterRule {
  id: string;
  field: string;
  operator: FilterOperator;
  value: string;
  // For array field rules
  subEntity?: string; // field path within sub-entity (e.g., "cards.name")
  subEntityOperator?: FilterOperator; // operator for sub-entity field
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