/** Shared by every /api call. Same origin, so the session cookie goes along. */

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/** `message` replaces the default, built from the status. */
export const get = async <T,>(
  path: string,
  signal?: AbortSignal,
  message?: string,
): Promise<T> => {
  const res = await fetch(`/api${path}`, {
    headers: { Accept: "application/json" },
    signal,
  });
  if (!res.ok) {
    // Non-members get 404, not 403, so group ids can't be probed.
    throw new ApiError(
      res.status,
      message ?? `GET /api${path} failed (${res.status})`,
    );
  }
  return (await res.json()) as T;
};

/** FastAPI puts the reason in `detail` — a 409 names what already exists. */
const errorDetail = async (res: Response, fallback: string) => {
  try {
    const body = await res.json();
    return typeof body?.detail === "string" ? body.detail : fallback;
  } catch {
    return fallback;
  }
};

export const send = async <T,>(
  method: "POST" | "PATCH" | "DELETE",
  path: string,
  body?: unknown,
  signal?: AbortSignal,
): Promise<T | null> => {
  const res = await fetch(`/api${path}`, {
    method,
    headers: {
      Accept: "application/json",
      ...(body === undefined ? {} : { "Content-Type": "application/json" }),
    },
    body: body === undefined ? undefined : JSON.stringify(body),
    signal,
  });
  if (!res.ok) {
    throw new ApiError(
      res.status,
      await errorDetail(res, `${method} /api${path} failed (${res.status})`),
    );
  }
  // DELETE answers 204 with no body.
  return res.status === 204 ? null : ((await res.json()) as T);
};
