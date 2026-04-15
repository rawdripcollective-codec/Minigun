# ---- build stage ----
FROM python:3.11-slim AS builder

WORKDIR /build

COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir build && \
    pip install --no-cache-dir fastapi uvicorn pydantic pydantic-settings httpx

# ---- runtime stage ----
FROM python:3.11-slim AS runtime

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin
COPY minigun/ ./minigun/
COPY pyproject.toml ./

# Install the package in non-editable mode
RUN pip install --no-cache-dir .

EXPOSE 8000

ENV MINIGUN_LOG_LEVEL=INFO
ENV MINIGUN_API_SECRET_KEY=changeme

CMD ["uvicorn", "minigun.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
