import time
import asyncio
import logging
from app.core import storage
from app.schemas.message import ChannelType
# from app.services.rabbitmq import get_rabbitmq_service # Removido, o serviço será injetado ou acessado de outra forma

logger = logging.getLogger(__name__)

# Simulação de um serviço de gestão de canais
CHANNEL_AVAILABILITY = {
    ChannelType.EMAIL: True,
    ChannelType.SMS: True,
    ChannelType.PUSH: False,  # Simular canal indisponível
    ChannelType.WHATSAPP: True,
}

# RabbitMQService instance will be passed or accessed globally
# For now, we'll assume it's available or passed as an argument
# RabbitMQService instance will be passed as an argument
from app.services.rabbitmq import RabbitMQService # Import for type hinting

async def validate_notification(data: dict, rabbitmq_service: RabbitMQService):
    trace_id = data.get("traceId")
    logger.info(f"[traceId: {trace_id}] Iniciando validação.")
    storage.set_status(trace_id, "Validating")

    await asyncio.sleep(2)  # Simular tempo de processamento

    channel = data.get('channel')

    if CHANNEL_AVAILABILITY.get(ChannelType(channel), False):
        logger.info(f"[traceId: {trace_id}] Canal '{channel}' validado com sucesso.")
        await rabbitmq_service.publish_message(data, "dispatch_queue", exchange_name="dispatch_queue_exchange")
    else:
        logger.warning(f"[traceId: {trace_id}] Canal '{channel}' indisponível. Falha na validação.")
        storage.set_status(trace_id, "ValidationFailed")

async def dispatch_notification(data: dict, rabbitmq_service: RabbitMQService):
    trace_id = data.get("traceId")
    logger.info(f"[traceId: {trace_id}] Iniciando despacho.")
    storage.set_status(trace_id, "Dispatching")
    
    await asyncio.sleep(2) # Simular tempo de processamento

    channel = data.get('channel')
    # A tarefa 'send_notification' será responsável por escolher a fila correta
    await rabbitmq_service.publish_message(data, f"{channel}_queue", exchange_name=f"{channel}_queue_exchange")
    logger.info(f"[traceId: {trace_id}] Despacho para envio iniciado.")

async def send_notification(data: dict, rabbitmq_service: RabbitMQService):
    trace_id = data.get("traceId")
    channel = data.get('channel')
    logger.info(f"[traceId: {trace_id}] Enviando notificação via '{channel}'.")
    storage.set_status(trace_id, "Sending")

    await asyncio.sleep(3) # Simular tempo de envio

    # Simulação de sucesso
    logger.info(f"[traceId: {trace_id}] Notificação enviada com sucesso.")
    # Atualiza o status final
    await rabbitmq_service.publish_message({"traceId": trace_id, "status": "Sent"}, "status_update_queue", exchange_name="status_update_queue_exchange")

async def update_status(data: dict, rabbitmq_service: RabbitMQService):
    trace_id = data.get("traceId")
    final_status = data.get("status") # Assuming the status is passed as "status" in the dict
    logger.info(f"[traceId: {trace_id}] Atualizando estado final para '{final_status}'.")
    storage.set_status(trace_id, final_status)
    logger.info(f"[traceId: {trace_id}] Processo concluído.")
