# قرارداد API نسخه ۱

پیشوند `/api/v1`؛ JSON با `snake_case`، UUID به صورت رشته، زمان ISO-8601 با offset، مبالغ عدد صحیح ریال. قرارداد کامل تولیدشده توسط برنامه در `/openapi.json` و `/docs` قرار دارد.

| روش و مسیر | دسترسی | کاربرد |
| --- | --- | --- |
| POST /auth/register | عمومی | name، email، password؛ ساخت مشتری |
| POST /auth/login | عمومی | email/password؛ JWT bearer |
| GET /auth/me | عضو | حساب فعلی |
| GET /resources | عمومی | فضاها |
| POST /resources | مدیر | name/description |
| GET /slots | عمومی | سانس‌ها؛ فیلتر resource_id و available_only |
| POST /slots | مدیر | resource_id، starts_at، ends_at، price_irr |
| GET /reservations | عضو | رزروهای خود |
| POST /reservations | عضو | slot_id |
| POST /reservations/{id}/cancel | مالک | لغو رزرو پرداخت‌نشده |
| POST /reservations/{id}/payments | مالک | ساخت یا بازیابی Payment |
| POST /payments/{id}/verify | مالک | تأیید آزمایشی فقط در development/test |
| GET /transactions | عضو | تراکنش‌های خود |
| GET /health/live | عمومی | حیات فرایند |
| GET /health/ready | عمومی | اتصال دیتابیس و نسخه migration |

فهرست‌ها `?limit=50&offset=0` دارند؛ حداکثر limit برابر 100 است. خروجی آرایه است؛ شمارش کل فعلاً ارائه نمی‌شود. سانس‌ها به ترتیب زمان و رزروها/تراکنش‌ها از جدید به قدیم مرتب‌اند. `available_only=true` سانس‌های آیندهٔ بدون رزرو فعال را برمی‌گرداند.

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"name":"مشتری نمونه","email":"customer@example.com","password":"Choose-a-long-password"}'
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"customer@example.com","password":"Choose-a-long-password"}'
# access_token خروجی را در متغیر TOKEN بگذارید.
curl http://localhost:8000/api/v1/reservations -H "Authorization: Bearer $TOKEN"
```

خطای تجاری شکل `{"error":{"code":"slot_unavailable","message":"..."}}` دارد. 401 برای ورود نامعتبر، 403 نقش نامجاز، 404 منبع ناموجود یا متعلق به دیگری، 409 تداخل یا وضعیت نامعتبر، 422 داده نامعتبر و 503 زیرساخت آماده‌نشده است. خطاهای اعتبارسنجی استاندارد FastAPI با `detail` برمی‌گردند. فرانت هر دو قالب را پردازش می‌کند.

تکرار ساخت Payment همان شناسه را برمی‌گرداند؛ تکرار verify همان Transaction را برمی‌گرداند. رزرو تکراری 409 دارد؛ برای ایجاد رزرو کلید idempotency عمومی ارائه نشده است. نرخ ارز/تومان از کلاینت وارد محاسبات نمی‌شود.
