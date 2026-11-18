import { useState } from "react";
import { useFormContext } from "react-hook-form";
import { useFishTank } from "@/api/hooks";
import type { FishTankEntry } from "@/api/types";
import { StockAdd, StockChoices, StockChosen } from "@/components/StockPanel";
import AddFishForm from "@/features/groups/AddFishForm";
import { describeFish, zfinStatus } from "@/fish";
import { EntryCard, FieldGrid, TextInput } from "@/styles/elements";
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
    const nickname = tank.find((row) => String(row.id) === entryId)?.nickname;
    return (
      <StockChosen
        name={nickname ?? describeFish(description)}
        detail={[nickname && describeFish(description), zfinStatus(description)]
          .filter(Boolean)
          .join(" · ")}
        onChange={clear}
      />
    );
  }

  const add = (
    <StockAdd type="button" onClick={() => setIsAdding(true)}>
      + Add a fish line to the tank
    </StockAdd>
  );

  return (
    <StockChoices
      title={`From your tank (${tank.length} fish line${tank.length === 1 ? "" : "s"})`}
      selectLabel="Select a fish line from your tank"
      placeholder="Select a fish line"
      options={tank.map((row) => ({
        value: String(row.id),
        label: row.nickname ? `${row.nickname} — ${describeFish(row.fish)}` : describeFish(row.fish),
      }))}
      onPick={(value) => {
        const entry = tank.find((row) => String(row.id) === value);
        if (entry) take(entry);
      }}
      emptyText="Your tank is empty."
      alternatives={add}
    >
      <AddFishForm
        groupId={groupId}
        open={isAdding}
        onClose={() => setIsAdding(false)}
        onAdded={take}
      />
    </StockChoices>
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
