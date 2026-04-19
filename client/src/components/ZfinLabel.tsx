import React from 'react';

/**
 * Render a ZFIN-style label that may carry superscript/subscript markup
 * (transgene notation, e.g. `abhd11<sup>hi3305Tg/+</sup>`). Only a small
 * allowlist of presentational tags is honored; anything else is stripped
 * before insertion so we don't pass through unexpected HTML from the
 * upstream.
 */

const ALLOWED_TAGS = ['sup', 'sub', 'i', 'b', 'em', 'strong'] as const;
const TAG_GUARD = new RegExp(
  `<(?!\\/?(?:${ALLOWED_TAGS.join('|')})\\b)[^>]*>`,
  'gi',
);

export function sanitizeZfinLabel(text: string): string {
  return text.replace(TAG_GUARD, '');
}

export default function ZfinLabel({
  text,
  className,
}: {
  text: string | null | undefined;
  className?: string;
}) {
  if (!text) return null;
  return (
    <span
      className={className}
      dangerouslySetInnerHTML={{ __html: sanitizeZfinLabel(text) }}
    />
  );
}
