import React from 'react';
import { Outlet } from 'react-router-dom';
import { Rail } from './Rail';
import { Topbar } from './Topbar';

export function Layout() {
  return (
    <div className="app">
      <Rail />
      <div className="viewport">
        <Topbar />
        <main id="main">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
