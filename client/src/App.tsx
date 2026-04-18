import React from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';

import Layout from '@/components/Layout';
import NotFoundPage from '@/pages/NotFoundPage';
import StudyDetailPage from '@/pages/StudyDetailPage';
import StudyListPage from '@/pages/StudyListPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<StudyListPage />} />
          <Route path="studies/:id" element={<StudyDetailPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
