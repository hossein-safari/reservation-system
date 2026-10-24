import type {
  Credentials,
  NewSlot,
  Payment,
  Reservation,
  Resource,
  Session,
  Slot,
  Transaction,
} from "../domain/models";

const messages: Record<string, string> = {
  invalid_credentials: "ایمیل یا رمز عبور درست نیست.",
  email_exists: "این ایمیل قبلاً ثبت شده است.",
  invalid_token: "نشست شما پایان یافته؛ دوباره وارد شوید.",
  authentication_required: "ابتدا وارد حساب خود شوید.",
  forbidden: "این بخش به دسترسی مدیر نیاز دارد.",
  slot_unavailable: "این سانس دیگر قابل رزرو نیست. فهرست را تازه کنید.",
  overlapping_slot: "این بازه با سانس دیگری هم‌پوشانی دارد.",
  past_slot: "زمان شروع باید در آینده باشد.",
  invalid_interval: "زمان پایان باید بعد از شروع باشد.",
  reservation_not_payable: "این رزرو در وضعیت قابل پرداخت نیست.",
  refund_required: "لغو رزرو پرداخت‌شده به فرایند استرداد نیاز دارد.",
  gateway_unavailable: "درگاه پرداخت در این محیط فعال نیست.",
  conflict: "این درخواست با عملیات دیگری تداخل دارد. اطلاعات را تازه کنید.",
  not_found: "اطلاعات درخواستی پیدا نشد.",
};

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

export class ApiClient {
  constructor(
    private token: string | null,
    private base = "/api/v1",
  ) {}

  private async request<T>(path: string, body?: unknown): Promise<T> {
    const response = await fetch(`${this.base}${path}`, {
      method: body === undefined ? "GET" : "POST",
      headers: {
        ...(body === undefined ? {} : { "Content-Type": "application/json" }),
        ...(this.token ? { Authorization: `Bearer ${this.token}` } : {}),
      },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new ApiError(
        response.status,
        messages[error.error?.code] ??
          (response.status === 422
            ? "اطلاعات فرم معتبر نیست. زمان و مقادیر را بررسی کنید."
            : "ارتباط با سرور با خطا روبه‌رو شد. دوباره تلاش کنید."),
      );
    }
    return response.json() as Promise<T>;
  }

  login(data: Credentials) {
    return this.request<Session>("/auth/login", {
      email: data.email,
      password: data.password,
    });
  }
  register(data: Credentials) {
    return this.request("/auth/register", data);
  }
  resources(offset = 0) {
    return this.request<Resource[]>(`/resources?limit=100&offset=${offset}`);
  }
  slots(resourceId: string, offset = 0) {
    return this.request<Slot[]>(
      `/slots?limit=20&offset=${offset}${resourceId ? `&resource_id=${encodeURIComponent(resourceId)}` : ""}`,
    );
  }
  reservations(offset = 0) {
    return this.request<Reservation[]>(
      `/reservations?limit=20&offset=${offset}`,
    );
  }
  transactions(offset = 0) {
    return this.request<Transaction[]>(
      `/transactions?limit=20&offset=${offset}`,
    );
  }
  reserve(slotId: string) {
    return this.request<Reservation>("/reservations", { slot_id: slotId });
  }
  cancel(id: string) {
    return this.request<Reservation>(`/reservations/${id}/cancel`, {});
  }
  createPayment(id: string) {
    return this.request<Payment>(`/reservations/${id}/payments`, {});
  }
  verify(id: string) {
    return this.request<Transaction>(`/payments/${id}/verify`, {});
  }
  createResource(name: string, description: string) {
    return this.request<Resource>("/resources", { name, description });
  }
  createSlot(data: NewSlot) {
    return this.request<Slot>("/slots", data);
  }
}
