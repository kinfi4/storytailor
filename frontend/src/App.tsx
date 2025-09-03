import React from 'react';
import { Link, Outlet, NavLink } from 'react-router-dom';

export default function App(): JSX.Element {
  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand">
            <span className="brand-badge" />
            <NavLink to="/" className="title-link" end>
              Story Tailer
            </NavLink>
          </div>
          <nav className="nav">
            <NavLink to="/" end className={({ isActive }) => isActive ? 'active' : ''}>Stories</NavLink>
            <NavLink to="/create" className={({ isActive }) => isActive ? 'active' : ''}>Create</NavLink>
          </nav>
        </div>
      </header>
      <main className="container">
        <Outlet />
      </main>
    </div>
  );
}
