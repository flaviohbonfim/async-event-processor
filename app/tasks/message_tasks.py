import random
import asyncio
import logging
from app.core import storage
from app.services.rabbitmq import RabbitMQService
from app.core.config import settings

logger = logging.getLogger(__name__)

async def process_initial_notification(data: dict, rabbitmq_service: RabbitMQService):
    trace_id = data.get("traceId")

    logger.info(f"[traceId: {trace_id}] Consumidor 1: Processador de Entrada - Iniciando processamento.")
    storage.set_status(trace_id, "RECEBIDO")

    if random.random() < 0.15:
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
        await asyncio.sleep(random.uniform(1, 1.5))
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
    
    await asyncio.sleep(3)

    if random.random() < 0.20:
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
    tipo_notificacao = data.get("channel")
    logger.info(f"[traceId: {trace_id}] Consumidor 3: Processador de Validação/Envio Final - Iniciando envio para '{tipo_notificacao}'.")
    storage.set_status(trace_id, "Validating/Sending")

    await asyncio.sleep(random.uniform(0.5, 1))

    if random.random() < 0.05:
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

async def process_dlq_message(data: dict, rabbitmq_service: RabbitMQService):
    trace_id = data.get("traceId")
    logger.error(f"[traceId: {trace_id}] Consumidor 4: Dead Letter Queue (DLQ) - Mensagem recebida na DLQ. Não será mais processada.")
    logger.error(f"DLQ Message Details: {data}")
    storage.set_status(trace_id, "DLQ_RECEIVED")
