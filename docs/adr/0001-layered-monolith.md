# ADR 0001: Monolith لایه‌ای و قرارداد درگاه

وضعیت: پذیرفته‌شده — ۲۰۲۶-۱۰-۲۴

## مسئله

طرح اولیه مشتری، سانس، رزرو، پرداخت و تراکنش را به هم وصل می‌کند. اجرای یکپارچه رزرو و ثبت نتیجه پرداخت به consistency نیاز دارد، ولی ارائه‌دهنده بانک هنوز تعیین نشده است.

## تصمیم

FastAPI همگام با SQLAlchemy 2 و UnitOfWork، PostgreSQL برای محیط اصلی، Alembic برای schema و React/TypeScript برای View. سرویس‌های کاربردی به Protocolهای Repository و PaymentGateway وابسته‌اند. مدل persistence از schema HTTP جداست. به‌جای microserviceهای زودهنگام، یک برنامه با مرزهای روشن داریم.

## پیامد

یک تراکنش دیتابیس وضعیت رزرو و پرداخت را هماهنگ می‌کند. درگاه توسعه deterministic است؛ درگاه خارجی در آینده به چرخه intent/callback، timeout، retry و reconciliation مستقل نیاز دارد و نباید تماس شبکه طولانی را زیر قفل دیتابیس انجام دهد. SQLite توسعه را ساده می‌کند ولی رفتار رقابتی با PostgreSQL در CI سنجیده می‌شود.
