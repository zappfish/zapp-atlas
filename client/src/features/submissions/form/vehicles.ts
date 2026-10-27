import { VehicleEnum } from "@/schema";

/** The schema's labels, which codegen keeps only as comments. A Record over
 *  the enum, so a vehicle added to the schema fails the build until named. */
export const VEHICLE_LABELS: Record<VehicleEnum, string> = {
  [VehicleEnum.acetone]: "Acetone",
  [VehicleEnum.acetonitrile]: "Acetonitrile",
  [VehicleEnum.bsa]: "Bovine serum albumin (BSA)",
  [VehicleEnum.butanone_mek]: "Butanone (MEK)",
  [VehicleEnum.cyclodextrin_hpbcd]: "Cyclodextrin (HPBCD)",
  [VehicleEnum.dimethyl_formamide]: "Dimethyl formamide (DMF)",
  [VehicleEnum.dmso]: "Dimethyl sulfoxide (DMSO)",
  [VehicleEnum.embryonic_media]: "Embryonic Media (EM/E3)",
  [VehicleEnum.ethanol]: "Ethanol",
  [VehicleEnum.glycerol]: "Glycerol",
  [VehicleEnum.isopropanol]: "Isopropanol",
  [VehicleEnum.methanol]: "Methanol",
  [VehicleEnum.methylcellulose]: "Methylcellulose",
  [VehicleEnum.pbs]: "Phosphate-buffered saline (PBS)",
  [VehicleEnum.polyethylene_glycol]: "Polyethylene glycol",
  [VehicleEnum.propylene_glycol]: "Propylene glycol",
  [VehicleEnum.solketal]: "Solketal",
  [VehicleEnum.water]: "Water",
  [VehicleEnum.other_not_listed]: "Other (not listed)",
};
