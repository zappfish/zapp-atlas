import React from 'react';
import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <section className="not-found">
      <h1>Not found</h1>
      <p>
        The page you were looking for doesn't exist.{' '}
        <Link to="/">Back to studies</Link>.
      </p>
    </section>
  );
}
