# معماری

یک monorepo با دو برنامه مستقل و یک PostgreSQL. هدف، پایه‌ای قابل اجرا با مرزهای روشن است؛ لایه‌های اضافی فقط در صورت نیاز اضافه می‌شوند.

## MVC و جهت وابستگی

```text
React View -> hook/controller -> typed API client
                                  |
FastAPI controller -> application service -> repository/gateway protocols
                                               ^
                                 SQLAlchemy repository / development gateway
```

- **Model:** موجودیت‌های SQLAlchemy در `infrastructure/models.py`، قواعد خالص دامنه در `domain/` و سرویس‌های کاربردی در `application/`. مدل ORM جزئیات persistence دارد و به کلاینت برگردانده نمی‌شود؛ schema خروجی مرز API است.
- **View:** کامپوننت‌های React؛ نمایش، فرم و دسترس‌پذیری.
- **Controller:** مسیرهای FastAPI اعتبارسنجی/احراز هویت را انجام می‌دهند و سرویس را صدا می‌زنند. hookهای React وضعیت تعاملات را کنترل می‌کنند. UI، SQL و قواعد تجاری را اجرا نمی‌کند.
- **Composition root:** `api/dependencies.py` قراردادها را به آداپتورهای SQLAlchemy و درگاه توسعه متصل می‌کند. سرویس‌ها به FastAPI وابسته نیستند.

## SOLID در کد

| اصل | کاربرد مشخص |
| --- | --- |
| SRP | AuthService، CatalogService، ReservationService و PaymentService مسئولیت جدا دارند؛ کنترلرهای HTTP نازک هستند. |
| OCP | درگاه جدید با پیاده‌سازی `PaymentGateway` و تغییر composition root اضافه می‌شود. |
| LSP | قرارداد Repository در تست‌های سرویس با fake جایگزین می‌شود؛ رفتار سرویس به Session وابسته نیست. |
| ISP | قراردادهای AuthRepository، CatalogRepository، BookingRepository و PaymentRepository جدا هستند. |
| DIP | سرویس‌ها Protocol و UnitOfWork می‌گیرند؛ SQLAlchemy و درگاه توسعه آداپتورند. |

## تراکنش و هم‌زمانی

هر command یک UnitOfWork دارد. Repository فقط query و flush می‌کند و commit نمی‌کند؛ commit در انتهای عملیات سرویس است. خطا باعث rollback می‌شود. قیمت از دیتابیس خوانده می‌شود.

قفل ردیف فضا ساخت سانس را سریالی می‌کند؛ constraint منع هم‌پوشانی PostgreSQL نیز لایهٔ نهایی حفاظت است. unique index جزئی روی `reservations.slot_id` برای وضعیت‌های فعال از دو رزرو هم‌زمان جلوگیری می‌کند. پرداخت، قفل رزرو و Payment را می‌گیرد؛ لغو هم همان قفل رزرو را دارد. نتیجهٔ درگاه، Payment، Transaction و وضعیت رزرو در یک commit ذخیره می‌شوند. بن‌بست با ترتیب ثابت قفل رزرو سپس Payment کاهش می‌یابد.

SQLite برای توسعه سریع و تست سبک است؛ ضمانت قفل ردیفی PostgreSQL را ندارد. تست‌های هم‌زمانی و منع هم‌پوشانی روی PostgreSQL اجرا می‌شوند. تست CI هر دو مسیر را پوشش می‌دهد.

## خواندن بیشتر

ساختار چندفایلی و dependency injection بر پایهٔ [راهنمای رسمی FastAPI](https://fastapi.tiangolo.com/tutorial/bigger-applications/) است؛ مدیریت commit/rollback با [تراکنش‌های SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html) و محدودیت‌های هم‌زمانی با [constraintهای PostgreSQL](https://www.postgresql.org/docs/current/ddl-constraints.html) پیاده شده است.
