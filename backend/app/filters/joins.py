from typing import Any, Dict, Set
from sqlalchemy.sql import Select
from sqlalchemy.exc import InvalidRequestError
import logging

logger = logging.getLogger(__name__)


class JoinManager:
    """Manages joins for the filtering service"""
    
    def __init__(self):
        self.joins_cache: dict[str, Set[str]] = {}
    
    def collect_required_joins(self, model_class, filters: Dict[str, Any]) -> set[str]:
        """Collect all relationship paths that need to be joined"""
        joins_needed = set()
        self._collect_joins_recursive(model_class, filters, joins_needed)
        return joins_needed
    
    def _collect_joins_recursive(
        self, 
        model_class, 
        filters: Dict[str, Any], 
        joins_needed: set[str], 
        current_path: str = ""
    ) -> None:
        """Recursively collect joins needed for nested filters"""
        for field_name, field_filters in filters.items():
            if self._is_logical_operator(field_name):
                self._handle_logical_operator_joins(
                    model_class, field_name, field_filters, joins_needed, current_path
                )
            else:
                self._handle_field_joins(
                    model_class, field_name, field_filters, joins_needed, current_path
                )
    
    def _is_logical_operator(self, field_name: str) -> bool:
        """Check if field name is a logical operator"""
        return field_name in ['and', 'or', 'not']
    
    def _handle_logical_operator_joins(
        self,
        model_class,
        operator: str,
        operand: Any,
        joins_needed: set[str],
        current_path: str
    ) -> None:
        """Handle joins for logical operators"""
        if operator in ['and', 'or'] and isinstance(operand, list):
            for filter_dict in operand:
                self._collect_joins_recursive(model_class, filter_dict, joins_needed, current_path)
        elif operator == 'not':
            self._collect_joins_recursive(model_class, operand, joins_needed, current_path)
    
    def _handle_field_joins(
        self,
        model_class,
        field_name: str,
        field_filters: Any,
        joins_needed: set[str],
        current_path: str
    ) -> None:
        """Handle joins for regular fields"""
        if not hasattr(model_class, field_name):
            return
            
        attr = getattr(model_class, field_name)
        if not hasattr(attr.property, 'mapper'):
            return
            
        # It's a relationship - add to joins needed
        join_path = f"{current_path}.{field_name}" if current_path else field_name
        joins_needed.add(join_path)
        
        # Recursively collect joins for sub-filters
        related_model = attr.property.mapper.class_
        if isinstance(field_filters, dict):
            self._collect_joins_recursive(related_model, field_filters, joins_needed, join_path)
    
    def apply_joins(self, stmt: Select, model_class, join_paths: set[str]) -> Select:
        """Apply all necessary joins to the statement"""
        for join_path in join_paths:
            stmt = self._add_single_join(stmt, model_class, join_path)
        return stmt
    
    def _add_single_join(self, stmt: Select, model_class, join_path: str) -> Select:
        """Add a single join to the statement"""
        try:
            parts = join_path.split('.')
            current_model = model_class
            
            for part in parts:
                if not hasattr(current_model, part):
                    logger.warning(f"Attribute {part} not found in {current_model}")
                    break
                    
                attr = getattr(current_model, part)
                if not hasattr(attr.property, 'mapper'):
                    logger.warning(f"Attribute {part} is not a relationship")
                    break
                    
                related_model = attr.property.mapper.class_
                stmt = stmt.join(attr)
                current_model = related_model
                
        except InvalidRequestError as e:
            logger.warning(f"Failed to add join for path {join_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error adding join for path {join_path}: {e}")
        
        return stmt
