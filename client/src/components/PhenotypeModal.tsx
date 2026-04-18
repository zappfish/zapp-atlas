import React from 'react';

import PhenotypePicker from '@/components/ZappForm/PhenotypePicker';
import type { PhenotypeTerm } from '@/types';

interface Props {
  open: boolean;
  onClose: () => void;
  onSelect: (term: PhenotypeTerm) => void;
}

/** Convert a full OBO IRI to its CURIE form (e.g. ZP_0001234 → ZP:0001234). */
function iriToCurie(iri: string): string {
  const tail = iri.split('/').pop() ?? iri;
  const us = tail.indexOf('_');
  if (us === -1) return tail;
  return `${tail.slice(0, us)}:${tail.slice(us + 1)}`;
}

export default function PhenotypeModal({ open, onClose, onSelect }: Props) {
  if (!open) return null;

  return (
    <div className="phenotype-modal-overlay" role="dialog" aria-label="Pick a phenotype">
      <div className="phenotype-modal">
        <div className="phenotype-modal-header">Pick a phenotype</div>
        <div className="phenotype-modal-body">
          <PhenotypePicker
            onSelectNode={(node) => {
              onSelect({
                term_uri: iriToCurie(node.uri),
                term_label: node.label ?? null,
              });
              onClose();
            }}
          />
        </div>
        <div className="phenotype-modal-footer">
          <button type="button" onClick={onClose}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
