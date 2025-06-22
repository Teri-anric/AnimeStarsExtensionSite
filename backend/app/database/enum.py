from enum import Enum


class CardType(Enum):
    ASS = "ass"
    S = "s"
    A = "a"
    B = "b"
    C = "c"
    D = "d"
    E = "e"


class CardCollection(Enum):
    TRADE = "trade" 
    NEED = "need"
    OWNED = "owned"
    UNLOCKED_OWNED = "unlocked_owned"
