
from .types import (
    BaseFilter, 
    UUIDEntryFilter, 
    StringEntryFilter, 
    IntegerEntryFilter,
    DateTimeEntryFilter,
    BooleanEntryFilter,
    ArrayEntryFilter
)




class UserFilter(BaseFilter):
    """Filter schema for User model"""
    id: UUIDEntryFilter | None = None
    username: StringEntryFilter | None = None
    email: StringEntryFilter | None = None
    is_active: BooleanEntryFilter | None = None
    created_at: DateTimeEntryFilter | None = None
    updated_at: DateTimeEntryFilter | None = None


class CardFilter(BaseFilter):
    """Filter schema for Card model"""
    id: UUIDEntryFilter | None = None
    name: StringEntryFilter | None = None
    description: StringEntryFilter | None = None
    attack: IntegerEntryFilter | None = None
    defense: IntegerEntryFilter | None = None
    cost: IntegerEntryFilter | None = None
    is_active: BooleanEntryFilter | None = None
    created_at: DateTimeEntryFilter | None = None
    updated_at: DateTimeEntryFilter | None = None
    
    # Relationship filters
    owner_user: UserFilter | None = None


class CardUsersStatsFilter(BaseFilter):
    """Filter schema for CardUsersStats model"""
    id: UUIDEntryFilter | None = None
    total_wins: IntegerEntryFilter | None = None
    total_losses: IntegerEntryFilter | None = None
    total_draws: IntegerEntryFilter | None = None
    win_rate: IntegerEntryFilter | None = None
    created_at: DateTimeEntryFilter | None = None
    updated_at: DateTimeEntryFilter | None = None
    
    # Relationship filters
    card: CardFilter | None = None
    user: UserFilter | None = None


class DeckFilter(BaseFilter):
    """Filter schema for Deck model"""
    id: UUIDEntryFilter | None = None
    name: StringEntryFilter | None = None
    description: StringEntryFilter | None = None
    is_public: BooleanEntryFilter | None = None
    created_at: DateTimeEntryFilter | None = None
    updated_at: DateTimeEntryFilter | None = None
    
    # Relationship filters
    owner: UserFilter | None = None
    
    # Array filters
    cards: ArrayEntryFilter[CardFilter] | None = None

