import type {
  AlleleBody,
  Fish,
  FishBody,
  FishDescription,
  FishResolution,
  ParentZygosity,
  ZfinAllele,
  Zygosity,
} from "@/api/types";

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
export const describeFish = (fish: Fish | FishBody): string => {
  const parts = [
    ...(fish.allele ?? []).map((a) => alleleLabel(a.allele_symbol, a.zygosity)),
    ...(fish.transient_reagent ?? []).map((r) => r.reagent_symbol),
  ];
  if (parts.length === 0) return fish.background_name ?? "Fish";
  const alleles = parts.join("; ");
  return fish.background_name ? `${alleles} (${fish.background_name})` : alleles;
};

/** What ZFIN knows the fish as, or that it is not registered. */
export const zfinStatus = (fish: Fish | FishBody): string =>
  fish.genotype_zfin_id ?? "Not registered with ZFIN";

/**
 * What an allele is: the change to the gene, or the construct inserted.
 * "point mutation in fgf8a", "integration of Tg(mpeg1:YFP)".
 */
export const alleleDescription = (allele: ZfinAllele): string => {
  if (allele.is_transgenic) {
    const constructs = allele.constructs.map((c) => c.name).join(" + ");
    return `integration of ${constructs || "a transgene"}`;
  }
  const kind = (allele.alteration_type ?? allele.type_label).replace(/_/g, " ").toLowerCase();
  const genes = allele.genes.map((g) => g.symbol).join(", ");
  return genes ? `${kind} in ${genes}` : `${kind}, gene not recorded`;
};

/** ZFIN's mutagen column, with a short explanation of each value. */
const MUTAGEN_GLOSS: Record<string, string> = {
  ENU: "ENU (random chemical mutagenesis)",
  DNA: "DNA injection (transgenesis)",
  CRISPR: "CRISPR (targeted gene editing)",
  TALEN: "TALEN (targeted gene editing)",
  "DNA and CRISPR": "DNA + CRISPR (targeted knock-in)",
  "DNA and TALEN": "DNA + TALEN (targeted knock-in)",
  "zinc finger nuclease": "zinc-finger nuclease (targeted gene editing)",
  spontaneous: "spontaneous (arose naturally)",
  "g-rays": "gamma irradiation",
  TMP: "TMP (chemical mutagenesis)",
  EMS: "EMS (chemical mutagenesis)",
};

export const mutagenGloss = (mutagen: string): string => MUTAGEN_GLOSS[mutagen] ?? mutagen;

/** The ZFIN record page for any ZFIN CURIE. */
export const zfinUrl = (curie: string) => `https://zfin.org/${curie.replace(/^ZFIN:/, "")}`;

export const ZYGOSITIES: { value: Zygosity; label: string }[] = [
  { value: "homozygous", label: "homozygous" },
  { value: "heterozygous", label: "heterozygous" },
  { value: "unknown", label: "unknown" },
  { value: "complex", label: "complex" },
];

/** A parent's zygosity can also be wild type: not carrying the allele at all. */
export const PARENT_ZYGOSITIES: { value: ParentZygosity; label: string }[] = [
  { value: "unknown", label: "unknown" },
  { value: "wild_type", label: "wild type" },
  { value: "heterozygous", label: "heterozygous" },
  { value: "homozygous", label: "homozygous" },
];

/**
 * An allele chosen from ZFIN, as a card in the fish's description. Zygosity
 * starts unset so that it is chosen rather than defaulted: it is part of a
 * genotype's identity in ZFIN.
 */
export interface AlleleChoice {
  allele: ZfinAllele;
  zygosity: Zygosity | "";
  motherZygosity: ParentZygosity;
  fatherZygosity: ParentZygosity;
}

export const isAnswered = (choice: AlleleChoice): boolean => choice.zygosity !== "";

/**
 * The allele as the data model stores it. The model's scalar gene and
 * construct slots take the first of each; a co-injected line's other
 * constructs stay visible on the card but are not stored.
 */
const alleleBody = ({
  allele,
  zygosity,
  motherZygosity,
  fatherZygosity,
}: AlleleChoice): AlleleBody => {
  const gene = allele.genes[0];
  const construct = allele.constructs[0];
  return {
    allele_zfin_id: allele.allele_id,
    allele_symbol: allele.symbol,
    alteration_type: allele.alteration_type,
    affected_gene_zfin_id: gene?.gene_id ?? null,
    affected_gene_symbol: gene?.symbol ?? null,
    construct_zfin_id: construct?.construct_id ?? null,
    construct_name: construct?.name ?? null,
    zygosity: zygosity as Zygosity,
    mother_zygosity: motherZygosity,
    father_zygosity: fatherZygosity,
  };
};

/** A fish body from what the builder collected, before ZFIN's ids attach.
 *  Every allele must have its zygosity answered (see ``isAnswered``). */
export const toFishBody = (
  alleles: AlleleChoice[],
  background: { genotype_id: string; abbreviation: string } | null,
  lineDescription: string,
): FishBody => ({
  background_zfin_id: background?.genotype_id ?? null,
  background_name: background?.abbreviation ?? null,
  allele: alleles.map(alleleBody),
  transient_reagent: [],
  line_description: lineDescription.trim() || null,
  fish_zfin_id: null,
  genotype_zfin_id: null,
});

/** The resolve request for a fish body. */
export const toDescription = (fish: FishBody): FishDescription => ({
  background_id: fish.background_zfin_id ?? null,
  alleles: (fish.allele ?? [])
    .filter((a) => a.allele_zfin_id)
    .map((a) => ({
      allele_id: a.allele_zfin_id as string,
      zygosity: a.zygosity as "unknown" | "heterozygous" | "homozygous" | "complex",
    })),
  reagents: (fish.transient_reagent ?? [])
    .map((r) => r.reagent_zfin_id)
    .filter((id): id is string => !!id),
});

/** The fish with the ids from ZFIN's answer, set when it names one genotype and fish. */
export const withResolution = (fish: FishBody, found: FishResolution | undefined): FishBody => ({
  ...fish,
  genotype_zfin_id: found?.genotype?.genotype_id ?? null,
  fish_zfin_id: found?.fish?.fish_id ?? null,
});

/** The resolve result as a sentence. */
export const resolutionText = (found: FishResolution): string => {
  if (found.fish) return `Matches ZFIN fish ${found.fish.fish_id} (${found.fish.name_plain}).`;
  if (found.genotype) {
    return `Matches ZFIN genotype ${found.genotype.genotype_id} (${found.genotype.name_plain}); no registered fish carries exactly this.`;
  }
  if (found.candidates.length > 1) {
    return `${found.candidates.length} registered ZFIN genotypes match this description; choosing a background may narrow it.`;
  }
  return "Not registered with ZFIN.";
};
