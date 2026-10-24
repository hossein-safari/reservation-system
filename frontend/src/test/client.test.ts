import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiClient, ApiError } from "../api/client";

afterEach(() => vi.unstubAllGlobals());

describe("API boundary", () => {
  it("sends the bearer token and lets the server determine the reservation amount", async () => {
    const fetch = vi
      .fn()
      .mockResolvedValue(
        new Response(JSON.stringify({ id: "r1" }), { status: 201 }),
      );
    vi.stubGlobal("fetch", fetch);
    await new ApiClient("token").reserve("slot-1");
    expect(fetch).toHaveBeenCalledWith(
      "/api/v1/reservations",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ slot_id: "slot-1" }),
        headers: expect.objectContaining({ Authorization: "Bearer token" }),
      }),
    );
  });

  it("provides readable Persian conflict and validation messages", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            error: { code: "slot_unavailable" },
          }),
          { status: 409 },
        ),
      ),
    );
    await expect(new ApiClient(null).reserve("s1")).rejects.toThrow(
      "این سانس دیگر قابل رزرو نیست",
    );
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          new Response("<html>Bad gateway</html>", { status: 502 }),
        ),
    );
    await expect(new ApiClient(null).resources()).rejects.toBeInstanceOf(
      ApiError,
    );
  });
});
