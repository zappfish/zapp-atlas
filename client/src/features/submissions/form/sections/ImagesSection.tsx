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
import { useFieldArray, useFormContext } from "react-hook-form";
import Field from "../Field";
import { emptyImage, type Submission } from "../submission";
import OptionalNotes from "../OptionalNotes";
import { ImageUpload, Measure } from "../imageEntry";
import { MEASURES } from "../measures";

const ImageEntry = ({
  n,
  index,
  onRemove,
}: {
  n: number;
  index: number;
  onRemove?: () => void;
}) => {
  const { register } = useFormContext<Submission>();

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
        <ImageUpload name={`images.${index}.file`} />

        <EntryMeta>
          {MEASURES.map(({ field, unitField, ...measure }) => (
            <Measure
              key={measure.label}
              {...measure}
              name={`images.${index}.${field}` as const}
              unitName={`images.${index}.${unitField}` as const}
            />
          ))}

          <Field label="Microscope information">
            {(id) => (
              <TextInput
                id={id}
                placeholder="Enter text"
                {...register(`images.${index}.microscope`)}
              />
            )}
          </Field>
        </EntryMeta>
      </EntryBody>

      {/* Below both columns: a note is wider than it is tall, and keeping it
          out of the column stops that column outgrowing the image beside it. */}
      <OptionalNotes name={`images.${index}.notes`} />
    </EntryCard>
  );
};

/** Each image carries its own metadata, which may differ between them. */
const ImagesSection = () => {
  const { control } = useFormContext<Submission>();
  const { fields, append, remove } = useFieldArray({ control, name: "images" });

  return (
    <>
      {fields.map((field, i) => (
        <ImageEntry
          key={field.id}
          n={i + 1}
          index={i}
          onRemove={fields.length > 1 ? () => remove(i) : undefined}
        />
      ))}

      <AddRow>
        <AddButton type="button" onClick={() => append(emptyImage())}>
          + Upload another image
        </AddButton>
      </AddRow>
    </>
  );
};

export default ImagesSection;
