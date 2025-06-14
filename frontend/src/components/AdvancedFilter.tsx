import React, { useState } from 'react';
import { CardFilter, CardType, StringFieldFilter, EnumFliedFilterCardType, EnumFliedFilterInt, EnumFliedFilterUUID } from '../client';
import '../styles/AdvancedFilter.css';

interface FilterRule {
  id: string;
  field: string;
  operator: string;
  value: string;
  logicalOperator?: 'and' | 'or';
}

interface AdvancedFilterProps {
  onFilterChange: (filter: CardFilter | null) => void;
  onClose: () => void;
}

const fieldOptions = [
  { value: 'name', label: 'Card Name', type: 'string' },
  { value: 'card_id', label: 'Card ID', type: 'number' },
  { value: 'rank', label: 'Rank', type: 'enum' },
  { value: 'anime_name', label: 'Anime Name', type: 'string' },
  { value: 'anime_link', label: 'Anime Link', type: 'string' },
  { value: 'author', label: 'Author', type: 'string' },
  { value: 'image', label: 'Image Path', type: 'string' },
  { value: 'mp4', label: 'MP4 Path', type: 'string' },
  { value: 'webm', label: 'WebM Path', type: 'string' }
];

const stringOperators = [
  { value: 'eq', label: 'Equals' },
  { value: 'ne', label: 'Not Equals' },
  { value: 'like', label: 'Contains (case sensitive)' },
  { value: 'ilike', label: 'Contains (case insensitive)' },
  { value: 'not_like', label: 'Does not contain' },
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

const rankOptions = [
  { value: 'ass', label: 'ASS' },
  { value: 's', label: 'S' },
  { value: 'a', label: 'A' },
  { value: 'b', label: 'B' },
  { value: 'c', label: 'C' },
  { value: 'd', label: 'D' },
  { value: 'e', label: 'E' }
];

const AdvancedFilter: React.FC<AdvancedFilterProps> = ({ onFilterChange, onClose }) => {
  const [rules, setRules] = useState<FilterRule[]>([
    { id: '1', field: 'name', operator: 'ilike', value: '' }
  ]);

  const addRule = () => {
    const newRule: FilterRule = {
      id: Date.now().toString(),
      field: 'name',
      operator: 'ilike',
      value: '',
      logicalOperator: 'and'
    };
    setRules([...rules, newRule]);
  };

  const removeRule = (id: string) => {
    if (rules.length > 1) {
      setRules(rules.filter(rule => rule.id !== id));
    }
  };

  const updateRule = (id: string, field: keyof FilterRule, value: string) => {
    setRules(rules.map(rule => 
      rule.id === id ? { ...rule, [field]: value } : rule
    ));
  };

  const getOperatorsForField = (fieldType: string) => {
    switch (fieldType) {
      case 'string':
        return stringOperators;
      case 'number':
        return numberOperators;
      case 'enum':
        return enumOperators;
      default:
        return stringOperators;
    }
  };

  const getFieldType = (fieldName: string) => {
    const field = fieldOptions.find(f => f.value === fieldName);
    return field?.type || 'string';
  };

  const buildFilter = (): CardFilter | null => {
    const validRules = rules.filter(rule => rule.value.trim() !== '' || rule.operator === 'is_null');
    
    if (validRules.length === 0) {
      return null;
    }

    const buildFieldFilter = (rule: FilterRule): Partial<CardFilter> => {
      const fieldType = getFieldType(rule.field);
      let filterValue: any;

      if (rule.operator === 'is_null') {
        filterValue = { is_null: true };
      } else if (rule.operator === 'in' || rule.operator === 'not_in') {
        const values = rule.value.split(',').map(v => v.trim()).filter(v => v !== '');
        if (values.length === 0) {
          return {}; // Skip empty lists
        }
        if (fieldType === 'enum') {
          filterValue = { [rule.operator]: values as CardType[] };
        } else if (fieldType === 'number') {
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
        } else if (fieldType === 'enum') {
          filterValue = { [rule.operator]: rule.value as CardType };
        } else {
          filterValue = { [rule.operator]: rule.value };
        }
      }

      return { [rule.field]: filterValue };
    };

    if (validRules.length === 1) {
      return buildFieldFilter(validRules[0]) as CardFilter;
    }

    // Group rules by logical operator
    const andRules: FilterRule[] = [];
    const orRules: FilterRule[] = [];

    validRules.forEach((rule, index) => {
      if (index === 0 || rule.logicalOperator === 'and') {
        andRules.push(rule);
      } else {
        orRules.push(rule);
      }
    });

    let filter: CardFilter = {};

    if (andRules.length > 0) {
      if (andRules.length === 1) {
        filter = buildFieldFilter(andRules[0]) as CardFilter;
      } else {
        filter.and = andRules.map(rule => buildFieldFilter(rule) as CardFilter);
      }
    }

    if (orRules.length > 0) {
      const orFilters = orRules.map(rule => buildFieldFilter(rule) as CardFilter);
      if (filter.and || Object.keys(filter).length > 0) {
        // Combine existing filter with OR rules
        filter = {
          or: [
            filter,
            ...(orFilters.length === 1 ? orFilters : [{ or: orFilters }])
          ]
        };
      } else {
        filter.or = orFilters;
      }
    }

    return filter;
  };

  const applyFilter = () => {
    const filter = buildFilter();
    onFilterChange(filter);
  };

  const clearFilter = () => {
    setRules([{ id: '1', field: 'name', operator: 'ilike', value: '' }]);
    onFilterChange(null);
  };

  const renderValueInput = (rule: FilterRule) => {
    const fieldType = getFieldType(rule.field);
    
    if (rule.operator === 'is_null') {
      return <span className="null-indicator">No value needed</span>;
    }

    if (rule.field === 'rank' && (rule.operator === 'eq' || rule.operator === 'ne')) {
      return (
        <select
          value={rule.value}
          onChange={(e) => updateRule(rule.id, 'value', e.target.value)}
          className="filter-input"
        >
          <option value="">Select rank...</option>
          {rankOptions.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      );
    }

    if (rule.operator === 'in' || rule.operator === 'not_in') {
      return (
        <input
          type="text"
          value={rule.value}
          onChange={(e) => updateRule(rule.id, 'value', e.target.value)}
          placeholder={fieldType === 'enum' ? 'ass,s,a' : 'value1,value2,value3'}
          className="filter-input"
        />
      );
    }

    return (
      <input
        type={fieldType === 'number' ? 'number' : 'text'}
        value={rule.value}
        onChange={(e) => updateRule(rule.id, 'value', e.target.value)}
        placeholder="Enter value..."
        className="filter-input"
      />
    );
  };

  return (
    <div className="advanced-filter">
      <div className="advanced-filter-header">
        <h3>Advanced Filter</h3>
        <button onClick={onClose} className="close-button">×</button>
      </div>

      <div className="filter-rules">
        {rules.map((rule, index) => (
          <div key={rule.id} className="filter-rule">
            {index > 0 && (
              <select
                value={rule.logicalOperator || 'and'}
                onChange={(e) => updateRule(rule.id, 'logicalOperator', e.target.value)}
                className="logical-operator"
              >
                <option value="and">AND</option>
                <option value="or">OR</option>
              </select>
            )}

            <select
              value={rule.field}
              onChange={(e) => updateRule(rule.id, 'field', e.target.value)}
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
              onChange={(e) => updateRule(rule.id, 'operator', e.target.value)}
              className="operator-select"
            >
              {getOperatorsForField(getFieldType(rule.field)).map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>

            {renderValueInput(rule)}

            {rules.length > 1 && (
              <button
                onClick={() => removeRule(rule.id)}
                className="remove-rule-button"
              >
                Remove
              </button>
            )}
          </div>
        ))}
      </div>

      <div className="filter-actions">
        <button onClick={addRule} className="add-rule-button">
          Add Rule
        </button>
        
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