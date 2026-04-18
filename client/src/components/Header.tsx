import React from 'react';
import { NavLink } from 'react-router-dom';

export default function Header() {
  return (
    <header className="app-header">
      <NavLink to="/" className="brand">
        ZAPP Atlas
      </NavLink>
      <nav>
        <ul>
          <li>
            <NavLink to="/" end>
              Studies
            </NavLink>
          </li>
        </ul>
      </nav>
    </header>
  );
}
