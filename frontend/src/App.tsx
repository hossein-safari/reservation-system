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

const chapters: {
  id: Tab;
  label: string;
  description: string;
  note: string;
}[] = [
  {
    id: "slots",
    label: "سانس‌های آزاد",
    description: "هر قرار خوب، از یک وقت مناسب شروع می‌شود.",
    note: "فضا و زمان دلخواهتان را پیدا کنید. با ثبت رزرو، آن وقت برای شما کنار گذاشته می‌شود.",
  },
  {
    id: "reservations",
    label: "رزروهای من",
    description: "وقت‌هایی که برای خودتان کنار گذاشته‌اید.",
    note: "جزئیات قرارها را ببینید، رزرو را نهایی کنید یا وقت پرداخت‌نشده را آزاد کنید.",
  },
  {
    id: "transactions",
    label: "تراکنش‌ها",
    description: "حساب روشنِ قرارهای شما.",
    note: "رسید پرداخت‌های تأییدشده با مبلغ و شمارهٔ پیگیری در این دفتر نگهداری می‌شود.",
  },
  {
    id: "admin",
    label: "مدیریت",
    description: "یک فضا تعریف کنید؛ برایش وقت بگذارید.",
    note: "ابتدا فضای قابل رزرو را ثبت کنید، سپس بازه‌های زمانی و هزینهٔ هر سانس را مشخص کنید.",
  },
];

export default function App() {
  const app = useReservationApp();
  const [authOpen, setAuthOpen] = useState(false);
  const [paymentId, setPaymentId] = useState<string | null>(null);
  const chapterIndex = chapters.findIndex((chapter) => chapter.id === app.tab);
  const chapter = chapters[chapterIndex];
  const names = new Map(
    app.resources.map((resource) => [resource.id, resource.name]),
  );
  const count =
    app.tab === "slots"
      ? app.slots.length
      : app.tab === "reservations"
        ? app.reservations.length
        : app.transactions.length;
  const today = new Intl.DateTimeFormat("fa-IR", {
    day: "numeric",
    month: "long",
    year: "numeric",
    timeZone: "Asia/Tehran",
  }).format(new Date());

  function navigate(tab: Tab) {
    setPaymentId(null);
    if (tab !== "slots" && !app.session) {
      setAuthOpen(true);
      return;
    }
    app.navigate(tab);
  }

  return (
    <div className="paper-app">
      <a className="skip-link" href="#main-content">
        رفتن به محتوای اصلی
      </a>
      <header className="masthead page-width">
        <div className="edition-line">
          <span>دفتر رزرو فضا و زمان</span>
          <time>{today}</time>
        </div>
        <div className="masthead-main">
          <a className="wordmark" href="/" aria-label="قرار، صفحه اصلی">
            قرار<span aria-hidden="true">.</span>
          </a>
          <p className="masthead-caption">
            برای هر قرار،
            <br />
            <strong>یک جای مشخص.</strong>
          </p>
          <div className="account">
            {app.session ? (
              <>
                <div className="account-name">
                  <span className="meta-label">حساب شما</span>
                  <span>{app.session.user.name}</span>
                </div>
                <button
                  className="button button--text"
                  disabled={app.busy}
                  onClick={app.logout}
                >
                  خروج
                  <Arrow />
                </button>
              </>
            ) : (
              <button
                className="button button--outline"
                onClick={() => setAuthOpen(true)}
              >
                ورود / ثبت‌نام
                <Arrow />
              </button>
            )}
          </div>
        </div>
        <nav className="chapter-nav" aria-label="منوی اصلی">
          {chapters
            .filter(
              (item) =>
                item.id !== "admin" || app.session?.user.role === "admin",
            )
            .map((item, index) => (
              <button
                key={item.id}
                className={`chapter-link ${app.tab === item.id ? "is-current" : ""}`}
                aria-current={app.tab === item.id ? "page" : undefined}
                onClick={() => navigate(item.id)}
              >
                <span className="chapter-link-number" aria-hidden="true">
                  {number(index + 1, 2)}
                </span>
                {item.label}
                <Arrow />
              </button>
            ))}
        </nav>
      </header>

      <main id="main-content" className="page-width book-layout" tabIndex={-1}>
        <section className="chapter-intro" aria-labelledby="page-title">
          <div className="chapter-index">
            <span>بخش</span>
            <span>{number(chapterIndex + 1, 2)}</span>
          </div>
          <h1 id="page-title">{chapter.label}</h1>
          <p className="chapter-description">{chapter.description}</p>
          <div className="chapter-note">
            <span className="small-cross" aria-hidden="true">
              +
            </span>
            <p>{chapter.note}</p>
          </div>
          <div className="time-zone-note">
            <span className="meta-label">مبنای زمان</span>
            <span>
              تهران <span dir="ltr">UTC +03:30</span>
            </span>
          </div>
        </section>
        <div className="chapter-content">
          <div className="content-toolbar">
            <div>
              <span className="meta-label">
                {app.tab === "slots" ? "انتخاب فضا" : "دفتر شخصی شما"}
              </span>
              {app.tab === "slots" ? (
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
              ) : (
                <p className="toolbar-title">
                  {app.tab === "admin" ? "فضاها و سانس‌ها" : "فهرست ثبت‌شده‌ها"}
                </p>
              )}
            </div>
            <button
              className="button button--text refresh-button"
              disabled={app.loading || app.busy}
              onClick={app.refresh}
            >
              <Refresh />
              تازه‌سازی
            </button>
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
              <span>در حال دریافت اطلاعات…</span>
              <div aria-hidden="true">
                <i />
                <i />
                <i />
              </div>
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
                  <span className="page-number">
                    <span className="meta-label">صفحه</span>
                    {number(app.page + 1, 2)}
                  </span>
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
        </div>
      </main>
      <footer className="colophon page-width">
        <span className="colophon-brand">قرار.</span>
        <p>وقت برای شما. جای آن با ما.</p>
        <div>
          <span>مبلغ‌ها به ریال</span>
          <span>نسخهٔ توسعه · پرداخت آزمایشی</span>
        </div>
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
