import React from "react";
import { Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import Footer from "./components/Footer";

import Home from "./routes/Home";
import Signup from "./routes/Signup";
import Profile from "./routes/Profile";
import Capture from "./routes/Capture";
import Dashboard from "./routes/Dashboard";
import AdminRecommendations from "./routes/AdminRecommendations";

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 container mx-auto p-4">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/capture" element={<Capture />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/admin" element={<AdminRecommendations />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}
