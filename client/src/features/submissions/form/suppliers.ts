/** Spelled out rather than capitalised: "vwr" -> "VWR". */
const SUPPLIER_ACRONYMS = new Set(["vwr"]);

export const supplierLabel = (value: string) =>
  value
    .split("_")
    .map((word) =>
      SUPPLIER_ACRONYMS.has(word)
        ? word.toUpperCase()
        : word.charAt(0).toUpperCase() + word.slice(1),
    )
    .join(" ");
