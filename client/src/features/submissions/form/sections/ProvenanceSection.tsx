import {
  AnnotatorPanel,
  EntryCard,
  FieldGrid,
  FieldNote,
  FieldValue,
  SelectInput,
  TextInput,
} from "@/styles/elements";
import { useFormContext } from "react-hook-form";
import Field from "../Field";
import type { Submission } from "../submission";
import OptionalNotes from "../OptionalNotes";
import { signedInUser } from "@/identity";
import {
  ORCID,
  PUBLICATION,
  PUBLISHED_SOURCES,
  ZFIN_LAB,
} from "../validation";

/** `value` is persisted; `label` is display-only. */
const SOURCES = [
  { value: "PMID", label: "PubMed ID (PMID)" },
  { value: "DOI", label: "DOI" },
  { value: "Internal database", label: "Internal database" },
  {
    value: "Non-published experimental result",
    label: "Non-published experimental result",
  },
  { value: "Other", label: "Other" },
];

/** Who produced the data and where it was published. */
const ProvenanceSection = () => {
  const identity = signedInUser();
  const { register, watch } = useFormContext<Submission>();
  const sourceType = watch("provenance.sourceType");

  return (
    <EntryCard>
      <AnnotatorPanel>
        {/* Shown, not asked for: the server takes the annotator from the
            session, so these are not inputs and are not submitted. */}
        <Field label="Annotator / submitter ORCID" labels="value">
          {(id, labelId) => (
            <FieldValue id={id} aria-labelledby={labelId}>
              {identity?.orcid_id}
            </FieldValue>
          )}
        </Field>

        <Field label="Annotator / submitter name" labels="value">
          {(id, labelId) => (
            <FieldValue id={id} aria-labelledby={labelId}>
              {identity?.name}
            </FieldValue>
          )}
        </Field>

      </AnnotatorPanel>

      <FieldGrid>
        <Field
          label="Principal investigator ORCID"
          name="provenance.principalInvestigatorOrcid"
        >
          {(id, _labelId, errorProps) => (
            <TextInput
              id={id}
              placeholder="0000-0000-0000-0000"
              {...errorProps}
              {...register("provenance.principalInvestigatorOrcid", ORCID)}
            />
          )}
        </Field>

        <Field label="Principal investigator name">
          {(id) => (
            <TextInput id={id} {...register("provenance.principalInvestigatorName")} />
          )}
        </Field>

        <Field label="Laboratory" name="provenance.laboratory">
          {(id, _labelId, errorProps) => (
            <>
              <TextInput
                id={id}
                placeholder="e.g. ZDB-LAB-251210-2"
                {...errorProps}
                {...register("provenance.laboratory", ZFIN_LAB)}
              />
              <FieldNote>
                No ZFIN lab ID?{" "}
                <a
                  href="https://zfin.org/action/profile/organization/submit"
                  target="_blank"
                  rel="noreferrer"
                >
                  Request one
                </a>
              </FieldNote>
            </>
          )}
        </Field>

        <Field label="Source of the information" required>
          {(id) => (
            <SelectInput id={id} defaultValue="" {...register("provenance.sourceType", {
              deps: "provenance.sourceValue",
            })}>
              <option value="">Select source type</option>
              {SOURCES.map((source) => (
                <option key={source.value} value={source.value}>
                  {source.label}
                </option>
              ))}
            </SelectInput>
          )}
        </Field>

            {PUBLISHED_SOURCES.includes(sourceType) && (
          <Field label="Source value" required name="provenance.sourceValue">
            {(id, _labelId, errorProps) => (
              <TextInput
                id={id}
                placeholder={
                  sourceType === "DOI"
                    ? "e.g. 10.1177/0023677219869037"
                    : "e.g. 41812223"
                }
                {...errorProps}
                {...register("provenance.sourceValue", {
                  ...PUBLICATION,
                  shouldUnregister: true,
                })}
              />
            )}
          </Field>
        )}

        {sourceType && !PUBLISHED_SOURCES.includes(sourceType) && (
          <Field label="Source note">
            {(id) => (
              <TextInput
                id={id}
                placeholder="Describe where the data comes from"
                {...register("provenance.sourceNote", { shouldUnregister: true })}
              />
            )}
          </Field>
        )}
      </FieldGrid>

      <OptionalNotes name="provenance.notes" />
    </EntryCard>
  );
};

export default ProvenanceSection;
