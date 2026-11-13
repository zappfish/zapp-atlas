/** The metadata every image carries, in the order it is asked for. */
export const MEASURES = [
  {
    label: "Scale bar",
    placeholder: "e.g. 100",
    units: ["µm", "mm", "Other"],
    field: "scaleBar",
    unitField: "scaleBarUnit",
  },
  // One unit is notation, not a choice, so it reads as a suffix.
  {
    label: "Magnification",
    placeholder: "e.g. 40",
    suffix: "X",
    field: "magnification",
    unitField: "magnificationUnit",
  },
  {
    label: "Resolution",
    placeholder: "e.g. 300",
    units: ["dpi", "Other"],
    field: "resolution",
    unitField: "resolutionUnit",
  },
] as const;
