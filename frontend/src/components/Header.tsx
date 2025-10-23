import React from "react";
import { Link } from "react-router-dom";

export default function Header() {
  return (
    <header className="p-4 bg-indigo-600 text-white">
      <div className="container mx-auto flex justify-between">
        <h1 className="text-lg font-semibold">Haski</h1>
        <nav>
          <Link to="/" className="mr-4">
            Home
          </Link>
          <Link to="/capture" className="mr-4">
            Capture
          </Link>
          <Link to="/dashboard">Dashboard</Link>
        </nav>
      </div>
    </header>
  );
}
