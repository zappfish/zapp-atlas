import type { Body } from "@/schema/bodies";

interface Measure {
  label: string;
  placeholder: string;
  /** The image's slot, which holds the number and its unit as one text. */
  slot: keyof Body<"Image">;
  units?: readonly string[];
  suffix?: string;
}

/** The metadata every image carries, in the order it is asked for. */
export const MEASURES: readonly Measure[] = [
  {
    label: "Scale bar",
    placeholder: "e.g. 100",
    units: ["µm", "mm", "Other"],
    slot: "scale_bar",
  },
  // Its unit is notation, not a choice: shown as a suffix.
  {
    label: "Magnification",
    placeholder: "e.g. 40",
    suffix: "X",
    slot: "magnification",
  },
  {
    label: "Resolution",
    placeholder: "e.g. 300",
    units: ["dpi", "Other"],
    slot: "resolution",
  },
];
