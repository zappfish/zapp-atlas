/**
 * Who is signed in, bootstrapped into the page by templates/app.html rather
 * than fetched: the server knows it from the session cookie, and it cannot
 * change while the page is open.
 */

export interface SignedInUser {
  orcid_id: string;
  name: string | null;
}

declare global {
  interface Window {
    ZAPP_SIGNED_IN_USER?: SignedInUser | null;
  }
}

export const signedInUser = (): SignedInUser | null =>
  window.ZAPP_SIGNED_IN_USER ?? null;

/** Memberships carry the CURIE form; the bootstrap carries the bare id. */
export const asCurie = (orcidId: string) => `ORCID:${orcidId}`;
