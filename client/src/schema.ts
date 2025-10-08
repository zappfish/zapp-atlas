import { z } from 'zod';

const IdRefSchema = z.object({
  type: z.enum(['PMID', 'DOI', 'Other publication', 'Internal database', 'Non-published experimental result', 'Other']).optional(),
  value: z.string().optional()
});

const ImageMetaSchema = z.object({
  name: z.string().optional(),
  type: z.string().optional(),
  size: z.number().optional()
});

const StageSchema = z.object({
  value: z.number().nonnegative().nullable(),
  unit: z.enum(['hpf', 'dpf', 'month']).nullable()
});

const RepeatedExposureSchema = z.object({
  duration_per_exposure_hours: z.number().nonnegative().nullable(),
  frequency_count: z.number().int().nonnegative().nullable(),
  interval_hours: z.number().nonnegative().nullable()
});

const SubstanceIdSchema = z.object({
  name: z.string().optional(),
  idType: z.enum(['PubChem', 'CAS', 'ChEBI', 'None']).default('None'),
  id: z.string().optional()
});

const PhenotypeItemSchema = z.object({
  termId: z.string().optional(), // TODO: ontology picker will fill this
  termLabel: z.string().optional(),
  prevalencePercent: z.number().min(0).max(100).nullable().optional(),
  severity: z.enum(['mild', 'moderate', 'severe']).nullable().optional()
});

export const ZappObservationSchema = z.object({
  provenance: z.object({
    annotator_orcid: z.string().optional(),
    source: IdRefSchema,
    additional_notes: z.string().optional()
  }),
  image: z.object({
    file: ImageMetaSchema.nullable(),
    additional_notes: z.string().optional()
  }),
  fish: z.object({
    strain_background: z.string().optional(),
    description: z.string().optional(),
    additional_notes: z.string().optional()
  }),
  rearing: z.object({
    standard: z.boolean(),
    non_standard_notes: z.string().optional(),
    additional_notes: z.string().optional()
  }),
  exposure: z.object({
    substance: SubstanceIdSchema,
    concentration: z.object({
      value: z.number().nonnegative().nullable(),
      unit: z.enum(['uM', 'mg/L']).nullable()
    }),
    route: z.enum(['water', 'injected', 'ingested', 'gavage']).nullable(),
    type: z.enum(['continuous', 'repeated']).nullable(),
    pattern: z.enum(['static', 'static_renewal', 'flow_through']).nullable(),
    duration: z.object({
      value: z.number().nonnegative().nullable(),
      unit: z.enum(['hour', 'min']).nullable()
    }),
    start_stage: StageSchema,
    end_stage: StageSchema,
    repeated: RepeatedExposureSchema,
    additional_notes: z.string().optional()
  }),
  phenotype: z.object({
    observation_stage: StageSchema,
    items: z.array(PhenotypeItemSchema),
    additional_notes: z.string().optional()
  })
});

export type ZappObservation = z.infer<typeof ZappObservationSchema>;
