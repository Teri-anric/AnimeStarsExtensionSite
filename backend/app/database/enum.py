from enum import Enum


class CardType(Enum):
    SSS = "sss"
    ASS = "ass"
    S_PLUS = "s_plus"
    S = "s"
    A_PLUS = "a_plus"
    A = "a"
    B_PLUS = "b_plus"
    B = "b"
    C_PLUS = "c_plus"
    C = "c"
    D_PLUS = "d_plus"
    D = "d"
    E_PLUS = "e_plus"
    E = "e"


class CardCollection(Enum):
    TRADE = "trade" 
    NEED = "need"
    OWNED = "owned"
    UNLOCKED_OWNED = "unlocked_owned"
