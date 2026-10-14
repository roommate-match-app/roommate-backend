# КакДостатьСоседа - Backend

Бэкенд приложения для поиска соседа, написанный на FastAPI.

Стек: Python, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, PostgreSQL 16, Docker.

## Структура проекта

```
app/
  main.py                 # сборка FastAPI-приложения и подключение роутеров
  core/
    config.py             # настройки (pydantic-settings)
    security.py           # bcrypt-хеширование и JWT
  db/
    database.py           # engine, SessionLocal, Base, get_db
    DB.sql                # справка: DDL-схема (генерируется из моделей)
    seed.sql              # демонстрационные данные
    models/               # ORM-модели (20 таблиц)
    schemas/              # Pydantic-DTO
  api/
    deps.py               # зависимости (текущий пользователь/анкета)
    routers/              # HTTP-роутеры по разделам UC
  services/
    matching.py           # расчёт совместимости анкет
    notifications.py      # создание уведомлений
migrations/               # Alembic
tests/                    # pytest-тесты (SQLite, без внешней БД)
Dockerfile                # образ API
docker-compose.yml        # postgres + api
```

## Локальный запуск

1. Создайте виртуальное окружение: `python -m venv venv`
2. Активируйте его:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
3. Установите зависимости: `pip install -r requirements.txt` (для тестов — `pip install -r requirements-dev.txt`)
4. Скопируйте `.env.example` в `.env` и задайте `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`.

### Вариант A: всё через Docker (рекомендуется)

```bash
docker compose up --build
```

Поднимаются PostgreSQL и API; миграции применяются автоматически при старте контейнера.
Swagger доступен на [http://localhost:8000/docs](http://localhost:8000/docs).

Загрузите демо-данные в пустую БД (из каталога `roommate-backend`):

```powershell
# PowerShell (Windows): оператор "<" не поддерживается — используйте конвейер
Get-Content -Raw app/db/seed.sql | docker exec -i roommate_postgres psql -U roommate_user -d roommate_db
```

```bash
# bash / macOS / Linux
docker exec -i roommate_postgres psql -U roommate_user -d roommate_db < app/db/seed.sql
```

> `seed.sql` создан для пустой БД. Повторный запуск приведёт к ошибкам дублирования ключей —
> чтобы перезагрузить данные с нуля, выполните `docker compose down -v && docker compose up --build`.

#### Демо-данные к существующему аккаунту (`seed_demo.sql`)

`app/db/seed_demo.sql` дополняет уже работающую БД: 22 анкеты с уникальными фото (Pinterest),
8 объявлений о жилье и переписки от разных людей с текущим пользователем
(по умолчанию `aleksejsolakov@gmail.com`, иначе — первый зарегистрированный аккаунт).
Файл не конфликтует с `seed.sql` и требует наличия пользователя в БД.

Изображения анкет и объявлений хранятся **локально** в каталоге загрузок (`uploads`,
том `uploads_data`, раздаётся бэкендом по `/media`). Ссылки в БД имеют вид `/media/<имя>`.
Скачать демонстрационные изображения в каталог загрузок можно скриптом:

```bash
# из каталога roommate-backend (требуется доступ к Pinterest)
python scripts/seed_media.py
```

```powershell
# PowerShell (Windows)
docker cp app/db/seed_demo.sql roommate_postgres:/tmp/seed_demo.sql
docker exec roommate_postgres psql -U roommate_user -d roommate_db -v ON_ERROR_STOP=1 -f /tmp/seed_demo.sql
```

```bash
# bash / macOS / Linux
docker cp app/db/seed_demo.sql roommate_postgres:/tmp/seed_demo.sql
docker exec roommate_postgres psql -U roommate_user -d roommate_db -v ON_ERROR_STOP=1 -f /tmp/seed_demo.sql
```

Повторный запуск приведёт к дублированию ключей — сначала удалите демо-данные:
`DELETE FROM notifications WHERE id::text LIKE 'd9%'; DELETE FROM users WHERE id::text LIKE 'd0000000-%';`
(остальные записи удаляются каскадно).

### Горячая перезагрузка бэкенда (dev)

`docker-compose.override.yml` (подключается автоматически при `docker compose up`) монтирует исходники
в контейнер и запускает `uvicorn --reload`, поэтому правки `.py` подхватываются **без пересборки образа** —
достаточно сохранить файл. Пересборка (`docker compose up -d --build`) нужна только при изменении
`requirements.txt`, `Dockerfile` или `.env`. На Windows включён polling (`WATCHFILES_FORCE_POLLING=true`)
для надёжного отслеживания изменений. Этот файл предназначен только для локальной разработки.

### Вариант B: локальный запуск API

5. Поднимите только БД: `docker compose up -d db`
6. Примените миграции: `alembic upgrade head`
7. (Опционально) Загрузите демо-данные: `psql "$env:DATABASE_URL" -f app/db/seed.sql`
8. Запустите сервер: `uvicorn app.main:app --reload`

### Настройки (`.env`)

| Переменная | Назначение |
| :--- | :--- |
| `DATABASE_URL` | Строка подключения к PostgreSQL |
| `SECRET_KEY` | Секрет для подписи JWT. **Обязателен** для `docker compose` (читается из `.env`). Сгенерировать: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` | Параметры JWT |
| `CORS_ORIGINS` | Разрешённые источники: через запятую или JSON-массив |

## Миграции (Alembic)

* Применить схему: `alembic upgrade head`
* Откатить последнюю: `alembic downgrade -1`
* Создать новую миграцию: `alembic revision --autogenerate -m "описание"`

Источник истины по схеме — ORM-модели `app/db/models/models.py` и миграции Alembic.
Файл `app/db/DB.sql` носит справочный характер.

## Тесты

```
python -m pytest -q
```

Тесты выполняются на SQLite и не требуют запущенного PostgreSQL.
Интеграционный тест `tests/test_scenario.py` проходит сквозной сценарий UC-1..UC-10.

## Пользователи демо-данных

Пароль всех пользователей из `seed.sql`: `password123`
`alice@example.com`, `bob@example.com`, `carol@example.com`, `admin@example.com`.

## API Документация (Контракты)

После запуска сервера интерактивная документация (Swagger UI) доступна по адресу:
[http://localhost:8000/docs](http://localhost:8000/docs)

Основные разделы API (порядок соответствует Use Cases):

| Префикс | Назначение |
| :--- | :--- |
| `POST /api/auth/register`, `/login`, `/refresh` | Регистрация, вход, обновление access-токена (UC-1) |
| `/api/profiles` | Анкета, привычки, предпочтения (UC-2..UC-4) |
| `/api/candidates` | Подбор анкет с фильтрами и совместимостью (UC-5) |
| `/api/likes`, `/api/matches` | Лайки и совпадения (UC-6) |
| `/api/chats` (+ `/unread-count`, WebSocket) | Чат, сообщения, счётчик непрочитанного (UC-7) |
| `/api/notifications` (+ `/unread-count`) | Уведомления (UC-8) |
| `/api/reviews`, `/api/users/{id}` | Отзывы и рейтинг (UC-9) |
| `/api/announcements`, `/api/applications` | Объявления и заявки (UC-10) |
| `/api/uploads` (+ `/media`) | Загрузка и раздача изображений |
| `/api/favorites`, `/api/complaints` | Избранное и жалобы |
| `/api/admin` | Модерация: пользователи, жалобы, объявления (роль `admin`) |
| `GET /health`, `/health/db` | Проверки живости и доступности БД |

## Артефакты для фронтенда

Экспорт OpenAPI-схемы для генерации типов и mock-сервера:

```bash
python -m scripts.export_openapi          # создаёт openapi.json
npx openapi-typescript openapi.json -o src/api/schema.d.ts
```

Токены: `POST /api/auth/login` возвращает `access_token` и `refresh_token`;
обновление — `POST /api/auth/refresh`.

## Линт и тесты

```bash
python -m ruff check .
python -m pytest -q
```

CI (GitHub Actions) прогоняет линт и тесты на SQLite, а также применяет миграции и
загружает `seed.sql` на PostgreSQL.

## Хранение данных и запуск в продакшене

### Где хранятся данные

| Данные | Где | Переживает пересоздание контейнера |
| :--- | :--- | :--- |
| Пользователи, анкеты, лайки, совпадения, чаты, объявления, отзывы | PostgreSQL в томе `postgres_data` | ✅ да |
| Загруженные фото (`/api/uploads`, раздаются по `/media`) | том `uploads_data` → `/app/uploads` | ✅ да |
| Секреты (`SECRET_KEY`, `DATABASE_URL`, `CORS_ORIGINS`) | файл `.env` (не в git) | ✅ да |

Тома создаёт Docker Compose автоматически. Удалить данные можно только явно:
`docker compose down -v` (удаляет том `postgres_data`). Обычный `docker compose down` и пересоздание
контейнеров данные и фото сохраняют.

### Резервное копирование

```bash
docker exec roommate_postgres pg_dump -U roommate_user roommate_db > backup.sql
# восстановление (на чистой БД после `alembic upgrade head`):
cat backup.sql | docker exec -i roommate_postgres psql -U roommate_user -d roommate_db
```

### Требования к серверу

- Linux с Docker Engine и Docker Compose v2.
- Домен и reverse-proxy (nginx/Caddy) для HTTPS.
- `.env` с сильным `SECRET_KEY` и продакшн-`CORS_ORIGINS` (домен фронтенда; можно JSON-массивом).

### Запуск на сервере

```bash
git clone <repo> && cd roommate-backend
cp .env.example .env            # задать SECRET_KEY и CORS_ORIGINS
docker compose up -d --build    # миграции (alembic upgrade head) применяются при старте api
```

> `docker-compose.override.yml` предназначен **только для локальной разработки** (публикует порт
> PostgreSQL `5432` на хост). На прод-сервер его переносить не нужно — тогда БД недоступна извне.

### Обновление версии

```bash
git pull
docker compose up -d --build    # пересборка образа + применение новых миграций
```

Секреты и порты: `5432` публикуется только в dev; `8000` открывайте через reverse-proxy, не напрямую.