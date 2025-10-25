import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/useAuth";

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isAvatarOpen, setIsAvatarOpen] = useState(false);

  const token = localStorage.getItem("authToken");

  const handleLogout = () => {
    logout();
    navigate("/");
    setIsMenuOpen(false);
    setIsAvatarOpen(false);
  };

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const toggleAvatarDropdown = () => {
    setIsAvatarOpen(!isAvatarOpen);
  };

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  const navLinkClass = (path: string) => {
    const baseClass =
      "px-3 sm:px-4 py-2 rounded-lg text-sm sm:text-base font-semibold transition duration-200";
    const activeClass = isActive(path)
      ? "bg-white/20 dark:bg-white/10 text-white"
      : "hover:bg-white/10 dark:hover:bg-white/10 text-white";
    return `${baseClass} ${activeClass}`;
  };

  const mobileNavLinkClass = (path: string) => {
    const baseClass =
      "block px-3 py-2 rounded-md text-base font-medium transition";
    const activeClass = isActive(path)
      ? "bg-white/20 dark:bg-white/10 text-white"
      : "hover:bg-white/10 dark:hover:bg-white/10 text-white";
    return `${baseClass} ${activeClass}`;
  };

  return (
    <nav className="sticky top-0 z-50 backdrop-blur-md bg-gradient-to-r from-blue-600/95 to-cyan-600/95 dark:from-blue-900/95 dark:to-cyan-900/95 shadow-md border-b border-white/10">
      <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 w-full">
        <div className="flex justify-between items-center h-16 sm:h-20">
          {/* Brand Logo */}
          <Link to="/" className="flex items-center space-x-2 flex-shrink-0">
            <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg bg-white/20 dark:bg-white/10 flex items-center justify-center">
              <span className="text-lg sm:text-xl font-black text-white">
                H
              </span>
            </div>
            <div className="flex flex-col leading-none">
              <span className="text-xl sm:text-2xl font-black text-white">
                Haski
              </span>
              <span className="text-xs font-semibold text-white/70">
                AI Analysis
              </span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex items-center space-x-1">
            <Link to="/" className={navLinkClass("/")}>
              Home
            </Link>

            {isAuthenticated && (
              <>
                <Link to="/analyze" className={navLinkClass("/analyze")}>
                  Analyze
                </Link>
                <Link to="/dashboard" className={navLinkClass("/dashboard")}>
                  Dashboard
                </Link>
              </>
            )}
          </div>

          {/* Desktop Right Section */}
          <div className="hidden md:flex items-center space-x-3">
            {token ? (
              <>
                {/* Avatar Dropdown */}
                <div className="relative">
                  <button
                    onClick={toggleAvatarDropdown}
                    className="flex items-center space-x-2 hover:bg-white/10 px-2 py-1 rounded-lg transition"
                  >
                    <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center text-sm font-bold text-white hover:bg-white/30 transition">
                      {user?.username?.[0]?.toUpperCase() ||
                        user?.email?.[0]?.toUpperCase() ||
                        "U"}
                    </div>
                    <svg
                      className={`w-4 h-4 text-white transition transform ${
                        isAvatarOpen ? "rotate-180" : ""
                      }`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 14l-7 7m0 0l-7-7m7 7V3"
                      />
                    </svg>
                  </button>

                  {/* Dropdown Menu */}
                  {isAvatarOpen && (
                    <div className="absolute right-0 mt-2 w-48 rounded-lg bg-white dark:bg-slate-800 shadow-lg border border-gray-200 dark:border-slate-700 overflow-hidden">
                      <div className="px-4 py-3 border-b border-gray-200 dark:border-slate-700">
                        <p className="text-sm font-semibold text-slate-900 dark:text-white truncate">
                          {user?.username || user?.email || "User"}
                        </p>
                        <p className="text-xs text-slate-600 dark:text-slate-400 truncate">
                          {user?.email}
                        </p>
                      </div>
                      <Link
                        to="/profile"
                        className="block px-4 py-2 text-sm text-slate-700 dark:text-slate-200 hover:bg-gray-100 dark:hover:bg-slate-700 transition"
                        onClick={() => setIsAvatarOpen(false)}
                      >
                        👤 Profile
                      </Link>
                      <Link
                        to="/settings"
                        className="block px-4 py-2 text-sm text-slate-700 dark:text-slate-200 hover:bg-gray-100 dark:hover:bg-slate-700 transition"
                        onClick={() => setIsAvatarOpen(false)}
                      >
                        ⚙️ Settings
                      </Link>
                      <button
                        onClick={handleLogout}
                        className="w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition border-t border-gray-200 dark:border-slate-700"
                      >
                        🚪 Logout
                      </button>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="px-4 py-2 text-sm sm:text-base font-semibold text-white hover:bg-white/10 rounded-lg transition"
                >
                  Login
                </Link>
                <Link
                  to="/signup"
                  className="px-4 sm:px-6 py-2 text-sm sm:text-base font-semibold bg-white text-blue-600 hover:bg-blue-50 dark:bg-white dark:text-blue-700 dark:hover:bg-gray-100 rounded-lg transition"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={toggleMenu}
            className="md:hidden inline-flex items-center justify-center p-2 rounded-lg hover:bg-white/10 transition"
          >
            <svg
              className="w-6 h-6 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {isMenuOpen ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden pb-4 space-y-1 border-t border-white/10">
            <Link
              to="/"
              className={mobileNavLinkClass("/")}
              onClick={() => setIsMenuOpen(false)}
            >
              Home
            </Link>

            {isAuthenticated && (
              <>
                <Link
                  to="/analyze"
                  className={mobileNavLinkClass("/analyze")}
                  onClick={() => setIsMenuOpen(false)}
                >
                  Analyze
                </Link>
                <Link
                  to="/dashboard"
                  className={mobileNavLinkClass("/dashboard")}
                  onClick={() => setIsMenuOpen(false)}
                >
                  Dashboard
                </Link>
              </>
            )}

            <div className="border-t border-white/10 pt-2 mt-2">
              {token ? (
                <>
                  <Link
                    to="/profile"
                    className="block px-3 py-2 rounded-md text-base font-medium text-white hover:bg-white/10 transition"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    👤 Profile
                  </Link>
                  <Link
                    to="/settings"
                    className="block px-3 py-2 rounded-md text-base font-medium text-white hover:bg-white/10 transition"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    ⚙️ Settings
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="w-full text-left px-3 py-2 rounded-md text-base font-medium text-red-300 hover:bg-red-900/20 transition"
                  >
                    🚪 Logout
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="block px-3 py-2 rounded-md text-base font-medium text-white hover:bg-white/10 transition"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Login
                  </Link>
                  <Link
                    to="/signup"
                    className="block px-3 py-2 rounded-md text-base font-medium bg-white text-blue-600 hover:bg-blue-50 dark:bg-slate-200 dark:text-blue-700 dark:hover:bg-slate-300 font-semibold rounded-lg transition"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Sign Up
                  </Link>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
