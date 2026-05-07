# FastAPI Shop

A production-ready online shop REST API built with **FastAPI**, **Clean Architecture**, and **PostgreSQL**.

## Features

- **RBAC** — three roles: `USER`, `MANAGER`, `ADMIN`
- **Products** — CRUD, soft-archive/restore, full-text search, image support
- **Categories** — hierarchical (parent/child), slug-based
- **Shopping cart** — add, update, remove items
- **Orders** — state machine: `PENDING → PAID → SHIPPED → DELIVERED / CANCELLED`
- **Payments** — mock Stripe: PaymentIntent → confirm → webhook (HMAC-SHA256 verified)
- **Popular this week** — weighted score `views×0.3 + purchases×0.7`, cached in Redis 1h
- **Reviews & Ratings** — 1–5 stars, one per user per product, verified-purchase flag
- **Discount / Coupon codes** — percentage or fixed amount, expiry dates, usage limits
- **Wishlist** — save products for later
- **Admin Analytics** — revenue by period, top products by sales
- **Email notifications** — order confirmation and status updates via SMTP

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.115 |
| Database | PostgreSQL 16 + SQLAlchemy 2.x async |
| Migrations | Alembic (async, 11 steps) |
| Cache | Redis 7 |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Email | aiosmtplib + Jinja2 templates |
| Containerization | Docker + Docker Compose |

## Architecture

Clean Architecture with strict layer separation:

```
src/
├── domain/          # Entities, abstract repositories, domain services
├── application/     # Use cases (business logic)
├── infrastructure/  # SQLAlchemy repos, JWT, Redis, mock payment, SMTP
└── presentation/    # FastAPI routers, Pydantic schemas, DI dependencies
```

## Quick Start

```bash
# 1. Clone and enter the backend directory
cd backend

# 2. Copy environment file
cp .env.example .env

# 3. Start services
docker-compose up -d

# 4. Run migrations
alembic upgrade head

# 5. Start the API
uvicorn src.main:app --reload
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## API Overview

| Method | Path | Access |
|--------|------|--------|
| POST | `/api/v1/auth/register` | Public |
| POST | `/api/v1/auth/login` | Public |
| GET | `/api/v1/products` | Public |
| GET | `/api/v1/products/popular` | Public |
| POST | `/api/v1/products` | MANAGER+ |
| POST | `/api/v1/orders` | USER+ |
| POST | `/api/v1/payments/intent` | USER+ |
| POST | `/api/v1/payments/confirm` | USER+ |
| GET | `/api/v1/analytics/revenue` | ADMIN |
| PUT | `/api/v1/users/{id}/role` | ADMIN |

Full endpoint list available at `/docs`.

## Environment Variables

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/shop
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key
WEBHOOK_SECRET=your-webhook-secret
SMTP_HOST=localhost
SMTP_PORT=587
```

---

# FastAPI Shop (RU)

Продакшн-готовый REST API интернет-магазина на **FastAPI**, **Clean Architecture** и **PostgreSQL**.

## Возможности

- **RBAC** — три роли: `USER`, `MANAGER`, `ADMIN`
- **Товары** — CRUD, мягкое архивирование/восстановление, полнотекстовый поиск, изображения
- **Категории** — иерархические (родитель/дочерние), slug-адресация
- **Корзина** — добавление, изменение, удаление товаров
- **Заказы** — машина состояний: `PENDING → PAID → SHIPPED → DELIVERED / CANCELLED`
- **Платежи** — mock Stripe: PaymentIntent → подтверждение → вебхук (HMAC-SHA256)
- **Популярное за неделю** — взвешенный рейтинг `просмотры×0.3 + покупки×0.7`, кэш Redis 1ч
- **Отзывы и рейтинги** — 1–5 звёзд, один отзыв на товар, флаг подтверждённой покупки
- **Промокоды** — процент или фиксированная скидка, срок действия, лимит использований
- **Список желаний** — сохранение товаров
- **Аналитика (Admin)** — выручка по периоду, топ товаров по продажам
- **Email-уведомления** — подтверждение заказа и обновление статуса

## Стек технологий

| Слой | Технология |
|------|-----------|
| Фреймворк | FastAPI 0.115 |
| БД | PostgreSQL 16 + SQLAlchemy 2.x async |
| Миграции | Alembic (async, 11 шагов) |
| Кэш | Redis 7 |
| Авторизация | JWT (python-jose) + bcrypt (passlib) |
| Email | aiosmtplib + Jinja2 шаблоны |
| Контейнеризация | Docker + Docker Compose |

## Архитектура

Чистая архитектура с чётким разделением слоёв:

```
src/
├── domain/          # Сущности, абстрактные репозитории, доменные сервисы
├── application/     # Use-case'ы (бизнес-логика)
├── infrastructure/  # SQLAlchemy-репозитории, JWT, Redis, платежи, SMTP
└── presentation/    # FastAPI-роутеры, Pydantic-схемы, DI-зависимости
```

## Быстрый старт

```bash
# 1. Перейти в директорию backend
cd backend

# 2. Скопировать файл окружения
cp .env.example .env

# 3. Запустить сервисы
docker-compose up -d

# 4. Применить миграции
alembic upgrade head

# 5. Запустить API
uvicorn src.main:app --reload
```

Документация API: [http://localhost:8000/docs](http://localhost:8000/docs)
