FROM python:3

WORKDIR /app

COPY uv.lock pyproject.toml .

RUN pip install uv
RUN uv sync

COPY . .
