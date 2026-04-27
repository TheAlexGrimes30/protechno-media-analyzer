# ProTechno Media Analyzer

Веб-приложение для медиа-команды: генерация и публикация контента, парсинг внешних источников, базовая аналитика и сборка PDF-отчётов.

Проект состоит из двух частей:

- `backend/` — FastAPI API, интеграции с VK, Google Sheets, Ollama и PostgreSQL.
- `frontend/` — React + Vite интерфейс для календаря, контент-планирования и работы с публикациями.

## Что умеет проект

- генерировать текст поста через Ollama;
- публиковать, удалять и загружать изображения для постов VK;
- парсить посты из VK;
- парсить публикации из Дзена;
- забирать события из публичной Google Sheet;
- оценивать состояние контента по CSV-выгрузке;
- строить PDF-отчёты по данным VK и Дзена;
- показывать frontend-интерфейс с календарём и контентными сценариями.

## Текущее состояние

Проект уже объединяет frontend и backend в одной ветке, но интеграция пока частичная:

- backend хранит данные и интеграции через PostgreSQL и API;
- frontend сценарии авторизации, календаря и части контент-планирования сейчас сохраняются в `localStorage` браузера;
- backend-аутентификация и полноценная серверная модель для календаря/пользователей пока не реализованы.

Это важно учитывать при демонстрации и дальнейшей разработке.

## Стек

- Python 3.10+
- FastAPI
- SQLAlchemy Async + Alembic
- PostgreSQL
- React 19
- Vite
- Ollama
- VK API
- Google Sheets

## Структура проекта

```text
backend/
  app/                 FastAPI app и конфигурация
  db/                  SQLAlchemy модели и подключение к БД
  modules/             API-модули: vk, llm, dzen, report, profiles, condition, sheet_parser
  schemas/             Pydantic-схемы
frontend/
  src/                 React UI
  public/              статические ассеты
alembic/               миграции БД
charts/                графики для PDF-отчётов
start-dev.bat          запуск backend + frontend в dev-режиме
start-prod.bat         production-сценарий: build фронта + FastAPI на одном порту
HOSTING.md             инструкции по LAN/туннелям
```

## Требования

Перед запуском нужны:

- Python 3.10 или новее
- Node.js 20+ и `npm`
- PostgreSQL
- запущенный Ollama, если нужен LLM/отчёт с рекомендациями

## Переменные окружения

В корне проекта нужен файл `.env`.

Минимальный набор:

```env
DB_NAME=protechno
DB_USER=postgres
DB_PASS=postgres
DB_HOST=localhost
DB_PORT=5432

ACCESS_TOKEN=vk_group_token
GROUP_ID=123456789

GOOGLE_SHEET_ID=your_google_sheet_id
GOOGLE_SHEET_GID=0
GOOGLE_WORKSHEET_NAME=0
GOOGLE_CREDENTIALS_PATH=service_account.json

OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
OLLAMA_TIMEOUT=120
```

Дополнительно для frontend:

```env
VITE_API_BASE_URL=
VITE_EMAILJS_SERVICE_ID=
VITE_EMAILJS_TEMPLATE_ID=
VITE_EMAILJS_PUBLIC_KEY=
```

Пояснения:

- `VITE_API_BASE_URL` нужен, если frontend собирается отдельно от Vite proxy.
- `VITE_EMAILJS_*` опциональны. Без них регистрация/подтверждение почты во frontend не сможет отправлять реальные письма.
- `GOOGLE_CREDENTIALS_PATH` должен указывать на JSON ключ сервисного аккаунта, если используется Google API сценарий.

## Установка зависимостей

### Backend

```powershell
cd C:\Users\Вадим\protechno-media-analyzer
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend

```powershell
cd C:\Users\Вадим\protechno-media-analyzer\frontend
npm install
```

## Инициализация базы данных

Создай базу PostgreSQL и примени миграции:

```powershell
cd C:\Users\Вадим\protechno-media-analyzer
alembic upgrade head
```

Миграции создают основные таблицы:

- `organizations`
- `users`
- `events`
- `posts`
- `analytics_log`
- `tags`
- `post_tags`
- `system_state`

## Запуск в dev-режиме

Есть два варианта.

### Вариант 1. Через готовый bat-скрипт

```powershell
cd C:\Users\Вадим\protechno-media-analyzer
.\start-dev.bat
```

Скрипт:

- проверяет Python и Node.js;
- при необходимости ставит зависимости;
- поднимает backend на `8000`;
- поднимает frontend на `5173`.

### Вариант 2. Вручную

Backend:

```powershell
cd C:\Users\Вадим\protechno-media-analyzer
python -m backend.app.main
```

Или:

```powershell
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```powershell
cd C:\Users\Вадим\protechno-media-analyzer\frontend
npm run dev
```

После запуска:

- frontend: `http://localhost:5173`
- backend: `http://localhost:8000`
- healthcheck: `http://localhost:8000/health/db`

В dev-режиме Vite проксирует `/api/*` на backend.

## Запуск в production-режиме

```powershell
cd C:\Users\Вадим\protechno-media-analyzer
.\start-prod.bat
```

Этот сценарий:

- собирает frontend;
- задаёт `FRONTEND_DIST`;
- запускает FastAPI на `8000`;
- раздаёт собранный frontend и API с одного порта.

## Основные API endpoints

### VK

- `POST /api/vk/parse` — парсинг стены VK
- `POST /api/vk/poster` — публикация поста
- `POST /api/vk/delete` — удаление поста
- `POST /api/vk/upload-photo` — загрузка изображения в VK

### LLM

- `POST /api/llm/generate` — генерация текста поста через Ollama

### Google Sheets

- `POST /api/sheet_parser/parse` — чтение публичной Google Sheet и сохранение CSV

### Dzen

- `POST /api/dzen_parser/parse` — парсинг публикаций Дзена

### Отчёты и аналитика

- `POST /api/report/generate` — генерация PDF-отчёта
- `POST /api/condition/assess` — оценка состояния по CSV

### Вспомогательное

- `GET /api/profiles/`
- `GET /api/profiles/{name}`
- `GET /health/db`

## Примеры полезных команд

Проверить backend:

```powershell
curl http://localhost:8000/health/db
```

Применить миграции:

```powershell
alembic upgrade head
```

Собрать frontend:

```powershell
cd frontend
npm run build
```

## Работа с Ollama

Если используются генерация постов и рекомендации в отчётах, Ollama должен быть поднят локально:

```powershell
ollama serve
ollama pull qwen2.5:3b
```

Если модель другая, зафиксируй её в `.env` через `OLLAMA_MODEL`.

## LAN и внешний доступ

Для показа с телефона, по локальной сети или через туннель см. [HOSTING.md](./HOSTING.md).

Там уже описаны:

- доступ по LAN-IP;
- dev/prod сценарии;
- Cloudflare Tunnel;
- ngrok;
- firewall Windows.

## Риски и ограничения

- Часть frontend-логики пока не хранится в PostgreSQL и не синхронизируется между пользователями.
- Для работы VK API нужен корректный `ACCESS_TOKEN` и `GROUP_ID`.
- Для LLM-сценариев нужен доступный Ollama.
- Для сценариев с Google может понадобиться сервисный аккаунт и валидный JSON-ключ.
- В репозитории есть артефакты данных и отчётов (`csv`, `pdf`, `charts`), их стоит контролировать отдельно перед релизом.

## Что стоит сделать дальше

- вынести frontend-аутентификацию из `localStorage` в backend;
- добавить `.env.example`;
- разделить demo-данные и production-артефакты;
- добавить тесты для backend API;
- описать сценарии деплоя не только для Windows, но и для Linux/docker.
