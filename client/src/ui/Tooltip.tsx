import React from 'react';
import * as RadixTooltip from '@radix-ui/react-tooltip';

type Props = {
  text: string;
};

export default function Tooltip({ text }: Props) {
  const tooltipId = React.useId();
  return (
    <RadixTooltip.Provider delayDuration={200} skipDelayDuration={200}>
      <RadixTooltip.Root>
        <RadixTooltip.Trigger asChild>
          <button
            type="button"
            className="tooltip-button"
            aria-label="Show help"
            aria-describedby={tooltipId}
          >
            i
          </button>
        </RadixTooltip.Trigger>
        <RadixTooltip.Portal>
          <RadixTooltip.Content
            id={tooltipId}
            className="tooltip-content"
            sideOffset={6}
          >
            {text}
            <RadixTooltip.Arrow className="tooltip-arrow" />
          </RadixTooltip.Content>
        </RadixTooltip.Portal>
      </RadixTooltip.Root>
    </RadixTooltip.Provider>
  );
}
