import { useEffect, useRef, type ReactNode } from "react";
import { DotsIcon } from "./icons";
import {
  RowMenuAction,
  RowMenuList,
  RowMenuToggle,
} from "@/styles/elements";

/** Built on <details>, so it opens itself; the effect only closes on outside click. */
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
      <RowMenuToggle aria-label={label}>
        <DotsIcon />
      </RowMenuToggle>
      <RowMenuList role="menu">{children}</RowMenuList>
    </details>
  );
};

/** `disabled` covers a destination that does not exist yet. */
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
  <RowMenuAction
    isDanger={danger}
    type="button"
    role="menuitem"
    disabled={disabled}
    onClick={onClick}
  >
    {icon}
    {label}
  </RowMenuAction>
);

export default RowMenu;
