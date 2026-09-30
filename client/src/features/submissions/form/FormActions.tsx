import { FormActionBar } from "@/styles/elements";

/**
 * Stays in view as the form scrolls, so saving a draft does not mean finding
 * the end of it first. Neither does anything until there is an endpoint to
 * save to.
 */
const FormActions = () => (
  <FormActionBar>
    <button className="btn btn--secondary" type="button">
      Save draft
    </button>
    <button className="btn btn--primary" type="button">
      Submit to atlas
    </button>
  </FormActionBar>
);

export default FormActions;
