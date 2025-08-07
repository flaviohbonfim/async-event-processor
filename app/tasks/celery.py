from celery import Celery
from kombu import Queue
from app.core.config import settings
from app.schemas.message import ChannelType

celery_app = Celery(
    "rabbitmq_fastapi_project",
    broker=f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASS}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}//",
    backend="rpc://",
    include=['app.tasks.message_tasks']  # Garantir que as tarefas sejam encontradas
)

# --- Definição das Filas ---
# Filas para cada fase do pipeline
pipeline_queues = [
    Queue('validation_queue', routing_key='validation_queue'),
    Queue('dispatch_queue', routing_key='dispatch_queue'),
    Queue('status_update_queue', routing_key='status_update_queue'),
]

# Filas para cada canal de comunicação
channel_queues = [
    Queue(f'{channel.value}_queue', routing_key=f'{channel.value}_queue') 
    for channel in ChannelType
]

celery_app.conf.task_queues = (
    *pipeline_queues,
    *channel_queues,
)

# --- Roteamento de Tarefas ---
celery_app.conf.task_routes = {
    # Roteamento das fases do pipeline
    'tasks.validate_notification': {'queue': 'validation_queue'},
    'tasks.dispatch_notification': {'queue': 'dispatch_queue'},
    'tasks.update_status': {'queue': 'status_update_queue'},
    
    # Roteamento genérico para a tarefa de envio
    # Como o nome da fila é dinâmico, o produtor especifica a fila diretamente.
    # No entanto, podemos definir um roteamento para a tarefa de envio para todas as filas de canal.
    'tasks.send_notification': {
        'queue': 'email_queue'
    },  # A fila aqui é apenas um padrão
}


# --- Configurações Adicionais ---
celery_app.conf.update(
    task_track_started=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
)

# Optional: Autodiscover tasks in specified modules
celery_app.autodiscover_tasks(['app.tasks'])