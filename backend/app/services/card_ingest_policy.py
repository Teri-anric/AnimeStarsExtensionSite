MAX_INGESTED_CARD_ID = 1_000_000


def is_card_id_ingestible(card_id: int) -> bool:
    return card_id <= MAX_INGESTED_CARD_ID
