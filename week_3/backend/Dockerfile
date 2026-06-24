FROM python:3.14.4-bookworm

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY src ./src

ENTRYPOINT ["uv", "run", "uvicorn"]
CMD ["--app-dir", "src", "--host", "0.0.0.0", "--port", "8001", "--access-log", "--log-level", "info", "app:app"]