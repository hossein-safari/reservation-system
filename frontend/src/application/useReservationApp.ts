import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ApiClient, ApiError } from "../api/client";
import type {
  Credentials,
  NewSlot,
  Reservation,
  Resource,
  Session,
  Slot,
  Transaction,
} from "../domain/models";

export type Tab = "slots" | "reservations" | "transactions" | "admin";

export function useReservationApp() {
  const [session, setSession] = useState<Session | null>(null);
  const [tab, setTab] = useState<Tab>("slots");
  const [resources, setResources] = useState<Resource[]>([]);
  const [slots, setSlots] = useState<Slot[]>([]);
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [resourceId, setResourceId] = useState("");
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [revision, setRevision] = useState(0);
  const activeAction = useRef(false);
  const api = useMemo(
    () => new ApiClient(session?.access_token ?? null),
    [session],
  );
  const refresh = useCallback(() => setRevision((value) => value + 1), []);

  useEffect(() => {
    let active = true;
    async function load() {
      setLoading(true);
      try {
        const allResources: Resource[] = [];
        for (let offset = 0; ; offset += 100) {
          const batch = await api.resources(offset);
          allResources.push(...batch);
          if (batch.length < 100) break;
        }
        const rows =
          tab === "slots"
            ? await api.slots(resourceId, page * 20)
            : tab === "reservations" && session
              ? await api.reservations(page * 20)
              : tab === "transactions" && session
                ? await api.transactions(page * 20)
                : [];
        if (!active) return;
        setError("");
        setResources(allResources);
        if (tab === "slots") setSlots(rows as Slot[]);
        if (tab === "reservations") setReservations(rows as Reservation[]);
        if (tab === "transactions") setTransactions(rows as Transaction[]);
      } catch (cause) {
        if (active) {
          setError(
            cause instanceof Error ? cause.message : "دریافت اطلاعات ممکن نشد.",
          );
          if (cause instanceof ApiError && cause.status === 401)
            setSession(null);
        }
      } finally {
        if (active) setLoading(false);
      }
    }
    void load();
    return () => {
      active = false;
    };
  }, [api, tab, resourceId, page, revision, session]);

  async function perform(
    action: () => Promise<unknown>,
    success: string,
  ): Promise<boolean> {
    if (activeAction.current) return false;
    activeAction.current = true;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await action();
      setNotice(success);
      refresh();
      return true;
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "عملیات انجام نشد.");
      if (cause instanceof ApiError && cause.status === 401) setSession(null);
      return false;
    } finally {
      activeAction.current = false;
      setBusy(false);
    }
  }

  function navigate(next: Tab) {
    setTab(next);
    setPage(0);
    setError("");
    setNotice("");
  }
  function logout() {
    setSession(null);
    setReservations([]);
    setTransactions([]);
    navigate("slots");
  }

  return {
    session,
    tab,
    resources,
    slots,
    reservations,
    transactions,
    resourceId,
    page,
    loading,
    busy,
    error,
    notice,
    navigate,
    logout,
    refresh,
    setPage,
    filterResource(id: string) {
      setResourceId(id);
      setPage(0);
    },
    authenticate(data: Credentials, register: boolean) {
      return perform(async () => {
        if (register) await api.register(data);
        setSession(await api.login(data));
      }, "با موفقیت وارد شدید.");
    },
    reserve(id: string) {
      return perform(
        () => api.reserve(id),
        "رزرو ثبت شد. برای نهایی‌کردن، از بخش رزروهای من پرداخت کنید.",
      );
    },
    cancel(id: string) {
      return perform(() => api.cancel(id), "رزرو لغو شد.");
    },
    pay(id: string) {
      return perform(async () => {
        const payment = await api.createPayment(id);
        await api.verify(payment.id);
      }, "پرداخت آزمایشی تأیید و رزرو نهایی شد؛ وجهی منتقل نشده است.");
    },
    createResource(name: string, description: string) {
      return perform(
        () => api.createResource(name, description),
        "فضا ایجاد شد.",
      );
    },
    createSlot(data: NewSlot) {
      return perform(() => api.createSlot(data), "سانس ایجاد شد.");
    },
  };
}
