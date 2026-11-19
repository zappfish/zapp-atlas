import { useState } from "react";
import { useFormContext } from "react-hook-form";
import { useFishTank } from "@/api/hooks";
import type { FishTankEntry } from "@/api/types";
import { StockAdd, StockChoices, StockChosen } from "@/components/StockPanel";
import AddFishForm from "@/features/groups/AddFishForm";
import { describeFish, zfinStatus } from "@/fish";
import { toBody, type Body } from "@/schema/bodies";
import { EntryCard } from "@/styles/elements";

/**
 * The fish the experiment used, picked from the group's tank, or added to
 * it through the tank's own dialog and picked on save.
 */
const FishFromTank = ({ groupId }: { groupId: number }) => {
  const [isAdding, setIsAdding] = useState(false);
  // Which tank entry the fish was taken from, while this page is open. It is
  // not stored: the experiment keeps the description, not the link.
  const [taken, setTaken] = useState<FishTankEntry | null>(null);
  const { setValue, watch } = useFormContext<Body<"Experiment">>();
  const { data: tank = [] } = useFishTank(groupId);
  const fish = watch("fish");

  const take = (entry: FishTankEntry) => {
    setTaken(entry);
    // The experiment stores its own copy, so the tank entry can change later
    // without rewriting what this experiment said.
    setValue("fish", toBody("Fish", entry.fish), { shouldDirty: true });
  };

  const clear = () => {
    setTaken(null);
    setValue("fish", null, { shouldDirty: true });
  };

  if (fish) {
    const nickname = taken?.nickname;
    return (
      <StockChosen
        name={nickname ?? describeFish(fish)}
        detail={[nickname && describeFish(fish), taken && zfinStatus(taken.fish)]
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
const FishSection = ({ groupId }: { groupId: number }) => (
  <EntryCard>
    <FishFromTank groupId={groupId} />
  </EntryCard>
);

export default FishSection;
