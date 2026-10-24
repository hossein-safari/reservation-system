import type { Reservation, Slot, Transaction } from "../domain/models";
import { dateTime, money, time } from "./format";

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
      <div className="empty">
        <span aria-hidden="true">◷</span>
        <h3>هنوز سانس آزادی ثبت نشده</h3>
        <p>مدیر می‌تواند از بخش مدیریت، فضا و سانس جدید اضافه کند.</p>
      </div>
    );
  return (
    <div className="slot-grid">
      {slots.map((slot) => (
        <article className="slot-card" key={slot.id}>
          <div className="slot-card-top">
            <span className="resource-icon" aria-hidden="true">
              ◫
            </span>
            <span className="availability">
              <i />
              قابل رزرو
            </span>
          </div>
          <h3>{names.get(slot.resource_id) ?? "فضای قابل رزرو"}</h3>
          <p className="muted slot-date">{dateTime(slot.starts_at)}</p>
          <div className="time-range">
            <span>بازه زمانی</span>
            <strong>
              {time(slot.starts_at)} تا {time(slot.ends_at)}
            </strong>
          </div>
          <div className="card-bottom">
            <div>
              <small className="muted">هزینه هر سانس</small>
              <strong>{money(slot.price_irr)}</strong>
            </div>
            <button
              className="primary"
              disabled={busy}
              onClick={() => onReserve(slot.id)}
            >
              رزرو سانس ←
            </button>
          </div>
        </article>
      ))}
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
      <div className="empty">
        <h3>رزروی ندارید</h3>
        <p>از سانس‌های آزاد، اولین قرار خود را انتخاب کنید.</p>
        <button className="outline" onClick={onBrowse}>
          مشاهده سانس‌ها
        </button>
      </div>
    );
  return (
    <div className="rows">
      {reservations.map((reservation) => (
        <article className="reservation-row" key={reservation.id}>
          <div>
            <h3>{names.get(reservation.slot.resource_id) ?? "رزرو سانس"}</h3>
            <p className="muted">
              {dateTime(reservation.slot.starts_at)} تا{" "}
              {time(reservation.slot.ends_at)}
            </p>
            <small className="muted">
              کد رزرو: {reservation.id.slice(0, 8)}
            </small>
          </div>
          <span className={`status ${reservation.status}`}>
            {statuses[reservation.status]}
          </span>
          <strong>{money(reservation.amount_irr)}</strong>
          {reservation.status === "pending" && (
            <div className="row-actions">
              <button
                className="primary"
                disabled={busy}
                onClick={() => onPay(reservation.id)}
              >
                پرداخت آزمایشی
              </button>
              <button
                className="outline"
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
      <div className="empty">
        <h3>تراکنشی ثبت نشده</h3>
        <p>نتیجه پرداخت‌های تأییدشده اینجا نمایش داده می‌شود.</p>
      </div>
    );
  return (
    <div className="rows">
      {transactions.map((transaction) => (
        <article className="reservation-row" key={transaction.id}>
          <div>
            <h3>پرداخت تأییدشده</h3>
            <p className="muted">{dateTime(transaction.created_at)}</p>
            <small className="reference" dir="ltr">
              {transaction.reference}
            </small>
          </div>
          <span className="status confirmed">موفق</span>
          <strong>{money(transaction.amount_irr)}</strong>
        </article>
      ))}
    </div>
  );
}
