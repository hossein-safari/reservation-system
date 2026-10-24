import type { Reservation, Slot, Transaction } from "../domain/models";
import { dateTime, dayParts, duration, money, number, time } from "./format";
import { Arrow } from "./Icons";

const statuses = {
  pending: "در انتظار پرداخت",
  confirmed: "تأییدشده",
  cancelled: "لغوشده",
};
interface SlotListProps {
  slots: Slot[];
  names: Map<string, string>;
  busy: boolean;
  onReserve: (id: string) => void;
}

export function SlotList({ slots, names, busy, onReserve }: SlotListProps) {
  if (!slots.length)
    return (
      <div className="empty-state">
        <h3>هنوز سانس آزادی ثبت نشده</h3>
        <p>مدیر می‌تواند از بخش مدیریت، فضا و سانس جدید اضافه کند.</p>
      </div>
    );
  const days = new Map<string, Slot[]>();
  for (const slot of slots) {
    const key = dayParts(slot.starts_at).key;
    const group = days.get(key) ?? [];
    group.push(slot);
    days.set(key, group);
  }
  return (
    <div className="schedule">
      {Array.from(days, ([key, group]) => {
        const date = dayParts(group[0].starts_at);
        return (
          <section
            className="schedule-day"
            key={key}
            aria-labelledby={`day-${group[0].id}`}
          >
            <header className="date-divider">
              <h2 id={`day-${group[0].id}`}>
                {date.weekday}، {date.label}
              </h2>
              <span className="date-divider-count">
                {number(group.length)} سانس آزاد
              </span>
            </header>
            {group.map((slot) => (
              <article className="time-row" key={slot.id}>
                <div className="time-row-clock">
                  <time dateTime={slot.starts_at}>{time(slot.starts_at)}</time>
                  <span>تا {time(slot.ends_at)}</span>
                </div>
                <div className="time-row-place">
                  <h3>{names.get(slot.resource_id) ?? "فضای قابل رزرو"}</h3>
                  <span>{duration(slot.starts_at, slot.ends_at)}</span>
                </div>
                <div className="time-row-price">
                  <span className="meta-label">هزینهٔ سانس</span>
                  <strong>{money(slot.price_irr)}</strong>
                </div>
                <button
                  className="button button--reserve"
                  aria-label={`رزرو سانس ${names.get(slot.resource_id) ?? "فضا"}، ${dateTime(slot.starts_at)}`}
                  disabled={busy}
                  onClick={() => onReserve(slot.id)}
                >
                  رزرو سانس
                  <Arrow />
                </button>
              </article>
            ))}
          </section>
        );
      })}
    </div>
  );
}

interface ReservationListProps {
  reservations: Reservation[];
  names: Map<string, string>;
  busy: boolean;
  onPay: (id: string) => void;
  onCancel: (id: string) => void;
  onBrowse: () => void;
}
export function ReservationList({
  reservations,
  names,
  busy,
  onPay,
  onCancel,
  onBrowse,
}: ReservationListProps) {
  if (!reservations.length)
    return (
      <div className="empty-state">
        <h3>رزروی ندارید</h3>
        <p>از سانس‌های آزاد، اولین قرار خود را انتخاب کنید.</p>
        <button className="button button--solid" onClick={onBrowse}>
          مشاهده سانس‌ها
          <Arrow />
        </button>
      </div>
    );
  return (
    <div className="record-list">
      {reservations.map((reservation) => (
        <article className="booking-record" key={reservation.id}>
          <div className="record-heading">
            <span className={`status status--${reservation.status}`}>
              {statuses[reservation.status]}
            </span>
            <span className="record-code">
              کد رزرو <bdi>{reservation.id.slice(0, 8)}</bdi>
            </span>
          </div>
          <div className="record-body">
            <div>
              <h3>{names.get(reservation.slot.resource_id) ?? "رزرو سانس"}</h3>
              <p>
                {dateTime(reservation.slot.starts_at)} تا{" "}
                {time(reservation.slot.ends_at)}
              </p>
            </div>
            <strong className="record-amount">
              {money(reservation.amount_irr)}
            </strong>
          </div>
          {reservation.status === "pending" && (
            <div className="record-actions">
              <button
                className="button button--solid"
                disabled={busy}
                onClick={() => onPay(reservation.id)}
              >
                پرداخت آزمایشی
                <Arrow />
              </button>
              <button
                className="button button--text"
                disabled={busy}
                onClick={() => onCancel(reservation.id)}
              >
                لغو رزرو
              </button>
            </div>
          )}
        </article>
      ))}
    </div>
  );
}

export function TransactionList({
  transactions,
}: {
  transactions: Transaction[];
}) {
  if (!transactions.length)
    return (
      <div className="empty-state">
        <h3>تراکنشی ثبت نشده</h3>
        <p>نتیجه پرداخت‌های تأییدشده اینجا نمایش داده می‌شود.</p>
      </div>
    );
  return (
    <div className="record-list">
      {transactions.map((transaction) => (
        <article className="receipt-record" key={transaction.id}>
          <div className="receipt-detail">
            <span className="status status--confirmed">موفق</span>
            <h3>پرداخت تأییدشده</h3>
            <p>{dateTime(transaction.created_at)}</p>
            <dl>
              <dt>شمارهٔ پیگیری</dt>
              <dd dir="ltr">{transaction.reference}</dd>
            </dl>
          </div>
          <strong className="record-amount">
            {money(transaction.amount_irr)}
          </strong>
        </article>
      ))}
    </div>
  );
}
