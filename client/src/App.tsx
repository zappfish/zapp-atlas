import React from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';

import Layout from '@/components/Layout';
import HomePage from '@/pages/HomePage';
import NotFoundPage from '@/pages/NotFoundPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
