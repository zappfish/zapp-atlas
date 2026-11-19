import { useForm } from "react-hook-form";
import { ApiError } from "@/api/client";
import { useReplaceStudy } from "@/api/hooks";
import type { Study, StudyBody } from "@/api/types";
import Modal from "@/components/Modal";
import { bodyResolver, showProblems } from "@/problems";
import { toBody } from "@/schema/bodies";
import {
  ModalActions,
  ModalField,
  ModalForm,
  ModalInput,
  ModalLabel,
  ModalText,
  ModalTextArea,
  ModalTitle,
} from "@/styles/elements";
import { ownFields } from "./studyFields";

/**
 * A study's own fields. What is checked, and what each message says, comes
 * from the schema: a publication is a PMID or a DOI, and a study without one
 * needs a nickname.
 */
const EditStudyForm = ({
  groupId,
  study,
  open,
  onClose,
}: {
  groupId: number;
  study: Study;
  open: boolean;
  onClose: () => void;
}) => {
  const replaceStudy = useReplaceStudy(groupId, study.id);
  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors },
  } = useForm<StudyBody>({
    values: ownFields(study),
    resolver: bodyResolver("Study"),
  });

  const close = () => {
    replaceStudy.reset();
    reset();
    onClose();
  };

  const save = handleSubmit((values) =>
    replaceStudy.mutate(toBody("Study", values), {
      onSuccess: close,
      // Anything the server found that the schema could not say.
      onError: (error) => {
        if (error instanceof ApiError) showProblems(setError, error.problems);
      },
    }),
  );

  return (
    <Modal open={open} title="Edit study" onClose={close}>
      <ModalForm onSubmit={save}>
        <ModalTitle>Edit study</ModalTitle>

        <ModalField>
          <ModalLabel>Publication</ModalLabel>
          <ModalInput
            placeholder="PMID:41812223 or DOI:10.1000/xyz123"
            aria-invalid={errors.publication ? true : undefined}
            {...register("publication")}
          />
          {errors.publication && (
            <ModalText role="alert">{errors.publication.message}</ModalText>
          )}
        </ModalField>

        <ModalField>
          <ModalLabel>Nickname</ModalLabel>
          <ModalInput
            maxLength={200}
            placeholder="e.g. Tamoxifen heart study"
            aria-invalid={errors.nickname ? true : undefined}
            {...register("nickname")}
          />
          {errors.nickname && (
            <ModalText role="alert">{errors.nickname.message}</ModalText>
          )}
        </ModalField>

        <ModalField>
          <ModalLabel>Description</ModalLabel>
          <ModalTextArea
            rows={3}
            placeholder="What the study sets out to do"
            {...register("description")}
          />
        </ModalField>

        <ModalField>
          <ModalLabel>ZFIN lab</ModalLabel>
          <ModalInput
            placeholder="e.g. ZFIN:ZDB-LAB-251210-2"
            aria-invalid={errors.lab ? true : undefined}
            {...register("lab")}
          />
          {errors.lab && <ModalText role="alert">{errors.lab.message}</ModalText>}
        </ModalField>

        {replaceStudy.error && (
          <ModalText role="alert">{replaceStudy.error.message}</ModalText>
        )}

        <ModalActions>
          <button className="btn btn--neutral" type="button" onClick={close}>
            Cancel
          </button>
          <button
            className="btn btn--primary"
            type="submit"
            disabled={replaceStudy.isPending}
          >
            {replaceStudy.isPending ? "Saving…" : "Save"}
          </button>
        </ModalActions>
      </ModalForm>
    </Modal>
  );
};

export default EditStudyForm;
