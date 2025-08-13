from fastapi.testclient import TestClient
import uuid
import pytest

from app.main import app
from app.core import storage

@pytest.fixture(autouse=True)
def clear_storage_before_each_test():
    """Garante que o armazenamento em memória esteja limpo antes de cada teste."""
    storage.clear_storage()
    yield

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_notification_success(mocker):
    notification_data = {
        "conteudoMensagem": "Olá Mundo!",
        "tipoNotificacao": "email"
    }

    mock_publish = mocker.patch('app.services.rabbitmq.RabbitMQService.publish_message')
    response = client.post("/api/notificar", json=notification_data)

    assert response.status_code == 202
    response_json = response.json()
    trace_id = response_json["traceId"]
    mensagem_id = response_json["mensagemId"]

    stored_data = storage.get_notification(str(trace_id))
    assert stored_data["status"] == "RECEBIDO"
    assert str(stored_data["mensagemId"]) == str(mensagem_id)
    assert stored_data["conteudoMensagem"] == notification_data["conteudoMensagem"]
    assert stored_data["channel"] == notification_data["tipoNotificacao"]
    mock_publish.assert_called_once()

def test_get_notification_status():
    trace_id = uuid.uuid4()
    data = {
        "mensagemId": str(uuid.uuid4()),
        "conteudoMensagem": "Teste",
        "tipoNotificacao": "sms",
        "status": "Sent",
        "traceId": str(trace_id) # Add traceId to the stored data
    }
    storage.set_notification(str(trace_id), data)

    response = client.get(f"/api/notificacao/status/{trace_id}")

    assert response.status_code == 200
    assert response.json() == {
        "traceId": str(trace_id),
        "mensagemId": str(data["mensagemId"]),
        "conteudoMensagem": data["conteudoMensagem"],
        "tipoNotificacao": data["tipoNotificacao"],
        "status": data["status"]
    }

def test_get_notification_status_not_found():
    non_existent_id = str(uuid.uuid4())
    response = client.get(f"/api/notificacao/status/{non_existent_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Notification not found"}
