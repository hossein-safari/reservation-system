import { useState } from "react";
import { useReservationApp } from "./application/useReservationApp";
import type { Tab } from "./application/useReservationApp";
import { AdminPanel } from "./ui/AdminPanel";
import { AuthDialog } from "./ui/AuthDialog";
import { SlotList, ReservationList, TransactionList } from "./ui/BookingViews";
import "./styles.css";

const tabs: { id: Tab; label: string; symbol: string }[] = [
  { id: "slots", label: "سانس‌های آزاد", symbol: "◫" },
  { id: "reservations", label: "رزروهای من", symbol: "▤" },
  { id: "transactions", label: "تراکنش‌ها", symbol: "⇄" },
  { id: "admin", label: "مدیریت", symbol: "⚙" },
];

export default function App() {
  const app = useReservationApp();
  const [authOpen, setAuthOpen] = useState(false);
  const [paymentId, setPaymentId] = useState<string | null>(null);
  const names = new Map(
    app.resources.map((resource) => [resource.id, resource.name]),
  );
  const count =
    app.tab === "slots"
      ? app.slots.length
      : app.tab === "reservations"
        ? app.reservations.length
        : app.transactions.length;
  const title = tabs.find((tab) => tab.id === app.tab)?.label;

  function navigate(tab: Tab) {
    setPaymentId(null);
    if (tab !== "slots" && !app.session) {
      setAuthOpen(true);
      return;
    }
    app.navigate(tab);
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="/" aria-label="قرار، صفحه اصلی">
          <span className="brand-mark">ق</span>
          <span>
            قرار<small>سامانه رزرو سانس</small>
          </span>
        </a>
        <div className="nav-label">فضای کار شما</div>
        <nav aria-label="منوی اصلی">
          {tabs
            .filter(
              (tab) => tab.id !== "admin" || app.session?.user.role === "admin",
            )
            .map((tab) => (
              <button
                key={tab.id}
                className={`nav-item ${app.tab === tab.id ? "active" : ""}`}
                onClick={() => navigate(tab.id)}
              >
                <span aria-hidden="true">{tab.symbol}</span>
                {tab.label}
              </button>
            ))}
        </nav>
        <div className="sidebar-note">
          <span className="live-dot" />
          برنامه‌ریزی ساده‌تر
          <p>زمان مناسب را پیدا کنید و با خیال راحت رزرو کنید.</p>
        </div>
        <div className="sidebar-footer">قرار؛ برای وقت‌های ارزشمند شما</div>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <div>
            <span className="muted">فضای کار</span>
            <span className="breadcrumb"> / {title}</span>
          </div>
          <div className="account">
            {app.session ? (
              <>
                <span className="avatar">
                  {app.session.user.name.slice(0, 1)}
                </span>
                <span>{app.session.user.name}</span>
                <button
                  className="text-button"
                  disabled={app.busy}
                  onClick={app.logout}
                >
                  خروج
                </button>
              </>
            ) : (
              <button className="outline" onClick={() => setAuthOpen(true)}>
                ورود / ثبت‌نام
              </button>
            )}
          </div>
        </header>
        <main id="main-content">
          <div className="page-heading">
            <div>
              <span className="eyebrow">هر برنامه‌ای، یک قرار</span>
              <h1>{title}</h1>
              <p className="muted">
                {app.tab === "slots"
                  ? "فضای دلخواه و زمان مناسب خود را انتخاب کنید."
                  : "وضعیت قرارها و پرداخت‌های خود را اینجا دنبال کنید."}
              </p>
            </div>
            <button
              className="outline"
              disabled={app.loading || app.busy}
              onClick={app.refresh}
            >
              ↻ تازه‌سازی
            </button>
          </div>
          {app.tab === "slots" && (
            <section className="intro-card">
              <div>
                <span className="pill">یک قدم تا قرار بعدی</span>
                <h2>
                  زمانتان را به بهترین شکل
                  <br />
                  برنامه‌ریزی کنید.
                </h2>
                <p>سانس را انتخاب کنید، رزرو کنید و آماده باشید.</p>
              </div>
              <div className="calendar-art" aria-hidden="true">
                <div className="calendar-top" />
                <div className="calendar-grid">
                  {Array.from({ length: 12 }, (_, index) => (
                    <span
                      key={index}
                      className={index === 6 ? "selected-day" : ""}
                    >
                      {index + 12}
                    </span>
                  ))}
                </div>
              </div>
            </section>
          )}
          {app.error && !authOpen && (
            <p role="alert" className="message error">
              {app.error}
            </p>
          )}
          {app.notice && (
            <p role="status" className="message success">
              {app.notice}
            </p>
          )}
          {app.tab === "slots" && (
            <div className="list-toolbar">
              <h2>زمان‌های در دسترس</h2>
              <label className="filter-label">
                فضا
                <select
                  aria-label="فضا"
                  value={app.resourceId}
                  onChange={(event) => app.filterResource(event.target.value)}
                >
                  <option value="">همه فضاها</option>
                  {app.resources.map((resource) => (
                    <option key={resource.id} value={resource.id}>
                      {resource.name}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          )}
          {app.loading ? (
            <div className="empty" role="status">
              در حال دریافت اطلاعات…
            </div>
          ) : (
            <>
              {app.tab === "slots" && (
                <SlotList
                  slots={app.slots}
                  names={names}
                  busy={app.busy}
                  onReserve={(id) => {
                    if (app.session) void app.reserve(id);
                    else setAuthOpen(true);
                  }}
                />
              )}
              {app.tab === "reservations" && (
                <ReservationList
                  reservations={app.reservations}
                  names={names}
                  busy={app.busy}
                  onPay={setPaymentId}
                  onCancel={(id) => void app.cancel(id)}
                  onBrowse={() => app.navigate("slots")}
                />
              )}
              {app.tab === "transactions" && (
                <TransactionList transactions={app.transactions} />
              )}
              {app.tab === "admin" && app.session?.user.role === "admin" && (
                <AdminPanel
                  resources={app.resources}
                  busy={app.busy}
                  createResource={app.createResource}
                  createSlot={app.createSlot}
                />
              )}
              {app.tab !== "admin" && (
                <div className="pagination">
                  <button
                    className="outline"
                    disabled={app.page === 0}
                    onClick={() => app.setPage((value) => value - 1)}
                  >
                    صفحه قبل
                  </button>
                  <span>
                    صفحه {new Intl.NumberFormat("fa-IR").format(app.page + 1)}
                  </span>
                  <button
                    className="outline"
                    disabled={count < 20}
                    onClick={() => app.setPage((value) => value + 1)}
                  >
                    صفحه بعد
                  </button>
                </div>
              )}
            </>
          )}
          <footer className="page-footer">
            <span>همه ساعت‌ها به وقت تهران • مبلغ‌ها به ریال</span>
            <span>نسخه توسعه / پرداخت آزمایشی</span>
          </footer>
        </main>
      </div>
      {authOpen && (
        <AuthDialog
          busy={app.busy}
          error={app.error}
          onClose={() => setAuthOpen(false)}
          onSubmit={app.authenticate}
        />
      )}
      {paymentId && (
        <div
          className="payment-confirm"
          role="region"
          aria-label="تأیید پرداخت آزمایشی"
        >
          <strong>درگاه آزمایشی</strong>
          <p>
            این عملیات فقط گردش پرداخت را شبیه‌سازی می‌کند و وجهی منتقل نمی‌شود.
          </p>
          <div className="row-actions">
            <button
              className="primary"
              disabled={app.busy}
              onClick={async () => {
                if (await app.pay(paymentId)) setPaymentId(null);
              }}
            >
              تأیید آزمایشی
            </button>
            <button
              className="outline"
              disabled={app.busy}
              onClick={() => setPaymentId(null)}
            >
              بستن
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
