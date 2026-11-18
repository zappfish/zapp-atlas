import { useState } from "react";
import { useFormContext } from "react-hook-form";
import { useFishTank } from "@/api/hooks";
import type { FishTankEntry } from "@/api/types";
import AddFishForm from "@/features/groups/AddFishForm";
import { describeFish, zfinStatus } from "@/fish";
import {
  EntryCard,
  FieldGrid,
  SelectInput,
  SubstanceAdd,
  SubstanceBody,
  SubstanceCard,
  SubstanceChange,
  SubstanceChoices,
  SubstanceChosen,
  SubstanceId,
  SubstanceLead,
  SubstanceName,
  SubstanceNames,
  SubstanceOr,
  SubstanceTitle,
  TextInput,
} from "@/styles/elements";
import Field from "../Field";
import type { Submission } from "../submission";

/**
 * The fish the experiment used, picked from the group's tank, or added to
 * it through the tank's own dialog and picked on save.
 */
const FishFromTank = ({ groupId }: { groupId: number }) => {
  const [isAdding, setIsAdding] = useState(false);
  const { setValue, watch } = useFormContext<Submission>();
  const { data: tank = [] } = useFishTank(groupId);
  const [entryId, description] = watch(["fish.entryId", "fish.description"]);

  const take = (entry: FishTankEntry) => {
    setValue("fish.entryId", String(entry.id));
    // The experiment stores its own copy, so the tank entry can change later
    // without rewriting what this submission said.
    setValue("fish.description", { ...entry.fish });
  };

  const clear = () => {
    setValue("fish.entryId", "");
    setValue("fish.description", null);
  };

  if (description) {
    const entry = tank.find((row) => String(row.id) === entryId);
    return (
      <SubstanceCard>
        <SubstanceChosen>
          <SubstanceNames>
            <SubstanceName>{entry?.nickname ?? describeFish(description)}</SubstanceName>
            <SubstanceId>
              {entry?.nickname ? `${describeFish(description)} · ` : ""}
              {zfinStatus(description)}
            </SubstanceId>
          </SubstanceNames>
          <SubstanceChange type="button" onClick={clear}>
            Change
          </SubstanceChange>
        </SubstanceChosen>
      </SubstanceCard>
    );
  }

  return (
    <SubstanceCard>
      <SubstanceBody>
        <SubstanceTitle>
          From your tank ({tank.length} fish line{tank.length === 1 ? "" : "s"})
        </SubstanceTitle>
        <SubstanceChoices>
          {tank.length > 0 ? (
            <SelectInput
              defaultValue=""
              aria-label="Select a fish line from your tank"
              onChange={(e) => {
                const entry = tank.find((row) => String(row.id) === e.target.value);
                if (entry) take(entry);
              }}
            >
              <option value="" disabled>
                Select a fish line
              </option>
              {tank.map((row) => (
                <option key={row.id} value={row.id}>
                  {row.nickname ? `${row.nickname} — ${describeFish(row.fish)}` : describeFish(row.fish)}
                </option>
              ))}
            </SelectInput>
          ) : (
            <SubstanceLead>Your tank is empty.</SubstanceLead>
          )}

          <SubstanceOr>OR</SubstanceOr>

          <SubstanceAdd type="button" onClick={() => setIsAdding(true)}>
            + Add a fish line to the tank
          </SubstanceAdd>
        </SubstanceChoices>
      </SubstanceBody>

      <AddFishForm
        groupId={groupId}
        open={isAdding}
        onClose={() => setIsAdding(false)}
        onAdded={take}
      />
    </SubstanceCard>
  );
};

/** The fish the experiment used. */
const FishSection = ({ groupId }: { groupId: number }) => {
  const { register } = useFormContext<Submission>();

  return (
    <EntryCard>
      <FishFromTank groupId={groupId} />

      <FieldGrid>
        <Field label="Additional condition">
          {(id) => <TextInput id={id} {...register("fish.additionalCondition")} />}
        </Field>
      </FieldGrid>
    </EntryCard>
  );
};

export default FishSection;
