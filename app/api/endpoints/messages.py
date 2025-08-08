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
from app.tasks.celery import celery_app  # Adicione esta importação


router = APIRouter()


@router.post("/notificar", response_model=NotificationCreateResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_notification(notification: NotificationCreate, rabbitmq_service: RabbitMQService = Depends(get_rabbitmq_service)):
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
    # await rabbitmq_service.publish_message(message=data, queue_name="validation_queue")  // Remova ou comente esta linha
    celery_app.send_task('tasks.validate_notification', kwargs={'data': data})  # Adicione esta linha para invocar a tarefa
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