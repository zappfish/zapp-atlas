/** Shared by every /api call. Same origin, so the session cookie goes along. */

import type { Problem } from "@/problems";

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
    /** What the server found wrong with the body, field by field, on a 422. */
    readonly problems: Problem[] = [],
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

/** One entry of the list FastAPI answers a 422 with. */
interface Refusal {
  /** `["body", ...]` for a field; absent for a rule about the body as a whole. */
  loc?: (string | number)[];
  msg: string;
}

/**
 * FastAPI puts the reason in `detail`: a sentence (a 409 names what already
 * exists), or for a body it could not accept, a list of what is wrong.
 */
const refused = async (res: Response, fallback: string) => {
  const detail: unknown = await res
    .json()
    .then((body) => body?.detail)
    .catch(() => undefined);

  if (typeof detail === "string") return new ApiError(res.status, detail);
  if (!Array.isArray(detail)) return new ApiError(res.status, fallback);

  const problems = (detail as Refusal[]).map(({ loc = [], msg }) => ({
    path: loc.slice(1),
    message: msg,
  }));
  const overall = problems.filter((problem) => problem.path.length === 0);
  return new ApiError(
    res.status,
    overall.map((problem) => problem.message).join(" ") ||
      "Some fields need attention.",
    problems,
  );
};

type Method = "POST" | "PUT" | "PATCH" | "DELETE";

const request = async <T,>(
  method: Method,
  path: string,
  init: Pick<RequestInit, "headers" | "body" | "signal">,
): Promise<T | null> => {
  const res = await fetch(`/api${path}`, {
    ...init,
    method,
    headers: { Accept: "application/json", ...init.headers },
  });
  if (!res.ok) {
    throw await refused(res, `${method} /api${path} failed (${res.status})`);
  }
  // DELETE answers 204 with no body.
  return res.status === 204 ? null : ((await res.json()) as T);
};

export const send = <T,>(
  method: Method,
  path: string,
  body?: unknown,
  signal?: AbortSignal,
): Promise<T | null> =>
  request<T>(method, path, {
    headers: body === undefined ? {} : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
    signal,
  });

/** A file with the fields that describe it. The browser sets the content type. */
export const upload = <T,>(
  path: string,
  form: FormData,
  signal?: AbortSignal,
): Promise<T | null> => request<T>("POST", path, { body: form, signal });
