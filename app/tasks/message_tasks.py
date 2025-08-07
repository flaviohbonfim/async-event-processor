import time
from celery.utils.log import get_task_logger
from app.tasks.celery import celery_app
from app.core import storage
from app.schemas.message import ChannelType
from app.services.rabbitmq import get_rabbitmq_service # Alterado para usar o getter

logger = get_task_logger(__name__)

# Simulação de um serviço de gestão de canais
CHANNEL_AVAILABILITY = {
    ChannelType.EMAIL: True,
    ChannelType.SMS: True,
    ChannelType.PUSH: False,  # Simular canal indisponível
    ChannelType.WHATSAPP: True,
}

@celery_app.task(name="tasks.validate_notification")
def validate_notification(data):
    trace_id = data.get("traceId")
    logger.info(f"[traceId: {trace_id}] Iniciando validação.")
    storage.set_status(trace_id, "Validating")

    time.sleep(2)  # Simular tempo de processamento

    channel = data.get('channel')
    rabbitmq_service = get_rabbitmq_service()

    if CHANNEL_AVAILABILITY.get(ChannelType(channel), False):
        logger.info(f"[traceId: {trace_id}] Canal '{channel}' validado com sucesso.")
        dispatch_notification.delay(data)
    else:
        logger.warning(f"[traceId: {trace_id}] Canal '{channel}' indisponível. Falha na validação.")
        storage.set_status(trace_id, "ValidationFailed")

@celery_app.task(name="tasks.dispatch_notification")
def dispatch_notification(data):
    trace_id = data.get("traceId")
    logger.info(f"[traceId: {trace_id}] Iniciando despacho.")
    storage.set_status(trace_id, "Dispatching")
    
    time.sleep(2) # Simular tempo de processamento

    channel = data.get('channel')
    # A tarefa 'send_notification' será responsável por escolher a fila correta
    send_notification.delay(data)
    logger.info(f"[traceId: {trace_id}] Despacho para envio iniciado.")

@celery_app.task(name="tasks.send_notification", acks_late=True)
def send_notification(data):
    trace_id = data.get("traceId")
    channel = data.get('channel')
    logger.info(f"[traceId: {trace_id}] Enviando notificação via '{channel}'.")
    storage.set_status(trace_id, "Sending")

    time.sleep(3) # Simular tempo de envio

    # Simulação de sucesso
    logger.info(f"[traceId: {trace_id}] Notificação enviada com sucesso.")
    # Atualiza o status final
    update_status.delay(trace_id, "Sent")

@celery_app.task(name="tasks.update_status")
def update_status(trace_id: str, final_status: str):
    logger.info(f"[traceId: {trace_id}] Atualizando estado final para '{final_status}'.")
    storage.set_status(trace_id, final_status)
    logger.info(f"[traceId: {trace_id}] Processo concluído.")