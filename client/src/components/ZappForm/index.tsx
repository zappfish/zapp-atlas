import React from 'react';
import { ZappObservationSchema, type ZappObservation } from '@/schema';
import ProvenanceSection from './ProvenanceSection';
import ImageSection from './ImageSection';
import FishInfoSection from './FishInfoSection';
import RearingSection from './RearingSection';
import ExposureSection from './ExposureSection';
import PhenotypeSection from './PhenotypeSection';

type Props = { onChange: (data: ZappObservation) => void };

function emptyObservation(): ZappObservation {
  return {
    provenance: {
      annotator_orcid: '',
      source: { type: undefined, value: undefined }
    },
    image: { file: null },
    fish: { strain_background: '' },
    rearing: { standard: true, non_standard_notes: '' },
    exposure: {
      substance: { name: '', idType: 'None', id: '' },
      concentration: { value: null, unit: 'uM' },
      route: 'water',
      type: null,
      pattern: null,
      start_stage: { value: null, unit: 'hpf' },
      end_stage: { value: null, unit: 'hpf' },
      repeated: {
        duration_per_exposure_hours: null,
        frequency_count: null,
        interval_hours: null
      }
    },
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

  return (
    <form className="grid" onSubmit={(e) => e.preventDefault()}>
      <ImageSection setImageFile={setImageFile} previewSrc={imagePreview} fileMeta={data.image.file} />
      <ProvenanceSection data={data} update={update} />
      <FishInfoSection data={data} update={update} />
      <RearingSection data={data} update={update} />
      <ExposureSection data={data} update={update} />
      <PhenotypeSection data={data} update={update} addPhenotype={addPhenotype} removePhenotype={removePhenotype} />
    </form>
  );
}
