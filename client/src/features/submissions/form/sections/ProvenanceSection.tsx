import { useCallback, useState } from "react";
import {
  EntryCard,
  EntryFooter,
  FieldGrid,
  FieldNote,
  FieldValue,
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

        <Field label="Principal investigator ORCID">
          {(id) => <TextInput id={id} placeholder="0000-0000-0000-0000" />}
        </Field>

        <Field label="Principal investigator name">
          {(id) => <TextInput id={id} />}
        </Field>

        <Field label="Laboratory">
          {(id) => (
            <>
              <TextInput id={id} placeholder="e.g. ZDB-LAB-120909-1" />
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
