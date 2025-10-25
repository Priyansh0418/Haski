import { Routes, Route, Navigate, Outlet } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { ToastProvider } from "./context/ToastContext";
import Navbar from "./components/Navbar";
import ToastContainer from "./components/ToastContainer";
import ProtectedRoute from "./components/ProtectedRoute";
import Home from "./routes/Home";
import Login from "./routes/Login";
import Signup from "./routes/Signup";
import Dashboard from "./routes/Dashboard";
import Analyze from "./routes/Analyze";
import Capture from "./routes/Capture";
import Recommendations from "./routes/Recommendations";
import Settings from "./routes/Settings";
import Profile from "./routes/Profile";
import AdminRecommendations from "./routes/AdminRecommendations";

/**
 * Main App Layout Shell
 * Features:
 * - Sticky top navigation bar with responsive design
 * - Full-width content area with max-w-7xl container for readability
 * - Subtle gradient background (light mode)
 * - Dark mode support via prefers-color-scheme media query
 * - Global toast notification container
 * - Protected routes with auth checks
 */
function AppShell() {
  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-slate-100 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      {/* Sticky Navigation */}
      <Navbar />

      {/* Main Content Area */}
      <main className="flex-1 w-full">
        <Outlet />
      </main>

      {/* Global Toast Container */}
      <ToastContainer />
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <Routes>
          {/* Public Layout Routes */}
          <Route element={<AppShell />}>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />

            {/* Protected Routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/analyze"
              element={
                <ProtectedRoute>
                  <Analyze />
                </ProtectedRoute>
              }
            />
            <Route
              path="/capture"
              element={
                <ProtectedRoute>
                  <Capture />
                </ProtectedRoute>
              }
            />
            <Route
              path="/recommendations"
              element={
                <ProtectedRoute>
                  <Recommendations />
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <Settings />
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/recommendations"
              element={
                <ProtectedRoute>
                  <AdminRecommendations />
                </ProtectedRoute>
              }
            />
          </Route>

          {/* Catch-all redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;
