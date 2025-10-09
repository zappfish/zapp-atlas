import React from 'react';
import { ZappObservationSchema, type ZappObservation } from '@/schema';
import ProvenanceSection from './ProvenanceSection';
import ImageSection from './ImageSection';
import FishInfoSection from './FishInfoSection';
import RearingSection from './RearingSection';
import ExposureSection from './ExposureSection';
import PhenotypeSection from './PhenotypeSection';

type Props = { onChange: (data: ZappObservation) => void };

type ExposureEvent = ZappObservation['exposures'][number];

function emptyExposureEvent(): ExposureEvent {
  return {
    textual_description: null,
    substance: { name: '', idType: 'CAS', id: '' },
    concentration: { value: null, unit: 'uM' },
    route: 'water',
    type: null,
    pattern: null,
    duration: { value: null, unit: null },
    start_stage: { value: null, unit: 'hpf' },
    end_stage: { value: null, unit: 'hpf' },
    repeated: {
      count: null,
      duration_per: { value: null, unit: null },
      interval_between: { value: null, unit: null },
      total_length: { value: null, unit: null },
    },
    additional_notes: ''
  };
}

function emptyObservation(): ZappObservation {
  return {
    provenance: {
      annotator_name: '',
      annotator_orcid: '',
      source: { type: undefined, value: undefined }
    },
    image: { file: null },
    fish: { strain_background: '' },
    rearing: { standard: true, non_standard_notes: '' },
    exposures: [emptyExposureEvent()],
    phenotype: {
      observation_stage: { value: null, unit: 'hpf' },
      items: [
        { termId: '', termLabel: '', prevalencePercent: null, severity: null }
      ]
    }
  };
}

export default function ZappForm({ onChange }: Props) {
  const [data, setData] = React.useState<ZappObservation>(() => emptyObservation());
  const [, setErrors] = React.useState<Record<string, string>>({});
  const [imagePreview, setImagePreview] = React.useState<string | null>(null);
  const prevObjectUrlRef = React.useRef<string | null>(null);
  const [imageFile, setImageFileState] = React.useState<File | null>(null);
  const [submitting, setSubmitting] = React.useState(false);
  const [submitResult, setSubmitResult] = React.useState<string | null>(null);

  const update = (updater: (d: ZappObservation) => ZappObservation) => {
    const next = updater(data);
    const parsed = ZappObservationSchema.safeParse(next);
    if (!parsed.success) {
      const errs: Record<string, string> = {};
      for (const issue of parsed.error.issues) errs[issue.path.join('.')] = issue.message;
      setErrors(errs);
    } else {
      setErrors({});
    }
    setData(next);
    onChange(next);
  };

  const setImageFile = (file: File | null) => {
    update((d) => ({
      ...d,
      image: {
        ...d.image,
        file: file ? { name: file.name, type: file.type, size: file.size } : null
      }
    }));
    setImageFileState(file);
    // Manage preview URL lifecycle
    if (prevObjectUrlRef.current) {
      URL.revokeObjectURL(prevObjectUrlRef.current);
      prevObjectUrlRef.current = null;
    }
    if (file) {
      const url = URL.createObjectURL(file);
      prevObjectUrlRef.current = url;
      setImagePreview(url);
    } else {
      setImagePreview(null);
    }
  };

  const addPhenotype = () =>
    update((d) => ({
      ...d,
      phenotype: {
        ...d.phenotype,
        items: [
          ...d.phenotype.items,
          { termId: '', termLabel: '', prevalencePercent: null, severity: null }
        ]
      }
    }));

  const removePhenotype = (idx: number) =>
    update((d) => {
      const remaining = d.phenotype.items.filter((_, i) => i !== idx);
      return {
        ...d,
        phenotype: {
          ...d.phenotype,
          items:
            remaining.length > 0
              ? remaining
              : [{ termId: '', termLabel: '', prevalencePercent: null, severity: null }]
        }
      };
    });

  React.useEffect(() => {
    return () => {
      if (prevObjectUrlRef.current) {
        URL.revokeObjectURL(prevObjectUrlRef.current);
      }
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setSubmitResult(null);
    try {
      const formData = new FormData();
      formData.append(
        'data',
        new Blob([JSON.stringify(data)], { type: 'application/json' }),
        'observation.json'
      );
      if (imageFile) {
        formData.append('image', imageFile, imageFile.name);
      }
      const res = await fetch('/obervation', { method: 'POST', body: formData });
      const text = await res.text();
      setSubmitResult(text || `Submitted. Status ${res.status}`);
    } catch (err) {
      setSubmitResult(err instanceof Error ? err.message : String(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form className="grid" onSubmit={handleSubmit}>
      <ImageSection
        setImageFile={setImageFile}
        previewSrc={imagePreview}
        fileMeta={data.image.file}
        imageNotes={data.image.additional_notes || ''}
        setImageNotes={(val: string) =>
          update((d) => ({
            ...d,
            image: { ...d.image, additional_notes: val }
          }))
        }
      />
      <ProvenanceSection data={data} update={update} />
      <FishInfoSection data={data} update={update} />
      <RearingSection data={data} update={update} />
      {data.exposures.map((ev, idx) => (
        <div key={idx} className="row">
          <div className="col-12">
            <h4>Exposure Event {idx + 1}</h4>
          </div>
          <ExposureSection
            exposure={ev}
            update={(fn) =>
              update((d) => ({
                ...d,
                exposures: d.exposures.map((e, i) => (i === idx ? fn(e) : e))
              }))
            }
          />
          <div className="col-12" style={{ display: 'flex', justifyContent: 'flex-end' }}>
            {data.exposures.length > 1 && (
              <button
                type="button"
                onClick={() =>
                  update((d) => ({
                    ...d,
                    exposures: d.exposures.filter((__, i) => i !== idx)
                  }))
                }
              >
                Remove this exposure
              </button>
            )}
          </div>
        </div>
      ))}
      <div className="row">
        <div className="col-12">
          <button
            type="button"
            onClick={() =>
              update((d) => ({ ...d, exposures: [...d.exposures, emptyExposureEvent()] }))
            }
          >
            + Add exposure
          </button>
        </div>
      </div>
      <PhenotypeSection data={data} update={update} addPhenotype={addPhenotype} removePhenotype={removePhenotype} />
      <div className="row">
        <div className="col-12">
          <button type="submit" disabled={submitting}>{submitting ? 'Submitting...' : 'Submit'}</button>
          {submitResult && <small className="hint" style={{ marginLeft: 12 }}>{submitResult}</small>}
        </div>
      </div>
    </form>
  );
}
