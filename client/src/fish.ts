import type { Fish } from "@/api/types";

/** An allele as ZFIN writes a genotype: "ti282a/ti282a", "ti282a/+", or just the symbol. */
const alleleLabel = (symbol: string, zygosity: string) => {
  switch (zygosity) {
    case "homozygous":
      return `${symbol}/${symbol}`;
    case "heterozygous":
      return `${symbol}/+`;
    default:
      return symbol;
  }
};

/**
 * A described fish in one line: its alleles and injected reagents on their
 * background, or the wild-type line alone when it carries none.
 */
export const describeFish = (fish: Fish): string => {
  const parts = [
    ...(fish.mutant_allele ?? []).map((a) => alleleLabel(a.allele_symbol, a.zygosity)),
    ...(fish.transgenic_allele ?? []).map((a) => alleleLabel(a.allele_symbol, a.zygosity)),
    ...(fish.transient_reagent ?? []).map((r) => r.reagent_symbol),
  ];
  if (parts.length === 0) return fish.background_name ?? "Fish";
  const alleles = parts.join("; ");
  return fish.background_name ? `${alleles} (${fish.background_name})` : alleles;
};

/** What ZFIN knows the fish as, or that it is not registered. */
export const zfinStatus = (fish: Fish): string =>
  fish.genotype_zfin_id ?? "Not registered with ZFIN";
