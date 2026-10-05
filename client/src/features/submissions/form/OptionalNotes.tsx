import { useState } from "react";
import {
  EntryFooter,
  Notes,
  NotesRemove,
  NotesToggle,
  TextArea,
} from "@/styles/elements";
import Field from "./Field";

/** Anything the section's own fields do not capture. */
const OptionalNotes = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <EntryFooter>
      {isOpen ? (
        <Notes>
          <Field label="Notes">{(id) => <TextArea id={id} rows={3} />}</Field>
          <NotesRemove type="button" onClick={() => setIsOpen(false)}>
            Remove notes
          </NotesRemove>
        </Notes>
      ) : (
        <NotesToggle type="button" onClick={() => setIsOpen(true)}>
          Add notes
        </NotesToggle>
      )}
    </EntryFooter>
  );
};

export default OptionalNotes;
