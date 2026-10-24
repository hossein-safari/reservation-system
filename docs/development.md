# توسعه و عملیات

## پیش‌نیاز

WSL Ubuntu، Python 3.12+ با `python3-venv`، Node 24 LTS و Docker Compose v2. همه فرمان‌ها از ریشه همین مخزن در bash اجرا می‌شوند. روی WSL از فایل‌سیستم Linux استفاده کنید.

## Backend محلی

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.lock
pip install -e . --no-deps
alembic upgrade head
python -m app.cli create-admin
uvicorn app.main:app --reload
```

پیش‌فرض SQLite در `backend/reservation.db` است. تنظیمات با متغیر محیطی `DATABASE_URL`، `APP_SECRET_KEY`، `APP_ENV`، `CORS_ORIGINS` و `ACCESS_TOKEN_MINUTES` تغییر می‌کنند. فایل `backend/.env` اختیاری است؛ env شل اولویت دارد. `CORS_ORIGINS` آرایه JSON مانند `["http://localhost:5173"]` است. PostgreSQL با `postgresql+psycopg://...` استفاده می‌شود.

```bash
ruff check .
ruff format --check .
mypy app
pytest
```

تست‌ها با SQLite موقت و بدون داده واقعی اجرا می‌شوند. برای PostgreSQL یک **دیتابیس تست اختصاصی** بدهید؛ fixture جدول‌های آن را پاک/بازسازی می‌کند:

```bash
TEST_DATABASE_URL=postgresql+psycopg://test:test@localhost:5433/reservation_test pytest
```

این مقدار را هرگز به دیتابیس عملیاتی اشاره ندهید. CI دیتابیس موقت اختصاصی دارد و تست‌های قفل و رقابت روی آن اجرا می‌شوند.

## Frontend محلی

```bash
cd frontend
npm ci
npm run dev
npm run lint
npm run format:check
npm test
npm run build
```

فرانت از `/api/v1` هم‌مبدأ استفاده می‌کند؛ Vite و nginx درخواست‌ها را proxy می‌کنند. توکن فقط در حافظه برنامه است؛ پس از reload ورود دوباره لازم است. کد View از transport مستقل است و تعاملات در hook مدیریت می‌شوند.

## Docker

`.env.example` را به `.env` کپی و کلیدها را اختصاصی کنید. سرویس‌های `db`، `api` و `web` شامل healthcheck هستند. api پس از سلامت db، migration را اجرا می‌کند. web روی 8080 و api فقط روی localhost:8000 publish می‌شوند. PostgreSQL به host منتشر نمی‌شود. هر دو برنامه بدون root اجرا می‌شوند.

اگر پورت‌ها اشغال‌اند، `WEB_PORT` و `API_PORT` را در `.env` تغییر دهید؛ برای Vite می‌توانید `npm run dev -- --port 15173` اجرا کنید. رمز PostgreSQL در URL اتصال استفاده می‌شود؛ مقدار hex یا alphanumeric انتخاب کنید تا به URL encoding نیاز نداشته باشد.

```bash
docker compose up --build -d
docker compose ps
docker compose logs --tail=100 api
docker compose exec api python -m app.cli create-admin
docker compose down
```

قبل از migration عملیاتی backup بگیرید. برای production، TLS در reverse proxy، secret manager، PostgreSQL اختصاصی و درگاه واقعی لازم‌اند. `APP_ENV=production` با کلید پیش‌فرض رد می‌شود و درگاه آزمایشی در production خطای 503 دارد؛ فعال‌سازی production به معنی آماده بودن پرداخت واقعی نیست.

## افزودن قابلیت

قاعده در domain/application، query در repository، schema/endpoint در api و interaction در hook React اضافه شود. ابتدا رفتار خطا، مالکیت داده و هم‌زمانی را مشخص کنید. migration با `alembic revision --autogenerate -m '...'` ایجاد و SQL آن بازبینی شود. schema اولیه به صورت دستی و پایدار ثبت شده است.
