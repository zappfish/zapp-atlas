import { useCallback, useRef, useState } from "react";
import {
  AddButton,
  AddRow,
  EntryBody,
  EntryCard,
  EntryHead,
  EntryRemove,
  EntryTitle,
  EntryFooter,
  EntryMeta,
  Notes,
  NotesRemove,
  NotesToggle,
  TextArea,
  TextInput,
} from "@/styles/elements";
import Field from "../Field";
import { ImageUpload, Measure } from "../imageEntry";
import { MEASURES } from "../measures";

const ImageEntry = ({ n, onRemove }: { n: number; onRemove?: () => void }) => {
  const [notesOpen, setNotesOpen] = useState(false);
  const openNotes = useCallback(() => setNotesOpen(true), []);
  const closeNotes = useCallback(() => setNotesOpen(false), []);

  return (
    <EntryCard>
      <EntryHead>
        <EntryTitle>Image {n}</EntryTitle>
        {onRemove && (
          <EntryRemove type="button" onClick={onRemove}>
            Remove
          </EntryRemove>
        )}
      </EntryHead>

      <EntryBody>
        <ImageUpload />

        <EntryMeta>
          {MEASURES.map((measure) => (
            <Measure key={measure.label} {...measure} />
          ))}

          <Field label="Microscope information">
            {(id) => <TextInput id={id} placeholder="Enter text" />}
          </Field>
        </EntryMeta>
      </EntryBody>

      {/* Below both columns: a note is wider than it is tall, and keeping it
          out of the column stops that column outgrowing the image beside it. */}
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

/** Each image carries its own metadata, which may differ between them. */
const ImagesSection = () => {
  // Ids rather than a count: removing one must not renumber those after it.
  const [ids, setIds] = useState([0]);
  const next = useRef(1);
  const add = useCallback(() => setIds((was) => [...was, next.current++]), []);
  const remove = useCallback(
    (id: number) => setIds((was) => was.filter((each) => each !== id)),
    [],
  );

  return (
    <>
      {ids.map((id, i) => (
        <ImageEntry
          key={id}
          n={i + 1}
          onRemove={ids.length > 1 ? () => remove(id) : undefined}
        />
      ))}

      <AddRow>
        <AddButton type="button" onClick={add}>
          + Upload another image
        </AddButton>
      </AddRow>
    </>
  );
};

export default ImagesSection;
