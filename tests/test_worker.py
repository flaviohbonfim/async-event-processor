import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from app.worker import process_message
from app.services.rabbitmq import RabbitMQService
from app.tasks.message_tasks import (
    process_initial_notification,
    process_retry_notification,
    process_final_notification,
    process_dlq_message,
)
from app.core.config import settings

@pytest.fixture
def mock_rabbitmq_service():
    """Fixture para mockar RabbitMQService."""
    service = AsyncMock(spec=RabbitMQService)
    return service

@pytest.fixture
def mock_incoming_message():
    """Fixture para mockar aio_pika.IncomingMessage."""
    message = MagicMock()
    # Mock the async context manager protocol
    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = None
    mock_context_manager.__aexit__.return_value = None
    message.process.return_value = mock_context_manager
    return message

@pytest.mark.asyncio
async def test_process_message_success(mock_incoming_message, mock_rabbitmq_service, mocker):
    """Testa o processamento bem-sucedido de uma mensagem."""
    test_data = {"traceId": "123", "conteudoMensagem": "Test", "tipoNotificacao": "email"}
    mock_incoming_message.body = json.dumps(test_data).encode()

    # Mock a specific task function
    mock_task_func = mocker.patch('app.tasks.message_tasks.process_initial_notification', new_callable=AsyncMock)

    await process_message(mock_incoming_message, mock_task_func, mock_rabbitmq_service)

    mock_incoming_message.process.assert_called_once()
    mock_task_func.assert_called_once_with(test_data, mock_rabbitmq_service)

@pytest.mark.asyncio
async def test_process_message_error_handling(mock_incoming_message, mock_rabbitmq_service, mocker):
    """Testa o tratamento de erros durante o processamento da mensagem."""
    test_data = {"traceId": "456", "conteudoMensagem": "Error Test", "tipoNotificacao": "sms"}
    mock_incoming_message.body = json.dumps(test_data).encode()

    # Mock the task function to raise an exception
    mock_task_func = mocker.patch('app.tasks.message_tasks.process_initial_notification', new_callable=AsyncMock)
    mock_task_func.side_effect = Exception("Simulated task error")

    # Mock logging to check if error is logged
    mock_logger_error = mocker.patch('app.worker.logger.error')

    await process_message(mock_incoming_message, mock_task_func, mock_rabbitmq_service)

    mock_incoming_message.process.assert_called_once()
    mock_task_func.assert_called_once_with(test_data, mock_rabbitmq_service)
    mock_logger_error.assert_called_once()
    assert "Error processing message" in mock_logger_error.call_args[0][0]

@pytest.mark.asyncio
async def test_process_message_invalid_json(mock_incoming_message, mock_rabbitmq_service, mocker):
    """Testa o tratamento de mensagem com JSON inválido."""
    mock_incoming_message.body = b"invalid json"

    mock_task_func = mocker.patch('app.tasks.message_tasks.process_initial_notification', new_callable=AsyncMock)
    mock_logger_error = mocker.patch('app.worker.logger.error')

    await process_message(mock_incoming_message, mock_task_func, mock_rabbitmq_service)

    mock_incoming_message.process.assert_called_once() # Message should still be processed/acked
    mock_task_func.assert_not_called() # Task function should not be called
    mock_logger_error.assert_called_once()
    assert "Error processing message" in mock_logger_error.call_args[0][0]
    assert "Expecting value" in mock_logger_error.call_args[0][0] # More specific to JSONDecodeError message

# You can add more specific tests for each task function if needed,
# but the focus here is on the worker's message processing logic.
