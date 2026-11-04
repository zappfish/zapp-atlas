import { useId, useState, type FocusEvent, type ReactNode } from "react";
import { InfoIcon } from "@/components/icons";
import {
  InfoTipBox,
  InfoTipBubble,
  InfoTipButton,
} from "@/styles/elements";

/** Disclosure rather than a hover-only tooltip (WCAG 1.4.13, 2.1.1): hover or
 *  focus opens it, click pins it for touch, Escape closes it. */
const InfoTip = ({ label, children }: { label: string; children: ReactNode }) => {
  const [isOver, setIsOver] = useState(false);
  const [isPinned, setIsPinned] = useState(false);
  const bubbleId = useId();
  const isOpen = isOver || isPinned;

  const close = () => {
    setIsOver(false);
    setIsPinned(false);
  };

  const leave = (event: FocusEvent<HTMLSpanElement>) => {
    if (!event.currentTarget.contains(event.relatedTarget)) close();
  };

  return (
    <InfoTipBox
      onMouseEnter={() => setIsOver(true)}
      onMouseLeave={() => setIsOver(false)}
      onFocus={() => setIsOver(true)}
      onBlur={leave}
      onKeyDown={(event) => {
        if (event.key === "Escape" && isOpen) {
          event.stopPropagation();
          close();
        }
      }}
    >
      <InfoTipButton
        type="button"
        aria-label={`About ${label}`}
        aria-expanded={isOpen}
        aria-controls={bubbleId}
        onClick={() => setIsPinned((was) => !was)}
      >
        <InfoIcon />
      </InfoTipButton>
      <InfoTipBubble id={bubbleId} hidden={!isOpen}>
        {children}
      </InfoTipBubble>
    </InfoTipBox>
  );
};

export default InfoTip;
