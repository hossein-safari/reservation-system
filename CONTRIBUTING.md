# مشارکت

کامیت‌ها را بر اساس تغییر مستقل تفکیک کنید: `docs:`, `feat(api):`, `feat(web):`, `test:`, `ci:` و `fix:`. secret، دیتابیس محلی و artifact ساخت را commit نکنید.

پیش از push، Ruff، mypy، pytest، ESLint، Vitest و build فرانت را اجرا کنید. تغییر رفتار به تست معنادار نیاز دارد؛ تغییر schema به migration صریح. خطای تجاری باید code پایدار داشته باشد. پول integer و زمان UTC است. کنترلر نباید query دیتابیس یا محاسبه قیمت داشته باشد؛ کامپوننت React نباید fetch پراکنده یا منطق رزرو را تکرار کند.

تغییر دامنه را همراه `docs/requirements.md` و `docs/api.md` به‌روز کنید. برای تصمیمی که گزینه‌های مهم دیگری داشته، ADR کوتاه بنویسید. اصل طراحی، کمینه‌کردن وابستگی و قابل‌تست‌بودن رفتار است؛ برای کد ساده abstraction بدون کاربرد اضافه نکنید.

در بک‌اند، هر موجودیت، مدل persistence و Repository فایل مستقل دارد. schema و کنترلر در ماژول حوزهٔ مربوط قرار می‌گیرند. domain نباید FastAPI، Pydantic یا SQLAlchemy را import کند؛ application و api نباید infrastructure را import کنند. آداپتورها را در `app/bootstrap/container.py` متصل کنید. تغییر وضعیت را از متد دامنه و تغییر داده را داخل `uow.transaction()` انجام دهید. `mypy app tests/unit tests/fakes` و تست‌های معماری/قرارداد هم بخشی از CI هستند.
