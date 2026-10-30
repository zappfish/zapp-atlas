import { useState } from "react";
import RecordSection from "@/components/RecordSection";
import AddStudyForm from "./AddStudyForm";

/** Empty until the API can list one group's studies; adding one opens it. */
const StudiesSection = ({ groupId }: { groupId: number }) => {
  const [adding, setAdding] = useState(false);

  return (
    <>
      <RecordSection
        id="studies"
        title="Studies"
        rows={[]}
        emptyTitle="No studies yet"
        emptyText="Add a study to group this lab's submissions under it."
        emptyAction={
          <button
            className="btn btn--secondary"
            type="button"
            onClick={() => setAdding(true)}
          >
            + New study
          </button>
        }
      />

      <AddStudyForm
        groupId={groupId}
        open={adding}
        onClose={() => setAdding(false)}
      />
    </>
  );
};

export default StudiesSection;
