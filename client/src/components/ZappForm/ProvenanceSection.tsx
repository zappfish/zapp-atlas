import React from 'react';
import Input from '@/ui/Input';
import Select from '@/ui/Select';
import FormSection from '@/ui/FormSection';
import TextArea from '@/ui/TextArea';
import type { ZappObservation } from '@/schema';
import { SOURCE_TYPE_OPTIONS } from './constants';
import { PROVENANCE_ORCID, PROVENANCE_SOURCE_TYPE, PROVENANCE_SOURCE_VALUE } from './explanations';

export default function ProvenanceSection({ data, update }: { data: ZappObservation; update: (u: (d: ZappObservation) => ZappObservation) => void }) {
  const [showNotes, setShowNotes] = React.useState(false);
  return (
    <div className="row">
      <FormSection title="Provenance of Data">
        <div className="col-6">
          <Input
            label="Annotator/Submitter ORCID"
            placeholder="0000-0000-0000-0000"
            value={data.provenance.annotator_orcid || ''}
            tooltip={PROVENANCE_ORCID}
            onChange={(e) =>
              update((d) => ({
                ...d,
                provenance: {
                  ...d.provenance,
                  annotator_orcid: e.target.value
                }
              }))
            }
            hint="Enter your ORCID iD (link to create one will be added)."
          />
        </div>
        <div className="col-6"></div>
        <div className="col-4">
          <Select
            label="Source of the information"
            value={data.provenance.source.type || ''}
            options={SOURCE_TYPE_OPTIONS}
            tooltip={PROVENANCE_SOURCE_TYPE}
            onChange={(e) =>
              update((d) => ({
                ...d,
                provenance: {
                  ...d.provenance,
                  source: {
                    ...d.provenance.source,
                    type: (e.target as HTMLSelectElement).value as ZappObservation['provenance']['source']['type'],
                    value: ''
                  }
                }
              }))
            }
          />
        </div>
        <div className="col-8">
          <Input
            label="Source value"
            placeholder="PMID number, DOI url, link, etc."
            value={data.provenance.source.value || ''}
            tooltip={PROVENANCE_SOURCE_VALUE}
            onChange={(e) =>
              update((d) => ({
                ...d,
                provenance: {
                  ...d.provenance,
                  source: { ...d.provenance.source, value: e.target.value }
                }
              }))
            }
          />
        </div>
        <div className="col-12">
          <button type="button" onClick={() => setShowNotes((s) => !s)}>
            {showNotes ? 'Hide notes' : 'Add notes'}
          </button>
        </div>
        {showNotes && (
          <div className="col-12">
            <TextArea
              label="Additional notes"
              placeholder="Additional notes not captured by the fields in this section"
              value={data.provenance.additional_notes || ''}
              onChange={(e) =>
                update((d) => ({
                  ...d,
                  provenance: { ...d.provenance, additional_notes: (e.target as HTMLTextAreaElement).value }
                }))
              }
            />
          </div>
        )}
      </FormSection>
    </div>
  );
}
