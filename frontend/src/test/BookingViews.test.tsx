import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";
import { SlotList } from "../ui/BookingViews";
import type { Slot } from "../domain/models";

it("groups slots by the Tehran calendar day across UTC midnight", async () => {
  const starts = [
    "2030-11-01T20:00:00Z",
    "2030-11-01T21:00:00Z",
    "2030-11-02T01:00:00Z",
  ];
  const slots: Slot[] = starts.map((starts_at, index) => ({
    id: `slot-${index}`,
    resource_id: "r1",
    starts_at,
    ends_at: new Date(new Date(starts_at).getTime() + 30 * 60000).toISOString(),
    price_irr: 500000,
  }));
  const reserve = vi.fn();
  const view = render(
    <SlotList
      slots={slots}
      names={new Map([["r1", "سالن آفتاب"]])}
      busy={false}
      onReserve={reserve}
    />,
  );
  const days = screen.getAllByRole("region");
  expect(days).toHaveLength(2);
  expect(within(days[0]).getAllByRole("article")).toHaveLength(1);
  expect(within(days[1]).getAllByRole("article")).toHaveLength(2);
  await userEvent.click(
    within(days[1]).getAllByRole("button", { name: /رزرو سانس/ })[0],
  );
  expect(reserve).toHaveBeenCalledWith("slot-1");
  view.rerender(
    <SlotList
      slots={slots}
      names={new Map([["r1", "سالن آفتاب"]])}
      busy={true}
      onReserve={reserve}
    />,
  );
  expect(
    screen
      .getAllByRole("button", { name: /رزرو سانس/ })
      .every((button) => button.hasAttribute("disabled")),
  ).toBe(true);
});
