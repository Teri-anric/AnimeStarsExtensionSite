import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  GenericFilter, 
  FilterRule, 
  FilterGroup, 
  UniversalFilterProps, 
  FieldOption,
  FilterOperator,
  FieldType 
} from '../types/filter';
import '../styles/AdvancedFilter.css';

const stringOperators = [
  { value: 'eq', label: '=' },
  { value: 'ne', label: '!=' },
  { value: 'contains', label: 'Contains' },
  { value: 'icontains', label: 'Contains (case insensitive)' },
  { value: 'not_contains', label: 'Does not contain' },
  { value: 'is_null', label: 'Is empty' }
];

const numberOperators = [
  { value: 'eq', label: '=' },
  { value: 'ne', label: '!=' },
  { value: 'in', label: 'In list' },
  { value: 'not_in', label: 'Not in list' },
  { value: 'is_null', label: 'Is empty' },
  { value: 'gt', label: '>' },
  { value: 'gte', label: '>=' },
  { value: 'lt', label: '<' },
  { value: 'lte', label: '<=' }
];

const enumOperators = [
  { value: 'eq', label: '=' },
  { value: 'ne', label: '!=' },
  { value: 'in', label: 'In list' },
  { value: 'not_in', label: 'Not in list' },
  { value: 'is_null', label: 'Is empty' }
];

const datetimeOperators = [
  { value: 'today', label: 'Today' },
  { value: 'yesterday', label: 'Yesterday' },
  { value: 'this_week', label: 'This week' },
  { value: 'last_week', label: 'Last week' },
  { value: 'this_month', label: 'This month' },
  { value: 'last_month', label: 'Last month' },
  { value: 'this_year', label: 'This year' },
  { value: 'last_year', label: 'Last year' },
  { value: 'last_n_days', label: 'Last N days' },
  { value: 'older_than_days', label: 'Older than N days' },
  { value: 'before', label: 'Before date' },
  { value: 'after', label: 'After date' },
  { value: 'eq', label: 'Exact date' },
  { value: 'is_null', label: 'Is empty' }
];

const booleanOperators = [
  { value: 'eq', label: 'is' },
  { value: 'ne', label: 'is not' },
  { value: 'is_null', label: 'Is empty' }
];

const arrayOperators = [
  { value: 'any', label: 'Has any item that' },
  { value: 'all', label: 'All items must' },
  { value: 'length', label: 'Number of items' }
];

const parseFilterToGroups = (filter: GenericFilter, fieldOptions: FieldOption[]): FilterGroup[] => {
  console.log('Parsing filter to groups:', filter);
  console.log('Available field options:', fieldOptions.map(f => f.value));
  const groups: FilterGroup[] = [];
  let groupId = 1;
  let ruleId = 1;

  const parseFieldFilter = (fieldName: string, fieldFilter: any): FilterRule => {
    const operators = Object.keys(fieldFilter);
    const operator = operators[0] as FilterOperator;
    const value = fieldFilter[operator];
    
    const fieldType = fieldOptions.find(f => f.value === fieldName)?.type || 'string';
    
    // Handle array field sub-entity filters
    if (fieldType === 'array' && (operator === 'any' || operator === 'all')) {
      if (typeof value === 'object' && value !== null) {
        // Extract sub-entity information
        const subEntityFields = Object.keys(value);
        if (subEntityFields.length > 0) {
          const subEntity = subEntityFields[0];
          const subEntityFilter = value[subEntity];
          const subEntityOperators = Object.keys(subEntityFilter);
          
          if (subEntityOperators.length > 0) {
            const subEntityOperator = subEntityOperators[0];
            const subEntityValue = subEntityFilter[subEntityOperator];
            
            let ruleValue = '';
            if (subEntityOperator === 'in' || subEntityOperator === 'not_in') {
              ruleValue = Array.isArray(subEntityValue) ? subEntityValue.join(', ') : String(subEntityValue);
            } else {
              ruleValue = String(subEntityValue);
            }
            
            return {
              id: (ruleId++).toString(),
              field: fieldName,
              operator,
              value: ruleValue,
              subEntity,
              subEntityOperator: subEntityOperator as FilterOperator
            };
          }
        }
      }
      
      // Fallback for malformed sub-entity filter
      return {
        id: (ruleId++).toString(),
        field: fieldName,
        operator,
        value: '',
        subEntity: undefined,
        subEntityOperator: undefined
      };
    }
    
    // Handle array length operator
    if (fieldType === 'array' && operator === 'length') {
      const lengthValue = typeof value === 'object' && value.eq !== undefined ? value.eq : value;
      return {
        id: (ruleId++).toString(),
        field: fieldName,
        operator,
        value: String(lengthValue)
      };
    }
    
    // Handle regular field filters
    let ruleValue = '';
    if (operator === 'is_null' && value === true) {
      ruleValue = '';
    } else if (operator === 'in' || operator === 'not_in') {
      ruleValue = Array.isArray(value) ? value.join(', ') : String(value);
    } else {
      ruleValue = String(value);
    }

    return {
      id: (ruleId++).toString(),
      field: fieldName,
      operator,
      value: ruleValue
    };
  };

  const parseSubFilter = (subFilter: GenericFilter): FilterGroup | null => {
    console.log('Parsing subFilter:', subFilter);
    const rules: FilterRule[] = [];
    let groupOperator: 'and' | 'or' = 'and';

    // Check if this subfilter has and/or operators
    if (subFilter.and && Array.isArray(subFilter.and)) {
      console.log('Found AND operation with', subFilter.and.length, 'items');
      groupOperator = 'and';
      subFilter.and.forEach(item => {
        Object.entries(item).forEach(([key, value]) => {
          console.log('Processing AND item:', key, value);
          if (fieldOptions.some(f => f.value === key)) {
            rules.push(parseFieldFilter(key, value));
          } else {
            console.log('Field not found in options:', key);
          }
        });
      });
    } else if (subFilter.or && Array.isArray(subFilter.or)) {
      console.log('Found OR operation with', subFilter.or.length, 'items');
      groupOperator = 'or';
      subFilter.or.forEach(item => {
        Object.entries(item).forEach(([key, value]) => {
          console.log('Processing OR item:', key, value);
          if (fieldOptions.some(f => f.value === key)) {
            rules.push(parseFieldFilter(key, value));
          } else {
            console.log('Field not found in options:', key);
          }
        });
      });
    } else {
      // Single field filter
      console.log('Processing single field filter');
      Object.entries(subFilter).forEach(([key, value]) => {
        console.log('Processing field:', key, value);
        if (fieldOptions.some(f => f.value === key)) {
          rules.push(parseFieldFilter(key, value));
        } else {
          console.log('Field not found in options:', key);
        }
      });
    }

    if (rules.length > 0) {
      return {
        id: (groupId++).toString(),
        logicalOperator: groupOperator,
        rules
      };
    }

    return null;
  };

  const processFilter = (currentFilter: GenericFilter): void => {
    if (currentFilter.and && Array.isArray(currentFilter.and)) {
      // Create separate groups for each item in the AND array
      currentFilter.and.forEach(subFilter => {
        const group = parseSubFilter(subFilter);
        if (group) {
          groups.push(group);
        }
      });
    } else if (currentFilter.or && Array.isArray(currentFilter.or)) {
      // Create separate groups for each item in the OR array  
      currentFilter.or.forEach(subFilter => {
        const group = parseSubFilter(subFilter);
        if (group) {
          groups.push(group);
        }
      });
    } else {
      // Single level filter - create one group
      const group = parseSubFilter(currentFilter);
      if (group) {
        groups.push(group);
      }
    }
  };

  processFilter(filter);

  return groups.length > 0 ? groups : [{
    id: '1',
    logicalOperator: 'and',
    rules: []
  }];
};

const AdvancedFilter: React.FC<UniversalFilterProps> = ({ 
  onFilterChange, 
  onClose, 
  initialFilter, 
  fieldOptions,
  title
}) => {
  const { t } = useTranslation();
  const defaultTitle = t('advancedFilter.title');

  // Function to translate labels
  const translateLabel = (label: string): string => {
    if (label.startsWith('filterConfig.') || label.startsWith('cards.') || label.startsWith('decks.') || label.startsWith('ranks.')) {
      return t(label);
    }
    return label;
  };
  const [groups, setGroups] = useState<FilterGroup[]>(() => {
    if (initialFilter) {
      return parseFilterToGroups(initialFilter, fieldOptions);
    }
    return [{
      id: '1',
      logicalOperator: 'and',
      rules: []
    }];
  });

  // Update groups when initialFilter changes (for URL parameters)
  useEffect(() => {
    if (initialFilter) {
      console.log('AdvancedFilter: initialFilter changed, updating groups:', initialFilter);
      const newGroups = parseFilterToGroups(initialFilter, fieldOptions);
      setGroups(newGroups);
    }
  }, [initialFilter, fieldOptions]);

  const addGroup = () => {
    const newGroup: FilterGroup = {
      id: Date.now().toString(),
      logicalOperator: 'and',
      rules: []
    };
    setGroups([...groups, newGroup]);
  };

  const removeGroup = (groupId: string) => {
    if (groups.length > 1) {
      setGroups(groups.filter(group => group.id !== groupId));
    }
  };

  const updateGroupOperator = (groupId: string, operator: 'and' | 'or') => {
    setGroups(groups.map(group => 
      group.id === groupId 
        ? { ...group, logicalOperator: operator }
        : group
    ));
  };

  const addRule = (groupId: string) => {
    const firstField = fieldOptions[0];
    const newRule: FilterRule = {
      id: Date.now().toString(),
      field: firstField?.value || '',
      operator: firstField?.type === 'string' ? 'icontains' : 
                firstField?.type === 'array' ? 'any' : 'eq',
      value: '',
      subEntity: undefined
    };
    
    setGroups(groups.map(group => 
      group.id === groupId 
        ? { ...group, rules: [...group.rules, newRule] }
        : group
    ));
  };

  const removeRule = (groupId: string, ruleId: string) => {
    setGroups(groups.map(group => {
      if (group.id === groupId) {
        const updatedRules = group.rules.filter(rule => rule.id !== ruleId);
        return { ...group, rules: updatedRules };
      }
      return group;
    }));
  };

  const updateRule = (groupId: string, ruleId: string, field: keyof FilterRule, value: string) => {
    setGroups(groups.map(group => {
      if (group.id === groupId) {
        const updatedRules = group.rules.map(rule => {
          if (rule.id === ruleId) {
            const updatedRule = { ...rule, [field]: value };
            
            // If field is changed, set appropriate operator based on field type
            if (field === 'field') {
              const fieldType = getFieldType(value);
              if (fieldType === 'string' && !['eq', 'ne', 'contains', 'icontains', 'not_contains', 'is_null'].includes(rule.operator)) {
                updatedRule.operator = 'icontains';
              } else if (fieldType === 'enum' && !['eq', 'ne', 'in', 'not_in', 'is_null'].includes(rule.operator)) {
                updatedRule.operator = 'eq';
              } else if (fieldType === 'number' && !['eq', 'ne', 'in', 'not_in', 'is_null'].includes(rule.operator)) {
                updatedRule.operator = 'eq';
              } else if (fieldType === 'boolean' && !['eq', 'is_null'].includes(rule.operator)) {
                updatedRule.operator = 'eq';
              } else if (fieldType === 'array' && !['any', 'all', 'length'].includes(rule.operator)) {
                updatedRule.operator = 'any';
                updatedRule.subEntity = undefined;
                updatedRule.value = '';
              }
              
              // Clear subEntity if changing away from array field
              if (fieldType !== 'array' && rule.subEntity) {
                updatedRule.subEntity = undefined;
              }
            }
            
            // If subEntity field is changed, clear the value
            if (field === 'subEntity') {
              updatedRule.value = '';
            }
            
            return updatedRule;
          }
          return rule;
        });
        return { ...group, rules: updatedRules };
      }
      return group;
    }));
  };

  const getOperatorsForField = (fieldType: FieldType) => {
    switch (fieldType) {
      case 'string':
        return stringOperators;
      case 'number':
        return numberOperators;
      case 'enum':
        return enumOperators;
      case 'datetime':
        return datetimeOperators;
      case 'boolean':
        return booleanOperators;
      case 'array':
        return arrayOperators;
      default:
        return stringOperators;
    }
  };

  const getFieldType = (fieldName: string): FieldType => {
    const field = fieldOptions.find(f => f.value === fieldName);
    return field?.type || 'string';
  };

  const getFieldEnumOptions = (fieldName: string) => {
    const field = fieldOptions.find(f => f.value === fieldName);
    return field?.enumOptions || [];
  };

  const getSubEntityConfig = (fieldName: string) => {
    const field = fieldOptions.find(f => f.value === fieldName);
    return field?.subEntityConfig;
  };

  const getDefaultOperatorForSubField = (fieldType: FieldType): FilterOperator => {
    switch (fieldType) {
      case 'string':
        return 'icontains';
      case 'enum':
        return 'eq';
      case 'number':
        return 'eq';
      case 'boolean':
        return 'eq';
      case 'datetime':
        return 'eq';
      default:
        return 'eq';
    }
  };

  const buildFilter = (): GenericFilter | null => {
    const validGroups = groups.map(group => ({
      ...group,
      rules: group.rules.filter(rule => rule.value.trim() !== '' || rule.operator === 'is_null')
    })).filter(group => group.rules.length > 0);
    
    if (validGroups.length === 0) {
      return null;
    }

    const buildFieldFilter = (rule: FilterRule): Partial<GenericFilter> => {
      const fieldType = getFieldType(rule.field);
      let filterValue: any;

      if (rule.operator === 'is_null') {
        filterValue = { is_null: true };
      } else if (fieldType === 'array') {
        // Handle array operators
        if (rule.operator === 'length') {
          const numValue = parseInt(rule.value);
          if (isNaN(numValue)) {
            return {}; // Skip invalid number
          }
          filterValue = { length: { eq: numValue } };
        } else if (rule.operator === 'any' || rule.operator === 'all') {
          // Handle sub-entity filters with proper operator selection
          if (rule.subEntity && rule.value) {
            const subEntityConfig = getSubEntityConfig(rule.field);
            const subFieldConfig = subEntityConfig?.fieldOptions.find(f => f.value === rule.subEntity);
            
            // Use explicit operator or fall back to default
            const operator = rule.subEntityOperator || getDefaultOperatorForSubField(subFieldConfig?.type || 'string');
            
            // Process value based on operator and field type
            let processedValue: any = rule.value;
            
            if (operator === 'in' || operator === 'not_in') {
              const values = rule.value.split(',').map(v => v.trim()).filter(v => v !== '');
              if (values.length === 0) {
                return {}; // Skip empty lists
              }
              if (subFieldConfig?.type === 'number') {
                const numValues = values.map(v => parseInt(v)).filter(v => !isNaN(v));
                if (numValues.length === 0) {
                  return {}; // Skip if no valid numbers
                }
                processedValue = numValues;
              } else {
                processedValue = values;
              }
            } else if (subFieldConfig?.type === 'number') {
              const numValue = parseInt(rule.value);
              if (isNaN(numValue)) {
                return {}; // Skip invalid number
              }
              processedValue = numValue;
            } else if (subFieldConfig?.type === 'boolean') {
              processedValue = rule.value.toLowerCase() === 'true';
            }
            
            filterValue = {
              [rule.operator]: {
                [rule.subEntity]: { [operator]: processedValue }
              }
            };
          } else {
            return {}; // Skip invalid sub-entity filter
          }
        }
      } else if (rule.operator === 'in' || rule.operator === 'not_in') {
        const values = rule.value.split(',').map(v => v.trim()).filter(v => v !== '');
        if (values.length === 0) {
          return {}; // Skip empty lists
        }
        if (fieldType === 'number') {
          const numValues = values.map(v => parseInt(v)).filter(v => !isNaN(v));
          if (numValues.length === 0) {
            return {}; // Skip if no valid numbers
          }
          filterValue = { [rule.operator]: numValues };
        } else {
          filterValue = { [rule.operator]: values };
        }
      } else {
        if (fieldType === 'number') {
          const numValue = parseInt(rule.value);
          if (isNaN(numValue)) {
            return {}; // Skip invalid number
          }
          filterValue = { [rule.operator]: numValue };
        } else if (fieldType === 'boolean') {
          const boolValue = rule.value.toLowerCase() === 'true';
          filterValue = { [rule.operator]: boolValue };
        } else {
          filterValue = { [rule.operator]: rule.value };
        }
      }

      return { [rule.field]: filterValue };
    };

    const buildGroupFilter = (group: FilterGroup): GenericFilter | null => {
      const validRules = group.rules.filter(rule => rule.value.trim() !== '' || rule.operator === 'is_null');
      if (validRules.length === 0) {
        return null;
      }

      const ruleFilters = validRules.map(rule => buildFieldFilter(rule) as GenericFilter);
      
      // Always wrap in and/or operator, even for single rules
      return { [group.logicalOperator]: ruleFilters };
    };

    if (validGroups.length === 1) {
      return buildGroupFilter(validGroups[0]);
    }

    // Multiple groups - combine with AND logic between groups
    const groupFilters = validGroups.map(group => buildGroupFilter(group)).filter(Boolean) as GenericFilter[];
    
    if (groupFilters.length === 1) {
      return groupFilters[0];
    }

    return { and: groupFilters };
  };

  const applyFilter = () => {
    const filter = buildFilter();
    console.log('Universal filter applying:', JSON.stringify(filter, null, 2));
    console.log('Current groups:', JSON.stringify(groups, null, 2));
    onFilterChange(filter);
  };

  const clearFilter = () => {
    setGroups([{
      id: '1',
      logicalOperator: 'and',
      rules: []
    }]);
    onFilterChange(null);
  };

  const renderValueInput = (groupId: string, rule: FilterRule) => {
    const fieldType = getFieldType(rule.field);
    
    if (rule.operator === 'is_null') {
      return <span className="null-indicator">{t('advancedFilter.noValueNeeded')}</span>;
    }

    // Array field handling
    if (fieldType === 'array') {
      if (rule.operator === 'length') {
        return (
          <input
            type="number"
            value={rule.value}
            onChange={(e) => updateRule(groupId, rule.id, 'value', e.target.value)}
            placeholder={t('advancedFilter.numberOfItems')}
            className="filter-input"
            min="0"
          />
        );
      } else if (rule.operator === 'any' || rule.operator === 'all') {
        const subEntityConfig = getSubEntityConfig(rule.field);
        if (!subEntityConfig) {
          return <span className="null-indicator">{t('advancedFilter.noSubEntityConfig')}</span>;
        }

        // Get the selected sub-entity field info
        const selectedSubField = rule.subEntity ? 
          subEntityConfig.fieldOptions.find(f => f.value === rule.subEntity) : null;

        return (
          <div className="sub-entity-filter">
            <select
              value={rule.subEntity || ''}
              onChange={(e) => updateRule(groupId, rule.id, 'subEntity', e.target.value)}
              className="filter-input sub-entity-field"
            >
              <option value="">{t('advancedFilter.selectField')}</option>
              {subEntityConfig.fieldOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            
            {/* Sub-entity operator selection */}
            {rule.subEntity && selectedSubField && (
              <select
                value={rule.subEntityOperator || getDefaultOperatorForSubField(selectedSubField.type)}
                onChange={(e) => updateRule(groupId, rule.id, 'subEntityOperator', e.target.value)}
                className="filter-input sub-entity-operator"
              >
                {getOperatorsForField(selectedSubField.type).map(op => (
                  <option key={op.value} value={op.value}>
                    {op.label}
                  </option>
                ))}
              </select>
            )}
            
            {/* Render appropriate input based on sub-entity field type */}
            {rule.subEntity && selectedSubField && (
              selectedSubField.type === 'enum' && 
              (rule.subEntityOperator === 'eq' || rule.subEntityOperator === 'ne' || !rule.subEntityOperator) ? (
                <select
                  value={rule.value}
                  onChange={(e) => updateRule(groupId, rule.id, 'value', e.target.value)}
                  className="filter-input sub-entity-value"
                >
                  <option value="">{t('advancedFilter.selectValue')}</option>
                  {selectedSubField.enumOptions?.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  type={selectedSubField.type === 'number' ? 'number' : 'text'}
                  value={rule.value}
                  onChange={(e) => updateRule(groupId, rule.id, 'value', e.target.value)}
                  placeholder={
                    rule.subEntityOperator === 'in' || rule.subEntityOperator === 'not_in' 
                      ? 'value1,value2,value3'
                      : t('advancedFilter.enterValue')
                  }
                  className="filter-input sub-entity-value"
                />
              )
            )}
          </div>
        );
      }
      return <span className="null-indicator">{t('advancedFilter.selectOperatorFirst')}</span>;
    }

    // DateTime operators that don't need input
    if (fieldType === 'datetime' && ['today', 'yesterday', 'this_week', 'last_week', 'this_month', 'last_month', 'this_year', 'last_year'].includes(rule.operator)) {
      return <span className="null-indicator">No value needed</span>;
    }

    // DateTime operators that need number input
    if (fieldType === 'datetime' && ['last_n_days', 'older_than_days'].includes(rule.operator)) {
      return (
        <input
          type="number"
          value={rule.value}
          onChange={(e) => updateRule(groupId, rule.id, 'value', e.target.value)}
          placeholder={t('advancedFilter.numberOfDays')}
          className="filter-input"
          min="1"
        />
      );
    }

    // DateTime operators that need date input
    if (fieldType === 'datetime' && ['before', 'after', 'eq'].includes(rule.operator)) {
      return (
        <input
          type="datetime-local"
          value={rule.value}
          onChange={(e) => updateRule(groupId, rule.id, 'value', e.target.value)}
          className="filter-input"
        />
      );
    }

    // Boolean input
    if (fieldType === 'boolean') {
      return (
        <select
          value={rule.value}
          onChange={(e) => updateRule(groupId, rule.id, 'value', e.target.value)}
          className="filter-input"
        >
          <option value="">{t('advancedFilter.selectValue')}</option>
          <option value="true">{t('advancedFilter.true')}</option>
          <option value="false">{t('advancedFilter.false')}</option>
        </select>
      );
    }

    // Enum fields with single selection
    if (fieldType === 'enum' && (rule.operator === 'eq' || rule.operator === 'ne')) {
      const enumOptions = getFieldEnumOptions(rule.field);
      return (
        <select
          value={rule.value}
          onChange={(e) => updateRule(groupId, rule.id, 'value', e.target.value)}
          className="filter-input"
        >
          <option value="">{t('advancedFilter.selectValue')}</option>
          {enumOptions.map(option => (
            <option key={option.value} value={option.value}>
              {translateLabel(option.label)}
            </option>
          ))}
        </select>
      );
    }

    // Multi-value input for 'in' and 'not_in' operators
    if (rule.operator === 'in' || rule.operator === 'not_in') {
      const enumOptions = getFieldEnumOptions(rule.field);
      const placeholder = fieldType === 'enum' && enumOptions.length > 0
        ? enumOptions.slice(0, 3).map(o => o.value).join(',')
        : 'value1,value2,value3';
        
      return (
        <input
          type="text"
          value={rule.value}
          onChange={(e) => updateRule(groupId, rule.id, 'value', e.target.value)}
          placeholder={placeholder}
          className="filter-input"
        />
      );
    }

    // Default input
    return (
      <input
        type={fieldType === 'number' ? 'number' : 'text'}
        value={rule.value}
        onChange={(e) => updateRule(groupId, rule.id, 'value', e.target.value)}
        placeholder={t('advancedFilter.enterValue')}
        className="filter-input"
      />
    );
  };

  return (
    <div className="advanced-filter">
      <div className="advanced-filter-header">
        <h3>{title || defaultTitle}</h3>
        <button onClick={onClose} className="close-button">×</button>
      </div>

      <div className="filter-groups">
        {groups.map((group, groupIndex) => (
          <div key={group.id} className="filter-group">
            <div className="filter-group-header">
              {groupIndex > 0 && (
                <div className="group-connector">{t('advancedFilter.and')}</div>
              )}
              
              <div className="filter-group-controls">
                <select
                  value={group.logicalOperator}
                  onChange={(e) => updateGroupOperator(group.id, e.target.value as 'and' | 'or')}
                  className="group-operator"
                >
                  <option value="and">{t('advancedFilter.and')}</option>
                  <option value="or">{t('advancedFilter.or')}</option>
                </select>
                
                {groups.length > 1 && (
                  <button
                    onClick={() => removeGroup(group.id)}
                    className="remove-group-button"
                  >
                    ×
                  </button>
                )}
              </div>
            </div>

            <div className="filter-rules">
              {group.rules.map((rule) => (
                <div key={rule.id} className="filter-rule">
                  <select
                    value={rule.field}
                    onChange={(e) => updateRule(group.id, rule.id, 'field', e.target.value)}
                    className="field-select"
                  >
                    {fieldOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {translateLabel(option.label)}
                      </option>
                    ))}
                  </select>

                  <select
                    value={rule.operator}
                    onChange={(e) => updateRule(group.id, rule.id, 'operator', e.target.value)}
                    className="operator-select"
                  >
                    {getOperatorsForField(getFieldType(rule.field)).map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>

                  {renderValueInput(group.id, rule)}

                  <button
                    onClick={() => removeRule(group.id, rule.id)}
                    className="remove-rule-button"
                  >
                    {t('advancedFilter.remove')}
                  </button>
                </div>
              ))}
              
              <button
                onClick={() => addRule(group.id)}
                className="add-rule-button-small"
              >
                {t('advancedFilter.addRuleToGroup')}
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="filter-actions">
        <div className="filter-group-actions">
          <button onClick={addGroup} className="add-group-button">
            {t('advancedFilter.addGroup')}
          </button>
        </div>
        
        <div className="filter-buttons">
          <button onClick={clearFilter} className="clear-button">
            {t('advancedFilter.clear')}
          </button>
          <button onClick={applyFilter} className="apply-button">
            {t('advancedFilter.applyFilter')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdvancedFilter; 