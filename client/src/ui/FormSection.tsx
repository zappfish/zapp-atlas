import React from 'react';

export default function FormSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="card">
      <h3 className="section-title">{title}</h3>
      <div className="grid">{children}</div>
    </section>
  );
}

