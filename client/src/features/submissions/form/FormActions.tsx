import {
  ActionsHint,
  ActionsPrompt,
  ActionsTitle,
  FormActionBar,
} from "@/styles/elements";

/**
 * Stays in view as the form scrolls, so saving a draft does not mean finding
 * the end of it first. Submitting logs what the form collected to the console;
 * there is nowhere to send it yet, and saving a draft does nothing at all.
 */
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
