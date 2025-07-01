

class FilterOperators:
    """Contains all supported filter operators and their implementations"""
    
    @staticmethod
    def get_operator_map():
        return {
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
            'in_': lambda col, val: col.in_(val),
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
    
    @staticmethod
    def get_supported_operators() -> list[str]:
        """Get list of all supported operator names"""
        return list(FilterOperators.get_operator_map().keys()) 