# E-commerce Backend (FastAPI + SQLite)

## Setup

1. Create environment file

Copy `.env.example` to `.env` and set `JWT_SECRET`.

2. Install dependencies

```
python -m venv .venv
.venv\Scripts\activate
pip install -r ecommerce/backend/requirements.txt
```

3. Run server

```
uvicorn ecommerce.backend.app.main:app --reload
```

API will be available at http://127.0.0.1:8000 and docs at /docs.

## Notes
- Database initializes from `ecommerce/backend/database/schema.sql` on startup.
- Uses JWT bearer tokens. Add `Authorization: Bearer <token>` to protected routes.
- Transactional order placement ensures stock checks, order creation, order items insert, stock decrement, and cart clearing are atomic.
