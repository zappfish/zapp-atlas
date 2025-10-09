import React from 'react';
import Input from '@/ui/Input';
import Select from '@/ui/Select';
import { EXPOSURE_SUBSTANCE } from './explanations';

type Substance = {
  name?: string;
  idType: 'PubChem' | 'CAS' | 'ChEBI' | 'None';
  id?: string;
};

const ID_TYPE_OPTIONS: Array<{ value: Substance['idType']; label: string }> = [
  { value: 'CAS', label: 'CAS' },
  { value: 'PubChem', label: 'PubChem' },
  { value: 'ChEBI', label: 'ChEBI' },
  { value: 'None', label: 'None' }
];

export default function SubstanceFields({
  value,
  onChange
}: {
  value: Substance;
  onChange: (next: Substance) => void;
}) {
  const applyChange = (partial: Partial<Substance>) => {
    onChange({
      ...value,
      ...partial
    });
  };

  // Default dropdown to CAS when value.idType is missing
  const idTypeValue: Substance['idType'] = value.idType ?? 'CAS';

  return (
    <>
      <div className="col-6">
        <Input
          label="Substance"
          placeholder="Substance label"
          tooltip={EXPOSURE_SUBSTANCE}
          value={value.name || ''}
          onChange={(e) => applyChange({ name: e.target.value })}
        />
      </div>
      <div className="col-2">
        <Select
          label="ID Type"
          value={idTypeValue}
          onChange={(e) => applyChange({ idType: e.target.value as Substance['idType'] })}
          options={ID_TYPE_OPTIONS}
        />
      </div>
      <div className="col-4">
        <Input
          label="Identifier"
          placeholder="e.g., 50-00-0"
          value={value.id || ''}
          onChange={(e) => applyChange({ id: e.target.value })}
        />
      </div>
    </>
  );
}
