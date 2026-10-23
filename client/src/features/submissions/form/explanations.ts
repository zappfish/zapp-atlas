export const REARING_INFO: Record<string, string> = {
  Standard:
    "28.5 °C; 14:10 light:dark; pH 7.2–7.5; E3/Danieau’s; ≤ 50 embryos per 100 mm dish.",
};

export const CONCENTRATION_INFO =
  "Final concentration of the substance in the exposure medium.";

export const UPLOAD_INFO = "Each image must contain only one fish.";

export const REGIMEN_INFO: Record<string, string> = {
  "Continuous exposure":
    "Fish remain exposed to a test substance for the entire test duration without intentional exposure free intervals. The exposure concentration is maintained at a constant or near constant level over time.",
  "Repeated exposures":
    "Fish receive the test substance in discrete dosing events separated by defined exposure free intervals.",
};

export const PATTERN_INFO: Record<string, string> = {
  "Sustained - static":
    "Fish continuously exposed to a single prepared solution over the test duration with no renewal of media.",
  "Sustained - static renewal":
    "Fish continuously exposed over the test period, solution is replaced at fixed intervals with fresh solution of the same composition.",
  "Sustained - dynamic (flow through)":
    "Fish continuously exposed with constant or near constant replacement of solution, maintaining target concentrations over time.",
};
