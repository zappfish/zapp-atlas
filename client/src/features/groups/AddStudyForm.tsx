import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router";
import { useCreateStudy } from "@/api/hooks";
import Modal from "@/components/Modal";
import {
  PUBLICATION_HINTS,
  toPublication,
  type PublicationType,
} from "@/publication";
import {
  ModalActions,
  ModalField,
  ModalForm,
  ModalInput,
  ModalLabel,
  ModalSelect,
  ModalText,
  ModalTextArea,
  ModalTitle,
} from "@/styles/elements";

type Kind = PublicationType | "unpublished";

/** Published: its identifier. Unpublished: a nickname, which the schema
 *  requires in place of one. */
const AddStudyForm = ({
  groupId,
  open,
  onClose,
}: {
  groupId: number;
  open: boolean;
  onClose: () => void;
}) => {
  const [kind, setKind] = useState<Kind>("PMID");
  const [identifier, setIdentifier] = useState("");
  const [nickname, setNickname] = useState("");
  const [description, setDescription] = useState("");
  const [formatError, setFormatError] = useState<string | null>(null);
  const createStudy = useCreateStudy(groupId);
  const navigate = useNavigate();

  const close = () => {
    createStudy.reset();
    setKind("PMID");
    setIdentifier("");
    setNickname("");
    setDescription("");
    setFormatError(null);
    onClose();
  };

  const submit = (event: FormEvent) => {
    event.preventDefault();
    let study: { publication?: string; nickname?: string; description?: string };
    if (kind === "unpublished") {
      study = {
        nickname: nickname.trim(),
        description: description.trim() || undefined,
      };
    } else {
      const publication = toPublication(kind, identifier);
      if (!publication) {
        setFormatError(PUBLICATION_HINTS[kind].message);
        return;
      }
      study = { publication };
    }
    createStudy.mutate(study, {
      onSuccess: (created) => {
        close();
        if (created) navigate(`/research-groups/${groupId}/studies/${created.id}`);
      },
    });
  };

  return (
    <Modal open={open} title="New study" onClose={close}>
      <ModalForm onSubmit={submit}>
        <ModalTitle>New study</ModalTitle>

        <ModalField>
          <ModalLabel>Is this study published?</ModalLabel>
          <ModalSelect
            value={kind}
            onChange={(e) => {
              setKind(e.target.value as Kind);
              setFormatError(null);
            }}
          >
            <option value="PMID">Yes, it has a PubMed ID</option>
            <option value="DOI">Yes, it has a DOI</option>
            <option value="unpublished">No, not yet</option>
          </ModalSelect>
        </ModalField>

        {kind === "unpublished" ? (
          <>
            <ModalField>
              <ModalLabel>Nickname</ModalLabel>
              <ModalInput
                value={nickname}
                onChange={(e) => setNickname(e.target.value)}
                required
                maxLength={200}
                placeholder="e.g. Tamoxifen heart study"
              />
            </ModalField>
            <ModalField>
              <ModalLabel>Description</ModalLabel>
              <ModalTextArea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
                placeholder="What the study sets out to do"
              />
            </ModalField>
          </>
        ) : (
          <ModalField>
            <ModalLabel>{kind === "PMID" ? "PubMed ID" : "DOI"}</ModalLabel>
            <ModalInput
              value={identifier}
              onChange={(e) => {
                setIdentifier(e.target.value);
                setFormatError(null);
              }}
              required
              placeholder={`e.g. ${PUBLICATION_HINTS[kind].example}`}
              aria-invalid={formatError ? true : undefined}
              aria-describedby={formatError ? "study-format-error" : undefined}
            />
          </ModalField>
        )}

        {formatError && (
          <ModalText id="study-format-error" role="alert">
            {formatError}
          </ModalText>
        )}
        {createStudy.error && (
          <ModalText role="alert">{createStudy.error.message}</ModalText>
        )}

        <ModalActions>
          <button className="btn btn--neutral" type="button" onClick={close}>
            Cancel
          </button>
          <button
            className="btn btn--primary"
            type="submit"
            disabled={createStudy.isPending}
          >
            {createStudy.isPending ? "Adding…" : "Add study"}
          </button>
        </ModalActions>
      </ModalForm>
    </Modal>
  );
};

export default AddStudyForm;
