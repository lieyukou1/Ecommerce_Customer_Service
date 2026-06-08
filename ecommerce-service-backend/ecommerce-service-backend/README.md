# property service demo backend

This backend is a full property-management mapping of the teacher's ecommerce demo.
It serves the single-page owner-facing frontend and provides:

- resident work order lists
- resident service item lists
- work order detail, status and progress
- work order urge request submission
- complaint request submission
- placeholder chat endpoints for the interaction shell

The seeded data includes:

- 3 residents with different business profiles
- 13 work orders across pending, in progress, on-site, completed and closed statuses
- service progress timelines
- service items, complaint samples and urge samples

## Start with Docker Compose

```powershell
cd D:\Desktop\SGG_Data\23_尚硅谷大模型项目之智能客服\前端、中台项目
docker compose up --build
```

If you already initialized an old MySQL volume and want to rebuild data from scratch:

```powershell
docker compose down -v
docker compose up --build
```

Default addresses after startup:

- API: `http://127.0.0.1:18081`
- OpenAPI: `http://127.0.0.1:18081/docs`

## Core APIs

- `GET /health`
- `GET /residents/{resident_id}/work-orders`
- `GET /residents/{resident_id}/service-items`
- `GET /work-orders/{work_order_id}`
- `GET /work-orders/{work_order_id}/status`
- `GET /work-orders/{work_order_id}/progress`
- `GET /service-items/{service_item_id}`
- `POST /work-orders/{work_order_id}/urge-requests`
- `POST /work-orders/{work_order_id}/complaint-requests`
- `GET /api/chat/history`
- `POST /api/chat`

## Local development

```powershell
cd D:\Desktop\SGG_Data\23_尚硅谷大模型项目之智能客服\前端、中台项目\ecommerce-service-backend\ecommerce-service-backend
uv sync
uv run python main.py
```

Set `DATABASE_URL` in `.env` if you want to point to a different MySQL host.
