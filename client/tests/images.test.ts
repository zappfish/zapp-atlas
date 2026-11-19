import { afterEach, expect, test, vi } from "vitest";

import { uploadImage } from "@/api/images";

afterEach(() => vi.unstubAllGlobals());

test("an image is uploaded as its file and the fields that describe it", async () => {
  const fetched = vi.fn<(url: string, init: RequestInit) => Promise<Response>>(
    async () => new Response(JSON.stringify({ id: 5 }), { status: 201 }),
  );
  vi.stubGlobal("fetch", fetched);

  const file = new File(["…"], "fish.png", { type: "image/png" });
  const saved = await uploadImage(3, file, { magnification: "40x", scale_bar: null });

  expect(saved).toEqual({ id: 5 });
  const [url, init] = fetched.mock.calls[0]!;
  expect(url).toBe("/api/observations/3/images");
  expect(init.method).toBe("POST");
  const form = init.body as FormData;
  expect(form.get("file")).toBe(file);
  expect(form.get("magnification")).toBe("40x");
  // A field with no value is left out, not sent as the word "null".
  expect(form.has("scale_bar")).toBe(false);
  // The browser writes the multipart content type, with its boundary.
  expect(init.headers).not.toHaveProperty("Content-Type");
});
