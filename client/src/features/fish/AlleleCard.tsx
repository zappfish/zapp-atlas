import type { ParentZygosity, Zygosity } from "@/api/types";
import {
  PARENT_ZYGOSITIES,
  ZYGOSITIES,
  alleleDescription,
  mutagenGloss,
  zfinUrl,
  type AlleleChoice,
} from "@/fish";
import {
  EntryBody,
  EntryCard,
  EntryHead,
  EntryMeta,
  EntryRemove,
  EntryTitle,
  ModalField,
  ModalLabel,
  ModalSelect,
} from "@/styles/elements";

/** One allele on the fish: ZFIN's details, and the zygosity chosen for it. */
const AlleleCard = ({
  choice,
  isDisabled = false,
  onChange,
  onRemove,
}: {
  choice: AlleleChoice;
  isDisabled?: boolean;
  onChange: (choice: AlleleChoice) => void;
  onRemove: () => void;
}) => {
  const { allele } = choice;
  const gene = allele.genes.map((g) => `${g.symbol} (${g.gene_id})`).join(", ");
  const constructs = allele.constructs.map((c) => `${c.name} (${c.construct_id})`).join(", ");

  return (
    <EntryCard>
      <EntryHead>
        <EntryTitle>
          {allele.symbol}
          {allele.is_transgenic && " · Tg"}
        </EntryTitle>
        <a href={zfinUrl(allele.allele_id)} target="_blank" rel="noopener noreferrer">
          View on ZFIN ↗
        </a>
        <EntryRemove type="button" onClick={onRemove} disabled={isDisabled}>
          Remove
        </EntryRemove>
      </EntryHead>

      <EntryBody>
        <EntryMeta>{alleleDescription(allele)}</EntryMeta>
        {gene && <EntryMeta>Gene: {gene}</EntryMeta>}
        {constructs && <EntryMeta>Construct: {constructs}</EntryMeta>}
        {allele.mutagen && <EntryMeta>Made with: {mutagenGloss(allele.mutagen)}</EntryMeta>}
        <EntryMeta>Allele id: {allele.allele_id}</EntryMeta>

        <ModalField>
          <ModalLabel>Zygosity in this fish</ModalLabel>
          <ModalSelect
            value={choice.zygosity}
            onChange={(e) => onChange({ ...choice, zygosity: e.target.value as Zygosity | "" })}
            required
            disabled={isDisabled}
          >
            <option value="" disabled>
              Choose…
            </option>
            {ZYGOSITIES.map((z) => (
              <option key={z.value} value={z.value}>
                {z.label}
              </option>
            ))}
          </ModalSelect>
        </ModalField>

        <details open={choice.motherZygosity !== "unknown" || choice.fatherZygosity !== "unknown"}>
          <summary>Parents' zygosity, if known</summary>
          <ModalField>
            <ModalLabel>Mother</ModalLabel>
            <ModalSelect
              value={choice.motherZygosity}
              onChange={(e) => onChange({ ...choice, motherZygosity: e.target.value as ParentZygosity })}
              disabled={isDisabled}
            >
              {PARENT_ZYGOSITIES.map((z) => (
                <option key={z.value} value={z.value}>
                  {z.label}
                </option>
              ))}
            </ModalSelect>
          </ModalField>
          <ModalField>
            <ModalLabel>Father</ModalLabel>
            <ModalSelect
              value={choice.fatherZygosity}
              onChange={(e) => onChange({ ...choice, fatherZygosity: e.target.value as ParentZygosity })}
              disabled={isDisabled}
            >
              {PARENT_ZYGOSITIES.map((z) => (
                <option key={z.value} value={z.value}>
                  {z.label}
                </option>
              ))}
            </ModalSelect>
          </ModalField>
        </details>
      </EntryBody>
    </EntryCard>
  );
};

export default AlleleCard;
