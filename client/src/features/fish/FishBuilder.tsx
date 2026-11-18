import { useEffect, useMemo, useState } from "react";
import { useResolveFish, useWildtypes } from "@/api/hooks";
import type { FishBody, ZfinAllele } from "@/api/types";
import {
  isAnswered,
  resolutionText,
  toDescription,
  toFishBody,
  type AlleleChoice,
} from "@/fish";
import { ModalField, ModalLabel, ModalSelect, ModalText, ModalTextArea } from "@/styles/elements";
import AlleleCard from "./AlleleCard";
import AlleleSearch from "./AlleleSearch";

/**
 * Builds a fish description: a wild-type background, alleles with their
 * zygosity, free text for the rest. As it changes, /api/zfin/resolve is
 * called to show what ZFIN has registered for it; the server does the same
 * match on save and stores the ids.
 *
 * `onChange` gets the body when every allele has a zygosity, else null.
 */
const FishBuilder = ({
  isDisabled = false,
  onChange,
}: {
  isDisabled?: boolean;
  onChange: (fish: FishBody | null) => void;
}) => {
  const wildtypes = useWildtypes();
  const [backgroundId, setBackgroundId] = useState("");
  const [alleles, setAlleles] = useState<AlleleChoice[]>([]);
  const [lineDescription, setLineDescription] = useState("");

  const background = wildtypes.data?.find((w) => w.genotype_id === backgroundId) ?? null;
  const unanswered = alleles.filter((a) => !isAnswered(a)).length;
  const isComplete = unanswered === 0 && (alleles.length > 0 || background !== null);

  const body = useMemo(
    () => (isComplete ? toFishBody(alleles, background, lineDescription) : null),
    [isComplete, alleles, background, lineDescription],
  );
  const description = useMemo(() => (body ? toDescription(body) : null), [body]);
  const resolution = useResolveFish(description);
  useEffect(() => onChange(body), [body, onChange]);

  const add = (allele: ZfinAllele) =>
    setAlleles((was) => [
      ...was,
      { allele, zygosity: "", motherZygosity: "", fatherZygosity: "" },
    ]);
  const replace = (i: number, choice: AlleleChoice) =>
    setAlleles((was) => was.map((each, j) => (j === i ? choice : each)));
  const remove = (i: number) => setAlleles((was) => was.filter((_, j) => j !== i));

  const status = !isComplete
    ? alleles.length === 0
      ? "Choose a background or add an allele to describe the fish."
      : `${unanswered} allele${unanswered === 1 ? "" : "s"} still need${unanswered === 1 ? "s" : ""} a zygosity.`
    : resolution.isPending
      ? "Checking ZFIN…"
      : resolution.error
        ? "ZFIN's registry is not available; the fish can still be saved without its ids."
        : resolution.data
          ? resolutionText(resolution.data)
          : "";

  return (
    <>
      <ModalField>
        <ModalLabel>Wild-type background</ModalLabel>
        <ModalSelect
          value={backgroundId}
          onChange={(e) => setBackgroundId(e.target.value)}
          disabled={isDisabled || !wildtypes.data}
        >
          <option value="">
            {wildtypes.error
              ? "ZFIN's wild-type lines are not available"
              : wildtypes.data
                ? "Unknown / not recorded"
                : "Loading…"}
          </option>
          {wildtypes.data?.map((w) => (
            <option key={w.genotype_id} value={w.genotype_id}>
              {w.name}
            </option>
          ))}
        </ModalSelect>
      </ModalField>

      <AlleleSearch
        alreadyIn={new Set(alleles.map((a) => a.allele.allele_id))}
        isDisabled={isDisabled}
        onPick={add}
      />

      {alleles.map((choice, i) => (
        <AlleleCard
          key={choice.allele.allele_id}
          choice={choice}
          isDisabled={isDisabled}
          onChange={(next) => replace(i, next)}
          onRemove={() => remove(i)}
        />
      ))}

      <ModalText role="status">{status}</ModalText>
      {resolution.data && resolution.data.candidates.length > 1 && (
        <ul>
          {resolution.data.candidates.map((c) => (
            <li key={c.genotype.genotype_id}>
              {c.genotype.name_plain} ({c.genotype.genotype_id})
              {c.backgrounds.length > 0 && ` on ${c.backgrounds.map((b) => b.name).join(", ")}`}
            </li>
          ))}
        </ul>
      )}

      <ModalField>
        <ModalLabel>Notes on the line (optional)</ModalLabel>
        <ModalTextArea
          value={lineDescription}
          onChange={(e) => setLineDescription(e.target.value)}
          rows={2}
          disabled={isDisabled}
          placeholder="A line ZFIN does not have, or how this fish differs from the record it matched"
        />
      </ModalField>
    </>
  );
};

export default FishBuilder;
