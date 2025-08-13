import random
import asyncio
import logging
from app.core import storage
from app.schemas.message import ChannelType
from app.services.rabbitmq import RabbitMQService
from app.core.config import settings

logger = logging.getLogger(__name__)

# Simulação de um serviço de gestão de canais
CHANNEL_AVAILABILITY = {
    ChannelType.EMAIL: True,
    ChannelType.SMS: True,
    ChannelType.PUSH: False,  # Simular canal indisponível
    ChannelType.WHATSAPP: True,
}

async def process_initial_notification(data: dict, rabbitmq_service: RabbitMQService):
    trace_id = data.get("traceId")
    mensagem_id = data.get("mensagemId")
    conteudo_mensagem = data.get("conteudoMensagem")
    tipo_notificacao = data.get("tipoNotificacao")

    logger.info(f"[traceId: {trace_id}] Consumidor 1: Processador de Entrada - Iniciando processamento.")
    storage.set_status(trace_id, "RECEBIDO") # Initial status as per requirement

    # Simulação de Falha Aleatória (10-15%)
    if random.random() < 0.15: # 15% chance of failure
        logger.warning(f"[traceId: {trace_id}] Consumidor 1: Falha simulada no processamento inicial.")
        storage.set_status(trace_id, "FALHA_PROCESSAMENTO_INICIAL")
        await rabbitmq_service.publish_message(
            data,
            settings.NOTIFICATION_RETRY_QUEUE,
            exchange_name=f"{settings.NOTIFICATION_RETRY_QUEUE}_exchange"
        )
        logger.info(f"[traceId: {trace_id}] Mensagem enviada para fila de retry: {settings.NOTIFICATION_RETRY_QUEUE}")
    else:
        logger.info(f"[traceId: {trace_id}] Consumidor 1: Processamento inicial bem-sucedido.")
        await asyncio.sleep(random.uniform(1, 1.5)) # Simular processamento
        storage.set_status(trace_id, "PROCESSADO_INTERMEDIARIO")
        await rabbitmq_service.publish_message(
            data,
            settings.NOTIFICATION_VALIDATION_QUEUE,
            exchange_name=f"{settings.NOTIFICATION_VALIDATION_QUEUE}_exchange"
        )
        logger.info(f"[traceId: {trace_id}] Mensagem enviada para fila de validação: {settings.NOTIFICATION_VALIDATION_QUEUE}")

async def process_retry_notification(data: dict, rabbitmq_service: RabbitMQService):
    trace_id = data.get("traceId")
    logger.info(f"[traceId: {trace_id}] Consumidor 2: Processador de Retries - Iniciando reprocessamento.")
    
    await asyncio.sleep(3) # Simular atraso antes do reprocessamento

    # Tentar reprocessar: Introduzir uma nova chance de falha aleatória (20%)
    if random.random() < 0.20: # 20% chance of failure
        logger.warning(f"[traceId: {trace_id}] Consumidor 2: Falha simulada no reprocessamento.")
        storage.set_status(trace_id, "FALHA_FINAL_REPROCESSAMENTO")
        await rabbitmq_service.publish_message(
            data,
            settings.NOTIFICATION_DLQ,
            exchange_name=f"{settings.NOTIFICATION_DLQ}_exchange"
        )
        logger.info(f"[traceId: {trace_id}] Mensagem enviada para DLQ: {settings.NOTIFICATION_DLQ}")
    else:
        logger.info(f"[traceId: {trace_id}] Consumidor 2: Reprocessamento bem-sucedido.")
        storage.set_status(trace_id, "REPROCESSADO_COM_SUCESSO")
        await rabbitmq_service.publish_message(
            data,
            settings.NOTIFICATION_VALIDATION_QUEUE,
            exchange_name=f"{settings.NOTIFICATION_VALIDATION_QUEUE}_exchange"
        )
        logger.info(f"[traceId: {trace_id}] Mensagem enviada para fila de validação após retry: {settings.NOTIFICATION_VALIDATION_QUEUE}")

async def process_final_notification(data: dict, rabbitmq_service: RabbitMQService):
    trace_id = data.get("traceId")
    tipo_notificacao = data.get("channel") # Corrected to use 'channel' key
    logger.info(f"[traceId: {trace_id}] Consumidor 3: Processador de Validação/Envio Final - Iniciando envio para '{tipo_notificacao}'.")
    storage.set_status(trace_id, "Validating/Sending")

    await asyncio.sleep(random.uniform(0.5, 1)) # Simular tempo de envio

    # Introduzir uma chance de falha de envio (5%)
    if random.random() < 0.05: # 5% chance of failure
        logger.warning(f"[traceId: {trace_id}] Consumidor 3: Falha simulada no envio final para '{tipo_notificacao}'.")
        storage.set_status(trace_id, "FALHA_ENVIO_FINAL")
        await rabbitmq_service.publish_message(
            data,
            settings.NOTIFICATION_DLQ,
            exchange_name=f"{settings.NOTIFICATION_DLQ}_exchange"
        )
        logger.info(f"[traceId: {trace_id}] Mensagem enviada para DLQ: {settings.NOTIFICATION_DLQ}")
    else:
        logger.info(f"[traceId: {trace_id}] Consumidor 3: Envio final para '{tipo_notificacao}' bem-sucedido.")
        storage.set_status(trace_id, "ENVIADO_SUCESSO")
        # No need to publish to status_update_queue here, as status is directly updated.
        # If a separate system needs to be notified of final success, this could be a place for it.

async def process_dlq_message(data: dict, rabbitmq_service: RabbitMQService):
    trace_id = data.get("traceId")
    logger.error(f"[traceId: {trace_id}] Consumidor 4: Dead Letter Queue (DLQ) - Mensagem recebida na DLQ. Não será mais processada.")
    # Log the message and its traceId, indicating it's in DLQ
    logger.error(f"DLQ Message Details: {data}")
    storage.set_status(trace_id, "DLQ_RECEIVED") # Optional: update status to reflect DLQ reception

# The original validate_notification, dispatch_notification, send_notification, update_status are no longer needed
# or will be refactored into the new functions above.
# Keeping them commented out for now to show the transition.

# async def validate_notification(data: dict, rabbitmq_service: RabbitMQService):
#     trace_id = data.get("traceId")
#     logger.info(f"[traceId: {trace_id}] Iniciando validação.")
#     storage.set_status(trace_id, "Validating")

#     await asyncio.sleep(2)  # Simular tempo de processamento

#     channel = data.get('channel')

#     if CHANNEL_AVAILABILITY.get(ChannelType(channel), False):
#         logger.info(f"[traceId: {trace_id}] Canal '{channel}' validado com sucesso.")
#         await rabbitmq_service.publish_message(data, "dispatch_queue", exchange_name="dispatch_queue_exchange")
#     else:
#         logger.warning(f"[traceId: {trace_id}] Canal '{channel}' indisponível. Falha na validação.")
#         storage.set_status(trace_id, "ValidationFailed")

# async def dispatch_notification(data: dict, rabbitmq_service: RabbitMQService):
#     trace_id = data.get("traceId")
#     logger.info(f"[traceId: {trace_id}] Iniciando despacho.")
#     storage.set_status(trace_id, "Dispatching")
    
#     await asyncio.sleep(2) # Simular tempo de processamento

#     channel = data.get('channel')
#     # A tarefa 'send_notification' será responsável por escolher a fila correta
#     await rabbitmq_service.publish_message(data, f"{channel}_queue", exchange_name=f"{channel}_queue_exchange")
#     logger.info(f"[traceId: {trace_id}] Despacho para envio iniciado.")

# async def send_notification(data: dict, rabbitmq_service: RabbitMQService):
#     trace_id = data.get("traceId")
#     channel = data.get('channel')
#     logger.info(f"[traceId: {trace_id}] Enviando notificação via '{channel}'.")
#     storage.set_status(trace_id, "Sending")

#     await asyncio.sleep(3) # Simular tempo de envio

#     # Simulação de sucesso
#     logger.info(f"[traceId: {trace_id}] Notificação enviada com sucesso.")
#     # Atualiza o status final
#     await rabbitmq_service.publish_message({"traceId": trace_id, "status": "Sent"}, "status_update_queue", exchange_name="status_update_queue_exchange")

# async def update_status(data: dict, rabbitmq_service: RabbitMQService):
#     trace_id = data.get("traceId")
#     final_status = data.get("status") # Assuming the status is passed as "status" in the dict
#     logger.info(f"[traceId: {trace_id}] Atualizando estado final para '{final_status}'.")
#     storage.set_status(trace_id, final_status)
#     logger.info(f"[traceId: {trace_id}] Processo concluído.")
