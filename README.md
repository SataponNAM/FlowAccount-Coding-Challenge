# Product API

FastAPI starter backend with an in-memory product catalogue.

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API documentation.

## Endpoints

- `GET /health` — service status
- `GET /api/products` — all products; add `?category=อาหาร` to filter by category
- `GET /products/{product_id}` — one product by sequential ID
- `POST /api/products` — validate and add a product

Each product has `name`, `sku`, `price`, `stock`, `category`, and `created_at` (plus a sequential numeric `id` for lookup).

`POST /api/products` accepts `name`, `sku`, `price`, `stock`, and `category`. Invalid input and duplicate SKUs return `400` in the format `{"errors": ["ข้อความข้อผิดพลาด"]}`.
