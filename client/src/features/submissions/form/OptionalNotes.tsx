import { useState } from "react";
import { useFormContext, type FieldPath } from "react-hook-form";
import {
  EntryFooter,
  Notes,
  NotesRemove,
  NotesToggle,
  TextArea,
} from "@/styles/elements";
import Field from "./Field";
import type { Submission } from "./submission";

/** Anything the section's own fields do not capture. */
const OptionalNotes = ({ name }: { name: FieldPath<Submission> }) => {
  const [isOpen, setIsOpen] = useState(false);
  const { register } = useFormContext<Submission>();

  return (
    <EntryFooter>
      {isOpen ? (
        <Notes>
          <Field label="Notes">
            {(id) => <TextArea id={id} rows={3} {...register(name)} />}
          </Field>
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
