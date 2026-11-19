import { useState } from "react";
import { useController } from "react-hook-form";
import type { components } from "@/api/openapi";

type Quantity = components["schemas"]["QuantityValue"];

const DECIMAL = /^\d+(\.\d+)?$/;

/**
 * A number and the unit it is in, as one value.
 *
 * What is typed and the unit chosen are held here, and the form is given a
 * quantity only once there is a number. A unit with no number measures
 * nothing, so it is never the form's value.
 */
export const useQuantity = (name: string, defaultUnit: string) => {
  const { field } = useController({ name });
  const saved = field.value as Quantity | undefined;
  const [text, setText] = useState(
    saved?.numeric_value === undefined ? "" : String(saved.numeric_value),
  );
  const [unit, setUnit] = useState(saved?.unit ?? defaultUnit);

  const isNumber = DECIMAL.test(text.trim());
  const hold = (nextText: string, nextUnit: string) => {
    setText(nextText);
    setUnit(nextUnit);
    field.onChange(
      DECIMAL.test(nextText.trim())
        ? { numeric_value: Number(nextText), unit: nextUnit }
        : undefined,
    );
  };

  return {
    text,
    unit,
    type: (next: string) => hold(next, unit),
    choose: (next: string) => hold(text, next),
    onBlur: field.onBlur,
    error:
      text.trim() === "" || isNumber
        ? undefined
        : "Enter a number, e.g. 10 or 2.5.",
  };
};

/**
 * For a text box whose slot holds a number: the number that was typed, or
 * nothing for an empty box. Anything else is kept as typed, so the schema
 * can say it is not a number; a box that quietly held nothing would not be
 * saved and would not say why.
 */
export const asNumber = (typed: string | number | null | undefined) => {
  if (typeof typed !== "string") return typed;
  if (typed.trim() === "") return null;
  return DECIMAL.test(typed.trim()) ? Number(typed) : typed;
};
