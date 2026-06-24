# Сервис асинхронной обработки платежей

FastAPI + PostgreSQL + RabbitMQ (FastStream). Принимает платежи, обрабатывает через эмуляцию шлюза и уведомляет через webhook.

## Запуск

```bash
cp .env.example .env
docker compose up --build
```

API: `http://localhost:8000` · Swagger UI: `http://localhost:8000/docs` · RabbitMQ UI: `http://localhost:15672` (guest/guest)

Миграции применяются автоматически. Переменные окружения берутся из `.env`.

## API

Все запросы требуют заголовок `X-API-Key`.

### POST /api/v1/payments

Заголовки: `X-API-Key`, `Idempotency-Key` (обязательный, защита от дублей).

```bash
curl -X POST http://localhost:8000/api/v1/payments \
  -H "Content-Type: application/json" \
  -H "X-API-Key: secret-api-key" \
  -H "Idempotency-Key: order-123" \
  -d '{"amount": "500.00", "currency": "RUB", "description": "Тест", "webhook_url": "https://example.com/webhook"}'
```

Ответ `202 Accepted`: `payment_id`, `status: pending`, `created_at`.

### GET /api/v1/payments/{payment_id}

```bash
curl http://localhost:8000/api/v1/payments/<payment_id> -H "X-API-Key: secret-api-key"
```

Ответ: полная информация о платеже включая `status` и `processed_at`.

## Как работает

```
POST /payments
  └─ INSERT payment + outbox (одна транзакция)

Relay worker (каждые 5с)
  └─ outbox pending → publish → payments.new → outbox sent

Consumer
  └─ получает сообщение
  └─ эмулирует шлюз (2-5с, 90% успех / 10% ошибка)
  └─ UPDATE payment.status
  └─ отправляет webhook (retry x3, exponential backoff)
  └─ при 3 ошибках → DLQ (payments.dead)
```

**Outbox pattern** гарантирует атомарность: платёж и событие записываются в одной транзакции — брокер получит сообщение даже при падении сервиса.
