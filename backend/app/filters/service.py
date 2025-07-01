from typing import Any, Dict, Optional, Union, get_origin, get_args
from sqlalchemy import Column, and_, or_, not_
from sqlalchemy.sql.elements import ClauseElement
from sqlalchemy.orm import InstrumentedAttribute, relationship
from sqlalchemy.sql import Select
from enum import Enum
from datetime import datetime, date
import inspect


class FilterService:
    """Universal filtering service that works with any SQLAlchemy model"""
    
    def __init__(self):
        self.operator_map = {
            # String operators
            'eq': lambda col, val: col == val,
            'ne': lambda col, val: col != val,
            'contains': lambda col, val: col.contains(val),
            'icontains': lambda col, val: col.ilike(f'%{val}%'),
            'like': lambda col, val: col.like(val),
            'ilike': lambda col, val: col.ilike(val),
            'not_like': lambda col, val: ~col.like(val),
            'startswith': lambda col, val: col.like(f'{val}%'),
            'endswith': lambda col, val: col.like(f'%{val}'),
            'in': lambda col, val: col.in_(val),
            'not_in': lambda col, val: ~col.in_(val),
            'is_null': lambda col, val: col.is_(None) if val else col.is_not(None),
            
            # Numeric operators
            'gt': lambda col, val: col > val,
            'gte': lambda col, val: col >= val,
            'lt': lambda col, val: col < val,
            'lte': lambda col, val: col <= val,
            
            # Date operators
            'before': lambda col, val: col < val,
            'after': lambda col, val: col > val,
            'between': lambda col, val: col.between(val[0], val[1]),
        }
    
    def apply_filters(self, stmt: Select, model_class, filters: Dict[str, Any]) -> Select:
        """Apply filters to a SQLAlchemy select statement"""
        if not filters:
            return stmt
            
        # Collect all relationships that need to be joined
        joins_needed = set()
        self._collect_joins(model_class, filters, joins_needed)
        
        # Add necessary joins
        for join_path in joins_needed:
            stmt = self._add_join(stmt, model_class, join_path)
            
        conditions = self._build_conditions(model_class, filters)
        if conditions:
            return stmt.where(and_(*conditions))
        return stmt
    
    def _collect_joins(self, model_class, filters: Dict[str, Any], joins_needed: set, current_path: str = ""):
        """Collect all relationship paths that need to be joined"""
        for field_name, field_filters in filters.items():
            if field_name in ['and', 'or', 'not']:
                if field_name == 'and' and isinstance(field_filters, list):
                    for filter_dict in field_filters:
                        self._collect_joins(model_class, filter_dict, joins_needed, current_path)
                elif field_name == 'or' and isinstance(field_filters, list):
                    for filter_dict in field_filters:
                        self._collect_joins(model_class, filter_dict, joins_needed, current_path)
                elif field_name == 'not':
                    self._collect_joins(model_class, field_filters, joins_needed, current_path)
            else:
                # Check if it's a relationship
                if hasattr(model_class, field_name):
                    attr = getattr(model_class, field_name)
                    if hasattr(attr.property, 'mapper'):
                        # It's a relationship - add to joins needed
                        join_path = f"{current_path}.{field_name}" if current_path else field_name
                        joins_needed.add(join_path)
                        
                        # Recursively collect joins for sub-filters
                        related_model = attr.property.mapper.class_
                        if isinstance(field_filters, dict):
                            self._collect_joins(related_model, field_filters, joins_needed, join_path)
    
    def _add_join(self, stmt: Select, model_class, join_path: str) -> Select:
        """Add a join to the statement based on the join path"""
        try:
            # Split the path and traverse the relationships
            parts = join_path.split('.')
            current_model = model_class
            
            for part in parts:
                if hasattr(current_model, part):
                    attr = getattr(current_model, part)
                    if hasattr(attr.property, 'mapper'):
                        related_model = attr.property.mapper.class_
                        stmt = stmt.join(attr)
                        current_model = related_model
                    else:
                        break
                else:
                    break
        except Exception:
            # If join fails, continue without it
            pass
        
        return stmt
    
    def _build_conditions(self, model_class, filters: Dict[str, Any], parent_alias=None) -> list[ClauseElement]:
        """Build SQLAlchemy conditions from filter dictionary"""
        conditions = []
        model_alias = parent_alias or model_class
        
        for field_name, field_filters in filters.items():
            if field_name in ['and', 'or', 'not']:
                # Handle logical operators
                conditions.extend(self._handle_logical_operators(field_name, field_filters, model_class))
            else:
                # Handle regular field filters
                condition = self._build_field_condition(model_alias, field_name, field_filters)
                if condition is not None:
                    conditions.append(condition)
        
        return conditions
    
    def _handle_logical_operators(self, operator: str, operand: Any, model_class) -> list[ClauseElement]:
        """Handle AND, OR, NOT logical operators"""
        conditions = []
        
        if operator == 'and':
            if isinstance(operand, list):
                for filter_dict in operand:
                    sub_conditions = self._build_conditions(model_class, filter_dict)
                    if sub_conditions:
                        conditions.append(and_(*sub_conditions))
        
        elif operator == 'or':
            if isinstance(operand, list):
                or_conditions = []
                for filter_dict in operand:
                    sub_conditions = self._build_conditions(model_class, filter_dict)
                    if sub_conditions:
                        or_conditions.extend(sub_conditions)
                if or_conditions:
                    conditions.append(or_(*or_conditions))
        
        elif operator == 'not':
            sub_conditions = self._build_conditions(model_class, operand)
            if sub_conditions:
                conditions.append(not_(and_(*sub_conditions)))
        
        return conditions
    
    def _build_field_condition(self, model_alias, field_name: str, field_filters: Dict[str, Any]) -> Optional[ClauseElement]:
        """Build condition for a specific field"""
        # Check if it's a relationship (sub-entity)
        if hasattr(model_alias, field_name):
            attr = getattr(model_alias, field_name)
            
            # If it's a relationship, handle sub-entity filtering
            if hasattr(attr.property, 'mapper'):
                related_model = attr.property.mapper.class_
                # For relationships, we need to reference the joined table's columns
                sub_conditions = []
                for sub_field, sub_filters in field_filters.items():
                    if hasattr(related_model, sub_field):
                        related_attr = getattr(related_model, sub_field)
                        condition = self._apply_field_operators(related_attr, sub_filters)
                        if condition is not None:
                            sub_conditions.append(condition)
                
                if sub_conditions:
                    return and_(*sub_conditions) if len(sub_conditions) > 1 else sub_conditions[0]
                return None
            
            # Regular field - apply operators
            return self._apply_field_operators(attr, field_filters)
        
        # Check for sql_property or computed fields
        if hasattr(model_alias, 'sql_property') and field_name in getattr(model_alias, 'sql_property', {}):
            sql_prop = model_alias.sql_property[field_name]
            return self._apply_field_operators(sql_prop, field_filters)
        
        # Field not found - skip silently or log warning
        return None
    
    def _apply_field_operators(self, column, field_filters: Dict[str, Any]) -> Optional[ClauseElement]:
        """Apply operators to a specific column"""
        conditions = []
        
        for operator, value in field_filters.items():
            if operator in self.operator_map:
                try:
                    condition = self.operator_map[operator](column, value)
                    conditions.append(condition)
                except Exception:
                    # Skip invalid operations silently
                    continue
        
        if conditions:
            return and_(*conditions) if len(conditions) > 1 else conditions[0]
        return None


# Global instance for backward compatibility
filter_service = FilterService() 