from uuid import UUID


from app.database.models.chat import ChatMessage
from app.database.repos.crud import CRUDRepository
from app.database.repos.base import BaseRepository


class ChatRepository(CRUDRepository[ChatMessage, UUID], BaseRepository):
    @property
    def entry_class(self) -> type[ChatMessage]:
        return ChatMessage
