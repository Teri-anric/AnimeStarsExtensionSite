import React, { useState } from 'react';
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
  { value: 'eq', label: 'Equals' },
  { value: 'ne', label: 'Not Equals' },
  { value: 'contains', label: 'Contains (case sensitive)' },
  { value: 'icontains', label: 'Contains (case insensitive)' },
  { value: 'not_contains', label: 'Does not contain' },
  { value: 'is_null', label: 'Is empty' }
];

const numberOperators = [
  { value: 'eq', label: 'Equals' },
  { value: 'ne', label: 'Not Equals' },
  { value: 'in', label: 'In list' },
  { value: 'not_in', label: 'Not in list' },
  { value: 'is_null', label: 'Is empty' }
];

const enumOperators = [
  { value: 'eq', label: 'Equals' },
  { value: 'ne', label: 'Not Equals' },
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
  { value: 'eq', label: 'Equals' },
  { value: 'is_null', label: 'Is empty' }
];

const parseFilterToGroups = (filter: GenericFilter, fieldOptions: FieldOption[]): FilterGroup[] => {
  console.log('Parsing filter to groups:', filter);
  const groups: FilterGroup[] = [];
  let groupId = 1;
  let ruleId = 1;

  const parseFieldFilter = (fieldName: string, fieldFilter: any): FilterRule => {
    const operators = Object.keys(fieldFilter);
    const operator = operators[0] as FilterOperator;
    const value = fieldFilter[operator];
    
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
    const rules: FilterRule[] = [];
    let groupOperator: 'and' | 'or' = 'and';

    // Check if this subfilter has and/or operators
    if (subFilter.and && Array.isArray(subFilter.and)) {
      groupOperator = 'and';
      subFilter.and.forEach(item => {
        Object.entries(item).forEach(([key, value]) => {
          if (fieldOptions.some(f => f.value === key)) {
            rules.push(parseFieldFilter(key, value));
          }
        });
      });
    } else if (subFilter.or && Array.isArray(subFilter.or)) {
      groupOperator = 'or';
      subFilter.or.forEach(item => {
        Object.entries(item).forEach(([key, value]) => {
          if (fieldOptions.some(f => f.value === key)) {
            rules.push(parseFieldFilter(key, value));
          }
        });
      });
    } else {
      // Single field filter
      Object.entries(subFilter).forEach(([key, value]) => {
        if (fieldOptions.some(f => f.value === key)) {
          rules.push(parseFieldFilter(key, value));
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
  title = 'Advanced Filter'
}) => {
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
      operator: firstField?.type === 'string' ? 'icontains' : 'eq',
      value: ''
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
              }
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

      if (validRules.length === 1) {
        return buildFieldFilter(validRules[0]) as GenericFilter;
      }

      const ruleFilters = validRules.map(rule => buildFieldFilter(rule) as GenericFilter);
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
      return <span className="null-indicator">No value needed</span>;
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
          placeholder="Number of days..."
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
          <option value="">Select value...</option>
          <option value="true">True</option>
          <option value="false">False</option>
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
          <option value="">Select value...</option>
          {enumOptions.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
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
        placeholder="Enter value..."
        className="filter-input"
      />
    );
  };

  return (
    <div className="advanced-filter">
      <div className="advanced-filter-header">
        <h3>{title}</h3>
        <button onClick={onClose} className="close-button">×</button>
      </div>

      <div className="filter-groups">
        {groups.map((group, groupIndex) => (
          <div key={group.id} className="filter-group">
            <div className="filter-group-header">
              {groupIndex > 0 && (
                <div className="group-connector">AND</div>
              )}
              
              <div className="filter-group-controls">
                <select
                  value={group.logicalOperator}
                  onChange={(e) => updateGroupOperator(group.id, e.target.value as 'and' | 'or')}
                  className="group-operator"
                >
                  <option value="and">AND</option>
                  <option value="or">OR</option>
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
                        {option.label}
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
                    Remove
                  </button>
                </div>
              ))}
              
              <button
                onClick={() => addRule(group.id)}
                className="add-rule-button-small"
              >
                Add Rule to Group
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="filter-actions">
        <div className="filter-group-actions">
          <button onClick={addGroup} className="add-group-button">
            Add Group
          </button>
        </div>
        
        <div className="filter-buttons">
          <button onClick={clearFilter} className="clear-button">
            Clear
          </button>
          <button onClick={applyFilter} className="apply-button">
            Apply Filter
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdvancedFilter; 