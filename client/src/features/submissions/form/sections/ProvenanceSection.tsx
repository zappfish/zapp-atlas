import { useCallback, useState } from "react";
import {
  EntryCard,
  EntryFooter,
  FieldGrid,
  FieldNote,
  Notes,
  NotesRemove,
  NotesToggle,
  SelectInput,
  TextArea,
  TextInput,
} from "@/styles/elements";
import Field from "../Field";

const SOURCES = [
  "PMID",
  "Internal database",
  "Non-published experimental result",
  "Other",
];

/** Who produced the data and where it was published. */
const ProvenanceSection = () => {
  const [notesOpen, setNotesOpen] = useState(false);
  const openNotes = useCallback(() => setNotesOpen(true), []);
  const closeNotes = useCallback(() => setNotesOpen(false), []);

  return (
    <EntryCard>
      <FieldGrid>
        {/* Read-only: you signed in with ORCID to reach this form, so these
            are known rather than asked for. Empty until the client can read
            the signed-in identity. */}
        <Field label="Annotator / submitter ORCID" required>
          {(id) => <TextInput id={id} readOnly placeholder="0000-0000-0000-0000" />}
        </Field>

        <Field label="Annotator / submitter name">
          {(id) => <TextInput id={id} readOnly />}
        </Field>

        <Field label="Principal investigator ORCID">
          {(id) => <TextInput id={id} placeholder="0000-0000-0000-0000" />}
        </Field>

        <Field label="Principal investigator name" hint="Filled in from the ORCID above.">
          {(id) => <TextInput id={id} />}
        </Field>

        <Field label="Laboratory">
          {(id) => (
            <>
              <TextInput id={id} placeholder="e.g. ZDB-LAB-120909-1" />
              <FieldNote>
                No ZFIN lab ID?{" "}
                <a
                  href="https://zfin.org/action/lab/new"
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
            <SelectInput id={id} defaultValue="">
              <option value="">Select source type</option>
              {SOURCES.map((source) => (
                <option key={source}>{source}</option>
              ))}
            </SelectInput>
          )}
        </Field>

        <Field label="Source value" required>
          {(id) => (
            <TextInput id={id} placeholder="PMID number, DOI url, link, etc" />
          )}
        </Field>
      </FieldGrid>

      <EntryFooter>
        {notesOpen ? (
          <Notes>
            <Field label="Notes">{(id) => <TextArea id={id} rows={3} />}</Field>
            <NotesRemove type="button" onClick={closeNotes}>
              Remove notes
            </NotesRemove>
          </Notes>
        ) : (
          <NotesToggle type="button" onClick={openNotes}>
            Add notes
          </NotesToggle>
        )}
      </EntryFooter>
    </EntryCard>
  );
};

export default ProvenanceSection;
