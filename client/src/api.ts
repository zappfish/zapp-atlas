/**
 * Fetch wrapper for the ZAPP Atlas API.
 *
 * All calls go through `api()`, which mounts under ``/api/`` so the API
 * routes never collide with SPA routes (e.g. ``/studies/:id`` is a page).
 * Vite proxies ``/api`` in dev; in prod the API is served from the same
 * origin as the SPA under the same prefix.
 */

export const API_BASE = '/api';

/** Absolute URL for an image blob the server stores on behalf of the SPA. */
export function imageUrl(id: number | string): string {
  return `${API_BASE}/images/${id}`;
}

export class ApiError extends Error {
  status: number;
  body: unknown;

  constructor(status: number, body: unknown, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.body = body;
  }
}

export interface ApiOptions extends Omit<RequestInit, 'body'> {
  body?: unknown;
  query?: Record<string, string | number | undefined>;
}

async function parseBody(res: Response): Promise<unknown> {
  const ct = res.headers.get('content-type') ?? '';
  if (ct.includes('application/json')) return res.json();
  if (ct.startsWith('text/')) return res.text();
  return null;
}

export async function api<T = unknown>(
  path: string,
  { body, query, headers, ...rest }: ApiOptions = {},
): Promise<T> {
  const prefixed = path.startsWith(API_BASE) ? path : `${API_BASE}${path}`;
  const url = new URL(prefixed, window.location.origin);
  if (query) {
    for (const [k, v] of Object.entries(query)) {
      if (v !== undefined) url.searchParams.set(k, String(v));
    }
  }

  const isForm = body instanceof FormData;
  const init: RequestInit = {
    ...rest,
    headers: {
      ...(body !== undefined && !isForm ? { 'content-type': 'application/json' } : {}),
      ...(headers ?? {}),
    },
    body:
      body === undefined
        ? undefined
        : isForm
          ? (body as FormData)
          : JSON.stringify(body),
  };

  const res = await fetch(url.toString().replace(window.location.origin, ''), init);
  const parsed = await parseBody(res);

  if (!res.ok) {
    throw new ApiError(res.status, parsed, `${res.status} ${res.statusText}`);
  }
  return parsed as T;
}
