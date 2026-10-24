import type { FormEvent } from "react";
import type { NewSlot, Resource } from "../domain/models";
import { Arrow } from "./Icons";

interface Props {
  resources: Resource[];
  busy: boolean;
  createResource: (name: string, description: string) => Promise<boolean>;
  createSlot: (data: NewSlot) => Promise<boolean>;
}

export function AdminPanel({
  resources,
  busy,
  createResource,
  createSlot,
}: Props) {
  async function resourceSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    if (
      await createResource(
        String(data.get("name")),
        String(data.get("description")),
      )
    )
      form.reset();
  }
  async function slotSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    // An explicit Tehran offset avoids interpreting the input in the browser's timezone.
    const success = await createSlot({
      resource_id: String(data.get("resource_id")),
      starts_at: new Date(`${data.get("starts_at")}:00+03:30`).toISOString(),
      ends_at: new Date(`${data.get("ends_at")}:00+03:30`).toISOString(),
      price_irr: Number(data.get("price_irr")),
    });
    if (success) form.reset();
  }
  return (
    <div className="admin-forms">
      <section className="form-section">
        <header className="form-section-heading">
          <div>
            <h2>فضای جدید</h2>
          </div>
        </header>
        <form className="form-stack" onSubmit={resourceSubmit}>
          <label>
            نام فضا
            <input name="name" required maxLength={120} />
          </label>
          <label>
            توضیحات
            <textarea name="description" rows={3} maxLength={2000} />
          </label>
          <button className="button button--solid" disabled={busy}>
            ایجاد فضا <Arrow />
          </button>
        </form>
      </section>
      <section className="form-section">
        <header className="form-section-heading">
          <div>
            <h2>سانس جدید</h2>
            <p>تاریخ میلادی؛ ساعت به وقت تهران</p>
          </div>
        </header>
        <form className="form-stack" onSubmit={slotSubmit}>
          <label>
            فضا
            <select
              name="resource_id"
              aria-label="فضا"
              required
              defaultValue=""
            >
              <option value="" disabled>
                انتخاب فضا
              </option>
              {resources.map((resource) => (
                <option key={resource.id} value={resource.id}>
                  {resource.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            شروع
            <input type="datetime-local" name="starts_at" required />
          </label>
          <label>
            پایان
            <input type="datetime-local" name="ends_at" required />
          </label>
          <label>
            قیمت (ریال)
            <input
              type="number"
              name="price_irr"
              min={1}
              max={1000000000000}
              step={1}
              required
            />
          </label>
          <button
            className="button button--solid"
            disabled={busy || !resources.length}
          >
            ایجاد سانس <Arrow />
          </button>
        </form>
      </section>
    </div>
  );
}
