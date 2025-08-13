from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import Optional

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
