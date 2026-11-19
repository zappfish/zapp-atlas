/**
 * The client must never reject a request the server accepts.
 *
 * `fixtures/request-examples.json` is written by the server (`just api-types`):
 * request bodies built from the schema, each with the level it is for and
 * whether the server accepts it. The client checks a body against the LinkML
 * JSON Schema before sending it, and the server against its generated models.
 * A body the client wrongly turned away could never be saved.
 *
 * Only the accepted examples are held to. Letting through a body the server
 * goes on to refuse costs a round trip, and the refusal is shown instead.
 */

import { describe, expect, test } from "vitest";

import { validateBody, type Stored } from "@/schema/bodies";

import examples from "./fixtures/request-examples.json";

interface RequestExample {
  name: string;
  level: Stored;
  body: unknown;
  accepted: boolean;
}

const accepted = (examples as RequestExample[]).filter(
  (example) => example.accepted,
);

describe("the client does not reject", () => {
  test.each(accepted)("$name", ({ level, body }) => {
    const validate = validateBody(level);
    expect(validate(body), JSON.stringify(validate.errors)).toBe(true);
  });
});
