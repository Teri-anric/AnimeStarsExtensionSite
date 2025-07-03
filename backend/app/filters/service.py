from typing import Any, Dict, List, Set
from sqlalchemy import and_
from sqlalchemy.sql import Select
import logging

from .operators import FilterOperators
from .joins import JoinManager
from .conditions import ConditionBuilder

logger = logging.getLogger(__name__)


class FilterService:
    """Universal filtering service that works with any SQLAlchemy model"""
    
    def __init__(self):
        self.operator_map = FilterOperators.get_operator_map()
        self.join_manager = JoinManager()
        self.condition_builder = ConditionBuilder(self.operator_map)
    
    def apply_filters(
        self, 
        stmt: Select, 
        model_class, 
        filters: Dict[str, Any] | None
    ) -> Select:
        """Apply filters to a SQLAlchemy select statement"""
        if not filters:
            return stmt
        
        try:
            # Collect and apply necessary joins
            joins_needed = self.join_manager.collect_required_joins(model_class, filters)
            stmt = self.join_manager.apply_joins(stmt, model_class, joins_needed)
            
            # Build and apply conditions
            conditions = self.condition_builder.build_conditions(model_class, filters)
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            return stmt
            
        except Exception as e:
            logger.error(f"Error applying filters: {e}")
            return stmt
    
    def get_supported_operators(self) -> list[str]:
        """Get list of all supported operators"""
        return FilterOperators.get_supported_operators()


# Global instance for backward compatibility
filter_service = FilterService() 