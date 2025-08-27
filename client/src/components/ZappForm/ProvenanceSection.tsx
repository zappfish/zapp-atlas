import React from 'react';
import Input from '@/ui/Input';
import Select from '@/ui/Select';
import FormSection from '@/ui/FormSection';
import type { ZappObservation } from '@/schema';
import { SOURCE_TYPE_OPTIONS } from './constants';

export default function ProvenanceSection({ data, update }: { data: ZappObservation; update: (u: (d: ZappObservation) => ZappObservation) => void }) {
  return (
    <div className="row">
      <FormSection title="Provenance of Data">
        <div className="col-6">
          <Input
            label="Annotator/Submitter ORCID"
            placeholder="0000-0000-0000-0000"
            value={data.provenance.annotator_orcid || ''}
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
            onChange={(e) =>
              update((d) => ({
                ...d,
                provenance: {
                  ...d.provenance,
                  source: {
                    ...d.provenance.source,
                    type: (e.target as HTMLSelectElement).value as any,
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
      </FormSection>
    </div>
  );
}
