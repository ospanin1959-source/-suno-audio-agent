# Suno Audio Agent

FastAPI-сервис для генерации музыкальных планов через Qwen и создания треков через Suno API.

## Возможности

- **GET /** — healthcheck, показывает статус настройки Suno API
- **POST /prompt** — создаёт музыкальный план (title, style_prompt, lyrics, tags) через Qwen
- **POST /generate** — создаёт план через Qwen и отправляет в Suno API, возвращает job_id
- **GET /status/{job_id}** — возвращает статус генерации из Suno API

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Скопируйте `.env.example` в `.env` и заполните ключи:
```bash
cp .env.example .env
```

3. Отредактируйте `.env`:
```
QWEN_API_KEY=your_qwen_api_key
QWEN_BASE_URL=https://api.qwen.ai/v1
QWEN_MODEL=qwen-max

SUNO_API_BASE=https://api.suno.ai
SUNO_API_KEY=your_suno_api_key
```

## Запуск

```bash
uvicorn main:app --reload
```

Сервер запустится на `http://localhost:8000`.

## Примеры запросов

### Healthcheck
```bash
curl http://localhost:8000/
```

### Создать музыкальный план
```bash
curl -X POST http://localhost:8000/prompt \
  -H "Content-Type: application/json" \
  -d '{"text": "тёмный synthwave про ночной город", "instrumental": true, "duration_sec": 180}'
```

### Сгенерировать трек
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "тёмный synthwave про ночной город", "instrumental": true}'
```

### Проверить статус
```bash
curl http://localhost:8000/status/{job_id}
```

## Режим без Suno API

Если переменные `SUNO_API_BASE` и `SUNO_API_KEY` не заданы:
- `/` вернёт `suno_configured: false`
- `/prompt` будет работать (только Qwen)
- `/generate` и `/status` вернут 503 Service Unavailable
