import { FormActionBar } from "@/styles/elements";

/**
 * Stays in view as the form scrolls, so saving a draft does not mean finding
 * the end of it first. Submitting shows what the form collected; there is
 * nowhere to send it yet, and saving a draft does nothing at all.
 */
const FormActions = () => (
  <FormActionBar>
    <button className="btn btn--secondary" type="button">
      Save draft
    </button>
    <button className="btn btn--primary" type="submit">
      Submit to atlas
    </button>
  </FormActionBar>
);

export default FormActions;
