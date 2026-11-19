import { useFormContext } from "react-hook-form";
import {
  ActionsHint,
  ActionsPrompt,
  ActionsTitle,
  FormActionBar,
} from "@/styles/elements";
import type { Submission } from "./submission";

/** Sticky: the form is long. No endpoints yet, so both buttons only log. */
const FormActions = () => {
  const { getValues } = useFormContext<Submission>();

  return (
    <FormActionBar>
      <ActionsPrompt>
        <ActionsTitle>Ready to submit?</ActionsTitle>
        <ActionsHint>Complete all required fields to continue.</ActionsHint>
      </ActionsPrompt>
      <button
        className="btn btn--secondary"
        type="button"
        onClick={() => console.log("Draft", getValues())}
      >
        Save draft
      </button>
      <button className="btn btn--primary" type="submit">
        Submit
      </button>
    </FormActionBar>
  );
};

export default FormActions;
