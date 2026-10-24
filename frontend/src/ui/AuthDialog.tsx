import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import type { Credentials } from "../domain/models";

interface Props {
  busy: boolean;
  error: string;
  onClose: () => void;
  onSubmit: (data: Credentials, register: boolean) => Promise<boolean>;
}

export function AuthDialog({ busy, error, onClose, onSubmit }: Props) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [register, setRegister] = useState(false);
  useEffect(() => {
    const element = dialog.current;
    element?.showModal();
    return () => element?.close();
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const credentials: Credentials = {
      email: String(data.get("email")),
      password: String(data.get("password")),
    };
    if (register) credentials.name = String(data.get("name"));
    if (await onSubmit(credentials, register)) onClose();
  }

  return (
    <dialog
      ref={dialog}
      className="auth-dialog"
      aria-labelledby="auth-title"
      onCancel={(event) => {
        if (busy) event.preventDefault();
        else onClose();
      }}
    >
      <div className="dialog-heading">
        <h2 id="auth-title">{register ? "ساخت حساب جدید" : "خوش برگشتید"}</h2>
        <button
          className="icon-button"
          disabled={busy}
          onClick={onClose}
          aria-label="بستن"
        >
          ×
        </button>
      </div>
      <p className="muted">برای مدیریت رزروها وارد حساب خود شوید.</p>
      <form onSubmit={submit}>
        {register && (
          <label>
            نام و نام خانوادگی
            <input name="name" required maxLength={120} autoComplete="name" />
          </label>
        )}
        <label>
          ایمیل
          <input
            name="email"
            type="email"
            dir="ltr"
            required
            autoComplete="email"
            maxLength={254}
          />
        </label>
        <label>
          رمز عبور
          <input
            name="password"
            type="password"
            dir="ltr"
            required
            minLength={register ? 12 : 1}
            maxLength={128}
            autoComplete={register ? "new-password" : "current-password"}
          />
        </label>
        {register && <small className="muted">حداقل ۱۲ نویسه</small>}
        {error && (
          <p role="alert" className="error">
            {error}
          </p>
        )}
        <button className="primary full" disabled={busy}>
          {busy ? "در حال انجام…" : register ? "ثبت‌نام" : "ورود"}
        </button>
      </form>
      <button
        className="text-button"
        disabled={busy}
        onClick={() => setRegister((value) => !value)}
      >
        {register ? "حساب دارید؟ وارد شوید" : "حساب ندارید؟ ثبت‌نام کنید"}
      </button>
    </dialog>
  );
}
