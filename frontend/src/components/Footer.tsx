import React from "react";

export default function Footer() {
  return (
    <footer className="p-4 bg-gray-100 text-center text-sm">
      © {new Date().getFullYear()} Haski — Privacy-first skin & hair helper
    </footer>
  );
}
