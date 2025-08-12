FROM python:3.10-slim-buster

# Desativa prompts interativos do poetry
ENV POETRY_NO_INTERACTION=1

# Instrui o poetry a não criar o ambiente virtual dentro da pasta do projeto
ENV POETRY_VIRTUALENVS_IN_PROJECT=false

# Define a localização do ambiente virtual do poetry
ENV POETRY_HOME="/opt/poetry"

# Adiciona o poetry ao PATH do sistema
ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app

# Instala o poetry
RUN pip install poetry

# Copia os ficheiros de dependência
COPY poetry.lock pyproject.toml ./

# Instala as dependências de produção
RUN poetry install --no-root

# Copia o código da aplicação
COPY . .

# Comando por defeito para correr a aplicação FastAPI
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]