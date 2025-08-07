# Sistema de Notificações Assíncronas com FastAPI e RabbitMQ

Este projeto implementa um backend para envio e processamento assíncrono de notificações usando FastAPI, Celery e RabbitMQ, conforme especificações do teste técnico.

## Funcionalidades
- **Endpoint POST /api/notificar**: Recebe payload com mensagemId, conteudoMensagem, tipoNotificacao; gera traceId; armazena em memória com status 'RECEBIDO'; publica na fila de entrada.
- **Pipeline de Processamento**: Consumidores para processamento inicial (com falha aleatória), retry, validação/envio (com falha), e DLQ.
- **Endpoint GET /api/notificacao/status/{traceId}**: Retorna detalhes da notificação incluindo status.
- **Armazenamento**: Em memória, com thread safety.
- **Testes**: Cobertura para criação, status e mocks para RabbitMQ.

## Requisitos Atendidos
- Configuração com FastAPI e aio-pika.
- Validação via Pydantic.
- Pipeline com falhas simuladas, retry e DLQ (após correções).
- Testes com pytest e mocks.

## Pendências
- Implementar simulações de falha e consumidores para retry/DLQ.
- Ajustar nomes de filas para incluir [SEU-NOME].

## Configuração
1. Instale Poetry: `pip install poetry`
2. Instale dependências: `poetry install`
3. Crie .env com credenciais RabbitMQ.

## Execução
- Com Docker: `docker compose up --build`
- Testes: `poetry run pytest`

## Debugging e Deploy
- Utilize `docker compose up --build` para desenvolvimento.
- Para deploy, considere utilizar um serviço de orquestração como Kubernetes.
