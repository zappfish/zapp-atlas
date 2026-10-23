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

/** `value` is persisted; `label` is display-only. */
const SOURCES = [
  { value: "PMID", label: "PubMed ID (PMID)" },
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
  const { register } = useFormContext<Submission>();

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
        <Field label="Principal investigator ORCID">
          {(id) => (
            <TextInput
              id={id}
              placeholder="0000-0000-0000-0000"
              {...register("provenance.principalInvestigatorOrcid")}
            />
          )}
        </Field>

        <Field label="Principal investigator name">
          {(id) => (
            <TextInput id={id} {...register("provenance.principalInvestigatorName")} />
          )}
        </Field>

        <Field label="Laboratory">
          {(id) => (
            <>
              <TextInput
                id={id}
                placeholder="e.g. ZDB-LAB-251210-2"
                {...register("provenance.laboratory")}
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
            <SelectInput id={id} defaultValue="" {...register("provenance.sourceType")}>
              <option value="">Select source type</option>
              {SOURCES.map((source) => (
                <option key={source.value} value={source.value}>
                  {source.label}
                </option>
              ))}
            </SelectInput>
          )}
        </Field>

        <Field label="Source value" required>
          {(id) => (
            <TextInput
              id={id}
              placeholder="PMID number, DOI url, link, etc"
              {...register("provenance.sourceValue")}
            />
          )}
        </Field>
      </FieldGrid>

      <OptionalNotes name="provenance.notes" />
    </EntryCard>
  );
};

export default ProvenanceSection;
