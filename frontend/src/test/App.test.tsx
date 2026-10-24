import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, expect, it, vi } from "vitest";
import App from "../App";

afterEach(() => vi.unstubAllGlobals());

it("shows available slots and requires authentication before booking", async () => {
  const showModal = vi.fn();
  HTMLDialogElement.prototype.showModal = showModal;
  HTMLDialogElement.prototype.close = vi.fn();
  vi.stubGlobal(
    "fetch",
    vi.fn(
      async (url: string) =>
        new Response(
          JSON.stringify(
            url.includes("/resources")
              ? [{ id: "resource-1", name: "سالن آفتاب", description: "" }]
              : [
                  {
                    id: "slot-1",
                    resource_id: "resource-1",
                    starts_at: "2030-11-01T10:00:00Z",
                    ends_at: "2030-11-01T11:00:00Z",
                    price_irr: 500000,
                  },
                ],
          ),
        ),
    ),
  );
  render(<App />);
  expect(
    await screen.findByRole("heading", { name: "سالن آفتاب" }),
  ).toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: /رزرو سانس/ }));
  expect(screen.getByLabelText("ایمیل")).toBeInTheDocument();
  expect(showModal).toHaveBeenCalled();
  expect(fetch).toHaveBeenCalledTimes(2);
});

it("clears the load error after a successful retry", async () => {
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockRejectedValueOnce(new Error("اتصال برقرار نشد"))
      .mockImplementation(async () => new Response("[]")),
  );
  render(<App />);
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "اتصال برقرار نشد",
  );
  expect(screen.getByRole("button", { name: /تازه‌سازی/ })).toBeEnabled();
  await userEvent.click(screen.getByRole("button", { name: /تازه‌سازی/ }));
  expect(
    await screen.findByRole("heading", { name: "هنوز سانس آزادی ثبت نشده" }),
  ).toBeInTheDocument();
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
});
