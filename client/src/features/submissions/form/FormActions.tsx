import {
  ActionsHint,
  ActionsPrompt,
  ActionsTitle,
  FormActionBar,
} from "@/styles/elements";

/** Sticky: the form is long. No endpoint yet, so Submit only logs. */
const FormActions = () => (
  <FormActionBar>
    <ActionsPrompt>
      <ActionsTitle>Ready to submit?</ActionsTitle>
      <ActionsHint>Complete all required fields to continue.</ActionsHint>
    </ActionsPrompt>
    <button className="btn btn--secondary" type="button">
      Save draft
    </button>
    <button className="btn btn--primary" type="submit">
      Review submission
    </button>
  </FormActionBar>
);

export default FormActions;
