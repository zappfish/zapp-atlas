import React from 'react';
import { createRoot } from 'react-dom/client';
import ZappAtlasApp from '@/components/ZappAtlasApp';
import './styles.css';

const rootEl = document.getElementById('root');
if (rootEl) {
  const root = createRoot(rootEl);
  root.render(
    <React.StrictMode>
      <ZappAtlasApp />
    </React.StrictMode>
  );
}

