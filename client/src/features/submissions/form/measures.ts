import type { ImageValues } from "./submission";

interface Measure {
  label: string;
  placeholder: string;
  field: keyof ImageValues;
  units?: readonly string[];
  unitField?: keyof ImageValues;
  suffix?: string;
}

/** The metadata every image carries, in the order it is asked for. */
export const MEASURES: readonly Measure[] = [
  {
    label: "Scale bar",
    placeholder: "e.g. 100",
    units: ["µm", "mm", "Other"],
    field: "scaleBar",
    unitField: "scaleBarUnit",
  },
  // Its unit is notation, not a choice: shown as a suffix, not stored.
  {
    label: "Magnification",
    placeholder: "e.g. 40",
    suffix: "X",
    field: "magnification",
  },
  {
    label: "Resolution",
    placeholder: "e.g. 300",
    units: ["dpi", "Other"],
    field: "resolution",
    unitField: "resolutionUnit",
  },
];
