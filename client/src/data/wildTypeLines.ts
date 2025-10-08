export type WildTypeLine = {
  // Short code e.g., AB, TL
  code: string;          // Short code e.g., AB, TL

  // ZFIN ZDB-GENO identifier
  genoId: string;        // ZFIN ZDB-GENO identifier

  // ZFIN ZDB-FISH identifier
  fishId: string;        // ZFIN ZDB-FISH identifier

  // Show on focus by default
  defaultSuggestion?: boolean; // Show on focus by default
};

// From https://zfin.org/action/feature/wildtype-list
export const wildTypeLines: WildTypeLine[] = [
  { code: 'AB', genoId: 'ZDB-GENO-960809-7', fishId: 'ZDB-FISH-150901-27842', defaultSuggestion: true },
  { code: 'TL', genoId: 'ZDB-GENO-990623-2', fishId: 'ZDB-FISH-150901-8850', defaultSuggestion: true },
  { code: 'TU', genoId: 'ZDB-GENO-990623-3', fishId: 'ZDB-FISH-150901-15216', defaultSuggestion: true },
  { code: 'WIK', genoId: 'ZDB-GENO-010531-2', fishId: 'ZDB-FISH-150901-23633', defaultSuggestion: true },

  { code: 'AB/C32', genoId: 'ZDB-GENO-070425-3', fishId: 'ZDB-FISH-150901-19012' },
  { code: 'AB/EKW', genoId: 'ZDB-GENO-091223-1', fishId: 'ZDB-FISH-150901-18519' },
  { code: 'AB/TL', genoId: 'ZDB-GENO-031202-1', fishId: 'ZDB-FISH-150901-29235' },
  { code: 'AB/TU', genoId: 'ZDB-GENO-010924-10', fishId: 'ZDB-FISH-150901-29084' },
  { code: 'ABO', genoId: 'ZDB-GENO-181106-1', fishId: 'ZDB-FISH-181106-1' },
  { code: 'C32', genoId: 'ZDB-GENO-030501-1', fishId: 'ZDB-FISH-150901-28222' },
  { code: 'Cooch Behar', genoId: 'ZDB-GENO-180717-1', fishId: 'ZDB-FISH-180717-1' },
  { code: 'DAR', genoId: 'ZDB-GENO-960809-13', fishId: 'ZDB-FISH-150901-28033' },
  { code: 'EKW', genoId: 'ZDB-GENO-990520-2', fishId: 'ZDB-FISH-150901-29731' },
  { code: 'HK', genoId: 'ZDB-GENO-980210-34', fishId: 'ZDB-FISH-150901-5210' },
  { code: 'HK/AB', genoId: 'ZDB-GENO-980210-40', fishId: 'ZDB-FISH-150901-7101' },
  { code: 'HK/SING', genoId: 'ZDB-GENO-980210-38', fishId: 'ZDB-FISH-150901-26310' },
  { code: 'IND', genoId: 'ZDB-GENO-980210-28', fishId: 'ZDB-FISH-150901-25193' },
  { code: 'INDO', genoId: 'ZDB-GENO-980210-32', fishId: 'ZDB-FISH-150901-10750' },
  { code: 'KOLN', genoId: 'ZDB-GENO-010725-1', fishId: 'ZDB-FISH-150901-6' },
  { code: 'NA', genoId: 'ZDB-GENO-030115-2', fishId: 'ZDB-FISH-150901-2506' },
  { code: 'NHGRI-1', genoId: 'ZDB-GENO-150204-3', fishId: 'ZDB-FISH-150901-27165' },
  { code: 'RW', genoId: 'ZDB-GENO-070802-4', fishId: 'ZDB-FISH-150901-1201' },
  { code: 'SAT', genoId: 'ZDB-GENO-100413-1', fishId: 'ZDB-FISH-150901-20769' },
  { code: 'SING', genoId: 'ZDB-GENO-980210-24', fishId: 'ZDB-FISH-150901-12475' },
  { code: 'SJA', genoId: 'ZDB-GENO-061206-2', fishId: 'ZDB-FISH-150901-28847' },
  { code: 'SJD', genoId: 'ZDB-GENO-990308-9', fishId: 'ZDB-FISH-150901-19739' },
  { code: 'SJD/C32', genoId: 'ZDB-GENO-070425-2', fishId: 'ZDB-FISH-150901-4447' },
  { code: 'SPF 5-D', genoId: 'ZDB-GENO-120309-3', fishId: 'ZDB-FISH-150901-14119' },
  { code: 'SPF AB', genoId: 'ZDB-GENO-120309-2', fishId: 'ZDB-FISH-150901-17220' },
  { code: 'TLN', genoId: 'ZDB-GENO-080307-1', fishId: 'ZDB-FISH-150901-17023' },
  { code: 'WIK/AB', genoId: 'ZDB-GENO-050511-1', fishId: 'ZDB-FISH-150901-12950' },
  { code: 'WT', genoId: 'ZDB-GENO-030619-2', fishId: 'ZDB-FISH-150901-29105' }
];

// Convenience lookup maps
export const wildTypeByCode: Record<string, WildTypeLine> = Object.fromEntries(
  wildTypeLines.map((w) => [w.code, w])
);

export const defaultWildTypeSuggestions: WildTypeLine[] = wildTypeLines.filter((w) => w.defaultSuggestion);
