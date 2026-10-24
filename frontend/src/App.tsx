import { useState } from "react";
import { useReservationApp } from "./application/useReservationApp";
import type { Tab } from "./application/useReservationApp";
import { AdminPanel } from "./ui/AdminPanel";
import { AuthDialog } from "./ui/AuthDialog";
import { SlotList, ReservationList, TransactionList } from "./ui/BookingViews";
import { PaymentDialog } from "./ui/PaymentDialog";
import { Arrow, Refresh } from "./ui/Icons";
import { number } from "./ui/format";
import "./styles.css";

const tabs: { id: Tab; label: string }[] = [
  { id: "slots", label: "سانس‌های آزاد" },
  { id: "reservations", label: "رزروهای من" },
  { id: "transactions", label: "تراکنش‌ها" },
  { id: "admin", label: "مدیریت" },
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
    <div className="app-root">
      <a className="skip-link" href="#main-content">
        رفتن به محتوای اصلی
      </a>
      <header className="site-header page-width">
        <a className="wordmark" href="/" aria-label="قرار، صفحه اصلی">
          قرار<span aria-hidden="true">.</span>
        </a>
        <nav className="main-nav" aria-label="منوی اصلی">
          {tabs
            .filter(
              (tab) => tab.id !== "admin" || app.session?.user.role === "admin",
            )
            .map((tab) => (
              <button
                key={tab.id}
                className={`nav-link ${app.tab === tab.id ? "is-current" : ""}`}
                aria-current={app.tab === tab.id ? "page" : undefined}
                onClick={() => navigate(tab.id)}
              >
                {tab.label}
              </button>
            ))}
        </nav>
        <div className="account">
          {app.session ? (
            <>
              <span className="account-name">{app.session.user.name}</span>
              <button
                className="button button--text"
                disabled={app.busy}
                onClick={app.logout}
              >
                خروج
              </button>
            </>
          ) : (
            <button
              className="button button--outline"
              onClick={() => setAuthOpen(true)}
            >
              ورود / ثبت‌نام
            </button>
          )}
        </div>
      </header>

      <main id="main-content" className="page-width page-content" tabIndex={-1}>
        <div className="page-heading">
          <h1>{title}</h1>
          <div className="page-actions">
            {app.tab === "slots" && (
              <select
                className="resource-select"
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
            )}
            <button
              className="button button--icon"
              aria-label="تازه‌سازی"
              title="تازه‌سازی"
              disabled={app.loading || app.busy}
              onClick={app.refresh}
            >
              <Refresh />
            </button>
          </div>
        </div>

        {app.error && !authOpen && (
          <p role="alert" className="message message--error">
            {app.error}
          </p>
        )}
        {app.notice && (
          <p role="status" className="message message--success">
            {app.notice}
          </p>
        )}
        {app.loading ? (
          <div className="loading-state" role="status">
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
              <div className="pagination" aria-label="صفحه‌بندی">
                <button
                  className="button button--text"
                  disabled={app.page === 0 || app.busy}
                  onClick={() => app.setPage((value) => value - 1)}
                >
                  <Arrow direction="right" />
                  صفحه قبل
                </button>
                <span>صفحه {number(app.page + 1)}</span>
                <button
                  className="button button--text"
                  disabled={count < 20 || app.busy}
                  onClick={() => app.setPage((value) => value + 1)}
                >
                  صفحه بعد
                  <Arrow />
                </button>
              </div>
            )}
          </>
        )}
      </main>
      <footer className="site-footer page-width">
        <span>همه ساعت‌ها به وقت تهران · مبلغ‌ها به ریال</span>
        <span>پرداخت آزمایشی</span>
      </footer>
      {authOpen && (
        <AuthDialog
          busy={app.busy}
          error={app.error}
          onClose={() => setAuthOpen(false)}
          onSubmit={app.authenticate}
        />
      )}
      {paymentId && (
        <PaymentDialog
          reservation={app.reservations.find(
            (reservation) => reservation.id === paymentId,
          )}
          busy={app.busy}
          error={app.error}
          onClose={() => setPaymentId(null)}
          onConfirm={async () => {
            if (await app.pay(paymentId)) setPaymentId(null);
          }}
        />
      )}
    </div>
  );
}
