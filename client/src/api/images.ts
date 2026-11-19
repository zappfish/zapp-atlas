import type { Body } from "@/schema/bodies";

import { send, upload } from "./client";
import type { Image } from "./types";

/** Where an image's file is served from, for an `<img>`. */
export const imageUrl = (imageId: number) => `/api/images/${imageId}`;

/** A file is uploaded once, with the fields that describe it, and never replaced. */
export const uploadImage = (
  observationId: number,
  file: File,
  description: Body<"Image">,
) => {
  const form = new FormData();
  form.set("file", file);
  for (const [field, value] of Object.entries(description)) {
    if (value != null) form.set(field, value);
  }
  return upload<Image>(`/observations/${observationId}/images`, form);
};

/** Replace what is said about an image. Its file stays as uploaded. */
export const replaceImage = (imageId: number, description: Body<"Image">) =>
  send<Image>("PUT", `/images/${imageId}`, description);

export const deleteImage = (imageId: number) =>
  send<null>("DELETE", `/images/${imageId}`);
