import { afterEach, describe, expect, test, vi } from "vitest";

import { ApiError, send } from "@/api/client";

const answer = (status: number, body: unknown) =>
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => new Response(JSON.stringify(body), { status })),
  );

afterEach(() => vi.unstubAllGlobals());

const refusal = (sending: Promise<unknown>) =>
  sending.then(
    () => expect.unreachable("the request was not refused"),
    (error: unknown) => error as ApiError,
  );

describe("a refused request", () => {
  test("carries the server's sentence", async () => {
    answer(409, { detail: "That nickname is already used" });
    const error = await refusal(send("POST", "/studies", {}));

    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ status: 409, message: "That nickname is already used", problems: [] });
  });

  test("carries each problem with a body, by where in the body it is", async () => {
    answer(422, {
      detail: [
        { loc: ["body", "fish", "allele", 0, "zygosity"], msg: "Field required" },
        { type: "schema_rule", msg: "Study: an unpublished study carries a nickname." },
      ],
    });
    const error = await refusal(send("PUT", "/experiments/1", {}));

    expect(error.problems).toEqual([
      { path: ["fish", "allele", 0, "zygosity"], message: "Field required" },
      { path: [], message: "Study: an unpublished study carries a nickname." },
    ]);
    // A rule about the body as a whole is the message.
    expect(error.message).toBe("Study: an unpublished study carries a nickname.");
  });
});
