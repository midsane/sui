FROM python:3.12

WORKDIR /app

COPY pyproject.toml .
RUN pip install uv

COPY . .
