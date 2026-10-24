import type { Reservation } from "../domain/models";
import { Dialog } from "./Dialog";
import { Arrow } from "./Icons";
import { money } from "./format";
interface Props {
  reservation?: Reservation;
  busy: boolean;
  error: string;
  onClose: () => void;
  onConfirm: () => Promise<void>;
}
export function PaymentDialog({
  reservation,
  busy,
  error,
  onClose,
  onConfirm,
}: Props) {
  return (
    <Dialog titleId="payment-title" busy={busy} onClose={onClose}>
      <span className="dialog-kicker">قرار / نهایی‌کردن رزرو</span>
      <h2 id="payment-title">یک قدم تا ثبت نهایی.</h2>
      {reservation && (
        <div className="payment-summary">
          <span className="meta-label">مبلغ رزرو</span>
          <strong>{money(reservation.amount_irr)}</strong>
          <span>
            کد رزرو <bdi>{reservation.id.slice(0, 8)}</bdi>
          </span>
        </div>
      )}
      <div className="payment-notice">
        <strong>درگاه آزمایشی</strong>
        <p>
          این عملیات فقط گردش پرداخت را شبیه‌سازی می‌کند و وجهی منتقل نمی‌شود.
        </p>
      </div>
      {error && (
        <p role="alert" className="message message--error">
          {error}
        </p>
      )}
      <div className="dialog-actions">
        <button
          className="button button--solid"
          disabled={busy}
          onClick={() => void onConfirm()}
        >
          {busy ? "در حال تأیید…" : "تأیید آزمایشی"}
          <Arrow />
        </button>
        <button
          className="button button--text"
          disabled={busy}
          onClick={onClose}
        >
          انصراف
        </button>
      </div>
    </Dialog>
  );
}
