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

/**
 * Written into the document by app.html, so it is there on the first render
 * with no request. Display only — the server derives a submission's annotator
 * from the session cookie, it is never sent in the payload.
 */
declare global {
  interface Window {
    ZAPP_SIGNED_IN_USER?: { orcid_id: string; name: string | null } | null;
  }
}

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
  const identity = window.ZAPP_SIGNED_IN_USER;

  return (
    <EntryCard>
      <FieldGrid>
        {/* Read-only: the ORCID sign-in already established who this is. */}
        <Field
          label="Annotator / submitter ORCID"
          required
          hint="From your ORCID sign-in."
        >
          {(id) => (
            <TextInput id={id} readOnly value={identity?.orcid_id ?? ""} />
          )}
        </Field>

        <Field label="Annotator / submitter name" hint="From your ORCID sign-in.">
          {(id) => <TextInput id={id} readOnly value={identity?.name ?? ""} />}
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
