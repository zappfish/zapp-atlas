import {
  AddButton,
  AddRow,
  EntryBody,
  EntryCard,
  EntryHead,
  EntryRemove,
  EntryTitle,
  EntryMeta,
  TextInput,
} from "@/styles/elements";
import Field from "../Field";
import OptionalNotes from "../OptionalNotes";
import { useEntries } from "../useEntries";
import { ImageUpload, Measure } from "../imageEntry";
import { MEASURES } from "../measures";

const ImageEntry = ({ n, onRemove }: { n: number; onRemove?: () => void }) => {

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
      <OptionalNotes />
    </EntryCard>
  );
};

/** Each image carries its own metadata, which may differ between them. */
const ImagesSection = () => {
  const { ids, add, remove } = useEntries();

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
