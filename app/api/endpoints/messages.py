from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.message import (
    NotificationCreate,
    NotificationCreateResponse,
    NotificationStatusResponse,
)
from app.services.rabbitmq import RabbitMQService, get_rabbitmq_service
from app.core import storage
from app.tasks.message_tasks import validate_notification
from uuid import uuid4


router = APIRouter()


@router.post("/notificar", response_model=NotificationCreateResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_notification(notification: NotificationCreate, rabbitmq_service: RabbitMQService = Depends(get_rabbitmq_service)):
    trace_id = uuid4()
    mensagem_id = notification.mensagemId or uuid4()
    data = {
        'mensagemId': str(mensagem_id),  # Convertido para string
        'conteudoMensagem': notification.conteudoMensagem,
        'tipoNotificacao': notification.tipoNotificacao,
        'status': 'RECEBIDO'
    }
    storage.set_notification(str(trace_id), data)
    await rabbitmq_service.publish_message(message=data, queue_name="fila.notificacao.entrada.seu-nome")
    return NotificationCreateResponse(mensagemId=mensagem_id, traceId=trace_id)

@router.get("/notificacao/status/{traceId}", response_model=NotificationStatusResponse)
async def get_status(traceId: str):
    info = storage.get_notification(traceId)
    if info is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return NotificationStatusResponse(**info, traceId=traceId)