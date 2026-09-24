import { useEffect, useRef, type ReactNode } from "react";
import { DotsIcon } from "./icons";

/**
 * A row's actions, behind a dots toggle. Built on <details>, so open and close
 * come from the element; the effect only closes it on an outside click.
 */
const RowMenu = ({ label, children }: { label: string; children: ReactNode }) => {
  const ref = useRef<HTMLDetailsElement>(null);

  useEffect(() => {
    const onClick = (event: MouseEvent) => {
      const menu = ref.current;
      if (menu?.open && !menu.contains(event.target as Node)) menu.open = false;
    };
    document.addEventListener("click", onClick);
    return () => document.removeEventListener("click", onClick);
  }, []);

  return (
    <details className="sub-menu" ref={ref}>
      <summary className="dash-icon-btn sub-menu__toggle" aria-label={label}>
        <DotsIcon />
      </summary>
      <div className="panel sub-menu__list" role="menu">
        {children}
      </div>
    </details>
  );
};

/** One action. `disabled` covers a destination that does not exist yet. */
export const RowMenuItem = ({
  icon,
  label,
  danger = false,
  disabled = false,
  onClick,
}: {
  icon: ReactNode;
  label: string;
  danger?: boolean;
  disabled?: boolean;
  onClick?: () => void;
}) => (
  <button
    className={`sub-menu__item${danger ? " sub-menu__item--danger" : ""}`}
    type="button"
    role="menuitem"
    disabled={disabled}
    onClick={onClick}
  >
    {icon}
    {label}
  </button>
);

export default RowMenu;
