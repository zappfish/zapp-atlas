import React, { useState } from 'react';
import ZappForm from '@/components/ZappForm';
import type { ZappObservation } from '@/schema';

export default function ZappAtlasApp() {
  const [data, setData] = useState<ZappObservation | null>(null);
  const [showDebug, setShowDebug] = useState(false);

  return (
    <div className="container">
      <h1>ZAPP Atlas: Observation Form</h1>
      <ZappForm onChange={setData} />

      <button type="button" onClick={() => setShowDebug((s) => !s)}>
        {showDebug ? 'Hide debug data' : 'Show debug data'}
      </button>
      {showDebug && (
        <>
          <h2>Debug Data</h2>
          <div className="json-preview">
            {data ? JSON.stringify(data, null, 2) : 'Interact with the form to see data here.'}
          </div>
        </>
      )}
    </div>
  );
}
