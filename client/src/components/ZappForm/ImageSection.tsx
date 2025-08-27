import React from 'react';
import FileInput from '@/ui/FileInput';
import FormSection from '@/ui/FormSection';
import type { ZappObservation } from '@/schema';

export default function ImageSection({ setImageFile }: { setImageFile: (file: File | null) => void }) {
  return (
    <div className="row">
      <FormSection title="Image of Observation">
        <div className="col-6">
          <FileInput
            label="Upload image"
            accept="image/jpeg,image/png,image/tiff"
            onChange={(e) => setImageFile((e.target as HTMLInputElement).files?.[0] || null)}
            hint="Accepted: .jpeg, .png, .tiff"
          />
        </div>
        <div className="col-6">
          <div className="field">
            <label>Additional image metadata</label>
            <small className="hint">Scale bar, DPI, magnification, control fish — TODO in later iteration.</small>
          </div>
        </div>
      </FormSection>
    </div>
  );
}

