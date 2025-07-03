from typing import Any
from sqlalchemy import and_, or_, not_
from sqlalchemy.sql.elements import ClauseElement
import logging

logger = logging.getLogger(__name__)


class ConditionBuilder:
    """Builds SQLAlchemy conditions from filter dictionaries"""
    
    def __init__(self, operator_map: dict[str, Any]):
        self.operator_map = operator_map
    
    def build_conditions(
        self, 
        model_class, 
        filters: dict[str, Any], 
        parent_alias=None
    ) -> list[ClauseElement]:
        """Build SQLAlchemy conditions from filter dictionary"""
        if not filters:
            return []
            
        conditions = []
        model_alias = parent_alias or model_class
        
        for field_name, field_filters in filters.items():
            if self._is_logical_operator(field_name):
                logical_conditions = self._handle_logical_operators(
                    field_name, field_filters, model_class
                )
                conditions.extend(logical_conditions)
            else:
                condition = self._build_field_condition(model_alias, field_name, field_filters)
                if condition is not None:
                    conditions.append(condition)
        
        return conditions
    
    def _is_logical_operator(self, field_name: str) -> bool:
        """Check if field name is a logical operator"""
        return field_name in ['and', 'or', 'not']
    
    def _handle_logical_operators(
        self, 
        operator: str, 
        operand: Any, 
        model_class
    ) -> list[ClauseElement]:
        """Handle AND, OR, NOT logical operators"""
        conditions = []
        
        if operator == 'and' and isinstance(operand, list):
            conditions.extend(self._handle_and_operator(operand, model_class))
        elif operator == 'or' and isinstance(operand, list):
            conditions.extend(self._handle_or_operator(operand, model_class))
        elif operator == 'not':
            conditions.extend(self._handle_not_operator(operand, model_class))
        
        return conditions
    
    def _handle_and_operator(self, operand: list[dict[str, Any]], model_class) -> list[ClauseElement]:
        """Handle AND operator"""
        conditions = []
        for filter_dict in operand:
            sub_conditions = self.build_conditions(model_class, filter_dict)
            if sub_conditions:
                conditions.append(and_(*sub_conditions))
        return conditions
    
    def _handle_or_operator(self, operand: list[dict[str, Any]], model_class) -> list[ClauseElement]:
        """Handle OR operator"""
        or_conditions = []
        for filter_dict in operand:
            sub_conditions = self.build_conditions(model_class, filter_dict)
            if sub_conditions:
                or_conditions.extend(sub_conditions)
        
        return [or_(*or_conditions)] if or_conditions else []
    
    def _handle_not_operator(self, operand: dict[str, Any], model_class) -> list[ClauseElement]:
        """Handle NOT operator"""
        sub_conditions = self.build_conditions(model_class, operand)
        return [not_(and_(*sub_conditions))] if sub_conditions else []
    
    def _build_field_condition(
        self, 
        model_alias, 
        field_name: str, 
        field_filters: dict[str, Any]
    ) -> ClauseElement | None:
        """Build condition for a specific field"""
        # Handle relationships (sub-entities)
        if hasattr(model_alias, field_name):
            attr = getattr(model_alias, field_name)
            
            if hasattr(attr.property, 'mapper'):
                return self._build_relationship_condition(attr, field_filters)
            else:
                return self._apply_field_operators(attr, field_filters)
        
        # Handle sql_property (computed fields)
        if hasattr(model_alias, 'sql_property'):
            sql_properties = getattr(model_alias, 'sql_property', {})
            if field_name in sql_properties:
                sql_prop = sql_properties[field_name]
                return self._apply_field_operators(sql_prop, field_filters)
        
        logger.warning(f"Field {field_name} not found in {model_alias}")
        return None
    
    def _build_relationship_condition(
        self, 
        relationship_attr, 
        field_filters: dict[str, Any]
    ) -> ClauseElement | None:
        """Build conditions for relationship fields"""
        related_model = relationship_attr.property.mapper.class_
        sub_conditions = []
        
        for sub_field, sub_filters in field_filters.items():
            if hasattr(related_model, sub_field):
                related_attr = getattr(related_model, sub_field)
                condition = self._apply_field_operators(related_attr, sub_filters)
                if condition is not None:
                    sub_conditions.append(condition)
            else:
                logger.warning(f"Sub-field {sub_field} not found in {related_model}")
        
        if sub_conditions:
            return and_(*sub_conditions) if len(sub_conditions) > 1 else sub_conditions[0]
        return None
    
    def _apply_field_operators(
        self, 
        column, 
        field_filters: dict[str, Any]
    ) -> ClauseElement | None:
        """Apply operators to a specific column"""
        conditions = []
        
        for operator, value in field_filters.items():
            if operator not in self.operator_map:
                logger.warning(f"Unknown operator: {operator}")
                continue
                
            try:
                condition = self.operator_map[operator](column, value)
                conditions.append(condition)
            except Exception as e:
                logger.warning(f"Failed to apply operator {operator} with value {value}: {e}")
                continue
        
        if conditions:
            return and_(*conditions) if len(conditions) > 1 else conditions[0]
        return None
