from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import Optional

class ChannelType(Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WHATSAPP = "whatsapp"

class NotificationCreate(BaseModel):
    mensagemId: Optional[UUID] = Field(default_factory=uuid4)
    conteudoMensagem: str
    tipoNotificacao: str

class NotificationCreateResponse(BaseModel):
    mensagemId: UUID
    traceId: UUID

class NotificationStatusResponse(BaseModel):
    traceId: UUID
    mensagemId: UUID
    conteudoMensagem: str
    tipoNotificacao: str
    status: str
