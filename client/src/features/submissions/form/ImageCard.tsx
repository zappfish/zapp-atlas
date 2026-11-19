import { useState } from "react";
import { FormProvider, useForm, useFormContext } from "react-hook-form";
import { ApiError } from "@/api/client";
import { useDeleteImage, useReplaceImage, useUploadImage } from "@/api/hooks";
import { imageUrl } from "@/api/images";
import type { Image } from "@/api/types";
import ConfirmDialog from "@/components/ConfirmDialog";
import { bodyResolver, showProblems } from "@/problems";
import { ImageScopeEnum } from "@/schema";
import { sameBody, toBody, type Body } from "@/schema/bodies";
import {
  EntryActions,
  EntryBody,
  EntryForm,
  EntryHead,
  EntryRemove,
  EntryStatus,
  EntryTitle,
  EntryMeta,
  PreviewImage,
  RadioGroup,
  RadioLabel,
  Upload,
  UploadChosen,
} from "@/styles/elements";
import Field from "./Field";
import { ImageUpload, Measure } from "./imageEntry";
import { MEASURES } from "./measures";
import { UPLOAD_INFO } from "./explanations";

type Values = Body<"Image">;

const SCOPES: { value: `${ImageScopeEnum}`; label: string }[] = [
  { value: "whole_organism", label: "The whole fish" },
  { value: "partial_organism", label: "Part of the fish" },
];

/** What is said about an image, whether or not its file is uploaded yet. */
const Description = () => {
  const { register } = useFormContext<Values>();
  return (
    <EntryMeta>
      {MEASURES.map(({ slot, ...measure }) => (
        <Measure key={slot} {...measure} name={slot} />
      ))}

      <Field label="What the image shows" labels="value">
        {(_id, labelId) => (
          <RadioGroup role="radiogroup" aria-labelledby={labelId}>
            {SCOPES.map((option) => (
              <RadioLabel key={option.value}>
                <input
                  type="radio"
                  value={option.value}
                  {...register("image_scope")}
                />
                {option.label}
              </RadioLabel>
            ))}
          </RadioGroup>
        )}
      </Field>
    </EntryMeta>
  );
};

/**
 * One image of an observation, saved on its own. A new one is a file and
 * what is said about it, uploaded together; a saved one's file stays as it
 * was uploaded, and what is said about it can be changed.
 */
const ImageCard = ({
  n,
  studyId,
  observationId,
  saved,
  onLeave,
}: {
  n: number;
  studyId: number;
  observationId: number;
  /** Absent for an image that has not been uploaded yet. */
  saved?: Image;
  /** An image that was never uploaded is discarded, or uploaded and listed anew. */
  onLeave?: () => void;
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [missing, setMissing] = useState(false);
  const [removing, setRemoving] = useState(false);

  const upload = useUploadImage(studyId, observationId);
  const replace = useReplaceImage(studyId, saved?.id ?? 0);
  const remove = useDeleteImage(studyId);
  const save = saved ? replace : upload;

  const form = useForm<Values>({
    values: saved ? toBody("Image", saved) : {},
    resolver: bodyResolver("Image"),
  });
  const isSaved = saved && sameBody("Image", form.watch(), saved);

  // Anything the server found that the schema could not say.
  const refused = (error: Error) => {
    if (error instanceof ApiError) showProblems(form.setError, error.problems);
  };

  const submit = form.handleSubmit((values) => {
    const description = toBody("Image", values);
    if (saved) {
      replace.mutate(description, { onError: refused });
    } else if (file) {
      upload.mutate({ file, description }, { onSuccess: onLeave, onError: refused });
    } else {
      setMissing(true);
    }
  });

  return (
    <FormProvider {...form}>
      <EntryForm onSubmit={submit} aria-label={`Image ${n}`}>
        <EntryHead>
          <EntryTitle>Image {n}</EntryTitle>
          <EntryRemove
            type="button"
            onClick={saved ? () => setRemoving(true) : onLeave}
          >
            Remove
          </EntryRemove>
        </EntryHead>

        <EntryBody>
          {saved ? (
            <Upload>
              <UploadChosen>
                <PreviewImage src={imageUrl(saved.id)} alt={`Image ${n}`} />
              </UploadChosen>
            </Upload>
          ) : (
            <ImageUpload
              onChoose={(chosen) => {
                setFile(chosen);
                setMissing(false);
              }}
              error={missing ? "Choose an image." : undefined}
              info={<p>{UPLOAD_INFO}</p>}
            />
          )}

          <Description />
        </EntryBody>

        <EntryActions>
          <EntryStatus role="status">
            {save.error
              ? save.error.message
              : !saved
                ? "Not uploaded yet."
                : isSaved
                  ? "Saved."
                  : "Changes not saved."}
          </EntryStatus>
          <button className="btn btn--primary" type="submit" disabled={save.isPending}>
            {save.isPending ? "Saving…" : saved ? "Save image" : "Upload image"}
          </button>
        </EntryActions>

        {/* Inside the card, so that one card still directly follows another. */}
        {saved && (
          <ConfirmDialog
            open={removing}
            title="Remove image"
            message={`Remove image ${n} and its file?`}
            isPending={remove.isPending}
            error={remove.error?.message}
            onConfirm={() => remove.mutate(saved.id)}
            onClose={() => {
              remove.reset();
              setRemoving(false);
            }}
          />
        )}
      </EntryForm>
    </FormProvider>
  );
};

export default ImageCard;
