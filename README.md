# Sistema de Notificações Assíncronas com FastAPI e RabbitMQ

Este projeto implementa um backend para envio e processamento assíncrono de notificações usando FastAPI e RabbitMQ, conforme especificações do teste técnico.

## Funcionalidades
- **Endpoint POST /api/notificar**: Recebe payload com `mensagemId`, `conteudoMensagem`, `tipoNotificacao`; gera `traceId`; armazena em memória com status 'RECEBIDO'; publica na fila de entrada.
- **Pipeline de Processamento Assíncrono**: Utiliza consumidores assíncronos para processamento de mensagens, incluindo:
    - **Processamento Inicial**: Consumidores que simulam falhas aleatórias.
    - **Mecanismo de Retry**: Mensagens que falham no processamento inicial são automaticamente reenviadas para reprocessamento.
    - **Validação e Envio**: Etapa final de processamento que pode simular falhas.
    - **Dead Letter Queue (DLQ)**: Mensagens que excedem o número de retries são movidas para uma fila de DLQ para análise posterior.
- **Endpoint GET /api/notificacao/status/{traceId}**: Retorna detalhes da notificação, incluindo seu status atual no pipeline de processamento.
- **Armazenamento em Memória**: Utiliza um armazenamento em memória thread-safe para manter o estado das notificações.
- **Testes Abrangentes**: Cobertura de testes para a API (criação e status de notificações) e para os consumidores, com mocks para a integração com RabbitMQ.

## Requisitos Atendidos
- Configuração robusta com FastAPI e integração com RabbitMQ para tarefas assíncronas.
- Validação de dados de entrada e saída via Pydantic.
- Implementação completa do pipeline de processamento com simulações de falha, retry automático e Dead Letter Queue (DLQ).
- Testes unitários e de integração utilizando pytest e mocks para garantir a qualidade e confiabilidade do sistema.
- Armazenamento em memória com garantia de thread safety.

## Configuração
1. Instale Poetry: `pip install poetry`
2. Instale dependências: `poetry install`
3. Crie um arquivo `.env` na raiz do projeto com as credenciais do RabbitMQ. Exemplo:
   ```
   RABBITMQ_DEFAULT_USER=guest
   RABBITMQ_DEFAULT_PASS=guest
   RABBITMQ_HOST=localhost
   RABBITMQ_PORT=5672
   ```

## Execução
- **Com Docker Compose (recomendado para desenvolvimento)**:
  ```bash
  docker compose up --build
  ```
  Isso irá levantar o FastAPI, os consumidores e o RabbitMQ.
- **Execução manual (para desenvolvimento ou depuração específica)**:
  1. Inicie o RabbitMQ (se não estiver usando Docker Compose).
  2. Inicie o FastAPI:
     ```bash
     poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
     ```
  3. Inicie os consumidores:
     ```bash
     poetry run python -m app.worker
     ```

## Testes
Para executar os testes:
```bash
poetry run pytest
```

## Debugging e Deploy
- Para desenvolvimento e depuração, utilize `docker compose up --build`.
- Para deploy em produção, considere utilizar um serviço de orquestração como Kubernetes, configurando o escalonamento do FastAPI e dos consumidores, além de um serviço de mensageria gerenciado.

## Contato
Para dúvidas ou sugestões, entre em contato.
