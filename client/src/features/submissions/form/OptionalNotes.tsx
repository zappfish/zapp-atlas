import { useState } from "react";
import { useFormContext } from "react-hook-form";
import {
  EntryFooter,
  FieldHint,
  Notes,
  NotesFoot,
  NotesRemove,
  NotesToggle,
  TextArea,
} from "@/styles/elements";
import Field from "./Field";

/** Anything the section's own fields do not capture. */
const OptionalNotes = ({ name }: { name: string }) => {
  const { register, getValues } = useFormContext();
  // Open on notes that were saved, so they are not hidden behind the toggle.
  const [isOpen, setIsOpen] = useState(() => Boolean(getValues(name)));

  return (
    <EntryFooter>
      {isOpen ? (
        <Notes>
          <Field label="Notes">
            {(id) => <TextArea id={id} rows={3} {...register(name)} />}
          </Field>
          <NotesFoot>
            <FieldHint>These notes will be publicly visible in the Atlas.</FieldHint>
            <NotesRemove type="button" onClick={() => setIsOpen(false)}>
              Remove notes
            </NotesRemove>
          </NotesFoot>
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
