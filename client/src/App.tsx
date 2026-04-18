import React from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';

import Layout from '@/components/Layout';
import ExperimentFormPage from '@/pages/ExperimentFormPage';
import NotFoundPage from '@/pages/NotFoundPage';
import StudyDetailPage from '@/pages/StudyDetailPage';
import StudyFormPage from '@/pages/StudyFormPage';
import StudyListPage from '@/pages/StudyListPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<StudyListPage />} />
          <Route path="studies/new" element={<StudyFormPage />} />
          <Route path="studies/:id" element={<StudyDetailPage />} />
          <Route path="studies/:id/edit" element={<StudyFormPage />} />
          <Route
            path="studies/:studyId/experiments/new"
            element={<ExperimentFormPage />}
          />
          <Route path="experiments/:id/edit" element={<ExperimentFormPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
