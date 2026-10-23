/** ZFS developmental stages, with ZFIN's hour windows (zfin.org/downloads/stage_ontology.txt). */

export interface Stage {
  id: string;
  period: string;
  name: string;
  /** Hours post fertilization; a stage runs from `start` up to, not including, `end`. */
  start: number;
  end: number;
}

export const ZFS_STAGES: Stage[] = [
  { id: "ZFS:0000001", period: "Zygote", name: "1-cell", start: 0, end: 0.75 },
  { id: "ZFS:0000002", period: "Cleavage", name: "2-cell", start: 0.75, end: 1 },
  { id: "ZFS:0000003", period: "Cleavage", name: "4-cell", start: 1, end: 1.25 },
  { id: "ZFS:0000004", period: "Cleavage", name: "8-cell", start: 1.25, end: 1.5 },
  { id: "ZFS:0000005", period: "Cleavage", name: "16-cell", start: 1.5, end: 1.75 },
  { id: "ZFS:0000006", period: "Cleavage", name: "32-cell", start: 1.75, end: 2 },
  { id: "ZFS:0000007", period: "Cleavage", name: "64-cell", start: 2, end: 2.25 },
  { id: "ZFS:0000008", period: "Blastula", name: "128-cell", start: 2.25, end: 2.5 },
  { id: "ZFS:0000009", period: "Blastula", name: "256-cell", start: 2.5, end: 2.75 },
  { id: "ZFS:0000010", period: "Blastula", name: "512-cell", start: 2.75, end: 3 },
  { id: "ZFS:0000011", period: "Blastula", name: "1k-cell", start: 3, end: 3.33 },
  { id: "ZFS:0000012", period: "Blastula", name: "High", start: 3.33, end: 3.66 },
  { id: "ZFS:0000013", period: "Blastula", name: "Oblong", start: 3.66, end: 4 },
  { id: "ZFS:0000014", period: "Blastula", name: "Sphere", start: 4, end: 4.33 },
  { id: "ZFS:0000015", period: "Blastula", name: "Dome", start: 4.33, end: 4.66 },
  { id: "ZFS:0000016", period: "Blastula", name: "30%-epiboly", start: 4.66, end: 5.25 },
  { id: "ZFS:0000017", period: "Gastrula", name: "50%-epiboly", start: 5.25, end: 5.66 },
  { id: "ZFS:0000018", period: "Gastrula", name: "Germ-ring", start: 5.66, end: 6 },
  { id: "ZFS:0000019", period: "Gastrula", name: "Shield", start: 6, end: 8 },
  { id: "ZFS:0000020", period: "Gastrula", name: "75%-epiboly", start: 8, end: 9 },
  { id: "ZFS:0000021", period: "Gastrula", name: "90%-epiboly", start: 9, end: 10 },
  { id: "ZFS:0000022", period: "Gastrula", name: "Bud", start: 10, end: 10.33 },
  { id: "ZFS:0000023", period: "Segmentation", name: "1-4 somites", start: 10.33, end: 11.66 },
  { id: "ZFS:0000024", period: "Segmentation", name: "5-9 somites", start: 11.66, end: 14 },
  { id: "ZFS:0000025", period: "Segmentation", name: "10-13 somites", start: 14, end: 16 },
  { id: "ZFS:0000026", period: "Segmentation", name: "14-19 somites", start: 16, end: 19 },
  { id: "ZFS:0000027", period: "Segmentation", name: "20-25 somites", start: 19, end: 22 },
  { id: "ZFS:0000028", period: "Segmentation", name: "26+ somites", start: 22, end: 24 },
  { id: "ZFS:0000029", period: "Pharyngula", name: "Prim-5", start: 24, end: 30 },
  { id: "ZFS:0000030", period: "Pharyngula", name: "Prim-15", start: 30, end: 36 },
  { id: "ZFS:0000031", period: "Pharyngula", name: "Prim-25", start: 36, end: 42 },
  { id: "ZFS:0000032", period: "Pharyngula", name: "High-pec", start: 42, end: 48 },
  { id: "ZFS:0000033", period: "Hatching", name: "Long-pec", start: 48, end: 60 },
  { id: "ZFS:0000034", period: "Hatching", name: "Pec-fin", start: 60, end: 72 },
  { id: "ZFS:0000035", period: "Larval", name: "Protruding-mouth", start: 72, end: 96 },
  { id: "ZFS:0000036", period: "Larval", name: "Day 4", start: 96, end: 120 },
  { id: "ZFS:0000037", period: "Larval", name: "Day 5", start: 120, end: 144 },
  { id: "ZFS:0000038", period: "Larval", name: "Day 6", start: 144, end: 168 },
  { id: "ZFS:0000039", period: "Larval", name: "Days 7-13", start: 168, end: 336 },
  { id: "ZFS:0000040", period: "Larval", name: "Days 14-20", start: 336, end: 504 },
  { id: "ZFS:0000041", period: "Larval", name: "Days 21-29", start: 504, end: 720 },
  { id: "ZFS:0000042", period: "Juvenile", name: "Days 30-44", start: 720, end: 1080 },
  { id: "ZFS:0000043", period: "Juvenile", name: "Days 45-89", start: 1080, end: 2160 },
  { id: "ZFS:0000044", period: "Adult", name: "Adult", start: 2160, end: 17520 },
];

const TIME = /^(\d+(?:\.\d+)?)\s*(hpf|dpf)$/i;

/** Hours post fertilization from "72 hpf" or "5 dpf"; null if not in that form. */
export const parseStageTime = (text: string): number | null => {
  const match = TIME.exec(text.trim());
  if (!match) return null;
  const [, amount = "", unit = ""] = match;
  return unit.toLowerCase() === "dpf" ? Number(amount) * 24 : Number(amount);
};

/** The ZFS stage a time falls in. */
export const stageAt = (text: string): Stage | undefined => {
  const hours = parseStageTime(text);
  if (hours === null) return undefined;
  return ZFS_STAGES.find((stage) => hours >= stage.start && hours < stage.end);
};
