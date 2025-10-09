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

const DurationSchema = z.object({
  value: z.number().nonnegative().nullable(),
  unit: z.enum(['minute', 'hour', 'day']).nullable()
})

const RepeatedExposureSchema = z.object({
  count: z.number().int().nonnegative().nullable(),
  duration_per: DurationSchema,
  interval_between: DurationSchema,
  total_length: DurationSchema,
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


// FIXME: This should really have a `regimen` key.
const ExposureEventSchema = z.object({
  substance: SubstanceIdSchema,
  concentration: z.object({
    value: z.number().nonnegative().nullable(),
    unit: z.string().nullable()
  }),
  route: z.enum(['water', 'injected', 'ingested', 'gavage']).nullable(),
  type: z.enum(['continuous', 'repeated']).nullable(),
  textual_description: z.string().nullable(),
  pattern: z.enum(['static', 'static_renewal', 'flow_through']).nullable(),
  duration: z.object({
    value: z.number().nonnegative().nullable(),
    unit: z.enum(['minute', 'hour', 'day']).nullable()
  }),
  start_stage: StageSchema,
  end_stage: StageSchema,
  repeated: RepeatedExposureSchema,
  additional_notes: z.string().optional()
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
  exposures: z.array(ExposureEventSchema),
  phenotype: z.object({
    observation_stage: StageSchema,
    items: z.array(PhenotypeItemSchema),
    additional_notes: z.string().optional()
  })
});

export type ZappObservation = z.infer<typeof ZappObservationSchema>;
