import {
  ActionsHint,
  ActionsPrompt,
  ActionsTitle,
  FormActionBar,
} from "@/styles/elements";

/** Sticky: the form is long, and saving should not mean scrolling to its end. */
const FormActions = ({
  title,
  hint,
  label,
  isPending,
}: {
  title: string;
  /** What happened last, or what saving does. */
  hint: string;
  /** The button's own words. */
  label: string;
  isPending: boolean;
}) => (
  <FormActionBar>
    <ActionsPrompt>
      <ActionsTitle>{title}</ActionsTitle>
      <ActionsHint role="status">{hint}</ActionsHint>
    </ActionsPrompt>
    <button className="btn btn--primary" type="submit" disabled={isPending}>
      {isPending ? "Saving…" : label}
    </button>
  </FormActionBar>
);

export default FormActions;
