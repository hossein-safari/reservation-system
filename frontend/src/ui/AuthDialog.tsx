import { useState } from "react";
import type { FormEvent } from "react";
import type { Credentials } from "../domain/models";
import { Dialog } from "./Dialog";
import { Arrow } from "./Icons";

interface Props {
  busy: boolean;
  error: string;
  onClose: () => void;
  onSubmit: (data: Credentials, register: boolean) => Promise<boolean>;
}
export function AuthDialog({ busy, error, onClose, onSubmit }: Props) {
  const [register, setRegister] = useState(false);
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
    <Dialog titleId="auth-title" busy={busy} onClose={onClose}>
      <span className="dialog-kicker">قرار / حساب شخصی</span>
      <h2 id="auth-title">{register ? "حساب جدید." : "ورود به دفتر."}</h2>
      <p className="dialog-description">
        {register
          ? "حساب بسازید و وقت قرار بعدی‌تان را انتخاب کنید."
          : "برای دیدن و مدیریت قرارها، وارد حساب خود شوید."}
      </p>
      <form className="paper-form" onSubmit={submit}>
        {register && (
          <label>
            نام و نام خانوادگی
            <input
              name="name"
              required
              maxLength={120}
              autoComplete="name"
              autoFocus
            />
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
            placeholder="you@example.com"
            autoFocus={!register}
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
        {register && <small className="field-hint">حداقل ۱۲ نویسه</small>}
        {error && (
          <p role="alert" className="message message--error">
            {error}
          </p>
        )}
        <button className="button button--solid button--full" disabled={busy}>
          {busy ? "در حال انجام…" : register ? "ثبت‌نام" : "ورود"}
          <Arrow />
        </button>
      </form>
      <div className="dialog-footnote">
        <button
          className="button button--text"
          disabled={busy}
          onClick={() => setRegister((value) => !value)}
        >
          {register ? "حساب دارید؟ وارد شوید" : "حساب ندارید؟ ثبت‌نام کنید"}
        </button>
      </div>
    </Dialog>
  );
}
