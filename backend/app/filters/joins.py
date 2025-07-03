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
            
        # It's a relationship - check if we need joins
        join_path = f"{current_path}.{field_name}" if current_path else field_name
        related_model = attr.property.mapper.class_
        
        if isinstance(field_filters, dict):
            # Check for ArrayEntryFilter operators
            if 'any' in field_filters:
                # For 'any' operator, we typically don't need explicit joins
                # as relationship.any() handles the subquery internally
                self._collect_joins_recursive(related_model, field_filters['any'], joins_needed, join_path)
            elif 'all' in field_filters:
                # For 'all' operator, we also don't need explicit joins
                self._collect_joins_recursive(related_model, field_filters['all'], joins_needed, join_path)
            elif 'length' in field_filters:
                # Length filtering might need the relationship loaded but not necessarily joined
                pass
            else:
                # Regular relationship filtering - may need joins depending on query complexity
                # For simple EXISTS queries, we might not need joins
                # But we add it to be safe - the SQL optimizer should handle it
                joins_needed.add(join_path)
                self._collect_joins_recursive(related_model, field_filters, joins_needed, join_path)
    
    def apply_joins(self, stmt: Select, model_class, join_paths: set[str]) -> Select:
        """Apply all necessary joins to the statement"""
        for join_path in join_paths:
            stmt = self._add_single_join(stmt, model_class, join_path)
        return stmt
    
    def _add_single_join(self, stmt: Select, model_class, join_path: str) -> Select:
        """Add a single join to the statement"""
        try:
            path_parts = join_path.split('.')
            current_model = model_class
            
            for part in path_parts:
                if hasattr(current_model, part):
                    attr = getattr(current_model, part)
                    if hasattr(attr.property, 'mapper'):
                        # It's a relationship, add join
                        stmt = stmt.join(attr)
                        current_model = attr.property.mapper.class_
                    else:
                        logger.warning(f"Attribute {part} is not a relationship")
                        break
                else:
                    logger.warning(f"Attribute {part} not found in {current_model}")
                    break
                    
            return stmt
        except InvalidRequestError as e:
            # Join might already exist or be invalid - log and continue
            logger.warning(f"Could not add join for {join_path}: {e}")
            return stmt
        except Exception as e:
            logger.error(f"Error adding join for {join_path}: {e}")
            return stmt
