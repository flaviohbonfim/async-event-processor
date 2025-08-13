from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.message import (
    NotificationCreate,
    NotificationCreateResponse,
    NotificationStatusResponse,
)
from app.services.rabbitmq import RabbitMQService, get_rabbitmq_service
from app.core import storage
from app.core.config import settings # Import settings
# from app.tasks.message_tasks import validate_notification # Not directly used here anymore
from uuid import uuid4
# from app.tasks.celery import celery_app  # Removida esta importação


router = APIRouter()


@router.post("/notificar", response_model=NotificationCreateResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_notification(notification: NotificationCreate, rabbitmq_service: RabbitMQService = Depends(get_rabbitmq_service)):
    if notification.tipoNotificacao not in settings.ALLOWED_NOTIFICATION_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported notification type: {notification.tipoNotificacao}. Allowed types are: {', '.join(settings.ALLOWED_NOTIFICATION_TYPES)}"
        )

    trace_id = uuid4()
    mensagem_id = notification.mensagemId or uuid4()
    data = {
        'mensagemId': str(mensagem_id),  # Convertido para string
        'conteudoMensagem': notification.conteudoMensagem,
        'channel': notification.tipoNotificacao,  # Alterado para 'channel' para matching com tarefas
        'status': 'RECEBIDO',
        'traceId': str(trace_id)  # Adicionado traceId
    }
    storage.set_notification(str(trace_id), data)

    try:
        # Publish to the initial notification input queue
        await rabbitmq_service.publish_message(
            message=data,
            routing_key=settings.NOTIFICATION_INPUT_QUEUE,
            exchange_name=f"{settings.NOTIFICATION_INPUT_QUEUE}_exchange"
        )
    except Exception as e:
        # Update status to FALHA_ENVIO if publishing fails
        data["status"] = "FALHA_ENVIO"
        storage.set_notification(str(trace_id), data)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from e

    return NotificationCreateResponse(mensagemId=mensagem_id, traceId=trace_id)

@router.get("/notificacao/status/{traceId}", response_model=NotificationStatusResponse)
async def get_status(traceId: str):
    info = storage.get_notification(traceId)
    if info is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    # Renomear 'channel' para 'tipoNotificacao' para matching com o schema
    if 'channel' in info:
        info['tipoNotificacao'] = info.pop('channel')
    return NotificationStatusResponse(**info)
