import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/useAuth";

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isAvatarOpen, setIsAvatarOpen] = useState(false);

  const token = localStorage.getItem("skinhairai_token");

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

  // Determine if a nav link is active
  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="sticky top-0 z-50 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 w-full">
        <div className="flex justify-between items-center h-16">
          {/* Brand Logo */}
          <Link to="/" className="flex items-center space-x-2 flex-shrink-0">
            <span className="text-2xl font-bold text-primary dark:text-primary">
              Haski
            </span>
          </Link>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex items-center space-x-1">
            <Link
              to="/"
              className={`px-3 py-2 text-sm font-semibold transition-colors border-b-2 ${
                isActive("/")
                  ? "text-primary border-primary"
                  : "text-slate-600 dark:text-slate-400 border-transparent hover:text-primary dark:hover:text-primary"
              }`}
            >
              Home
            </Link>
            {isAuthenticated && (
              <>
                <Link
                  to="/analyze"
                  className={`px-3 py-2 text-sm font-semibold transition-colors border-b-2 ${
                    isActive("/analyze")
                      ? "text-primary border-primary"
                      : "text-slate-600 dark:text-slate-400 border-transparent hover:text-primary dark:hover:text-primary"
                  }`}
                >
                  Analyze
                </Link>
                <Link
                  to="/dashboard"
                  className={`px-3 py-2 text-sm font-semibold transition-colors border-b-2 ${
                    isActive("/dashboard")
                      ? "text-primary border-primary"
                      : "text-slate-600 dark:text-slate-400 border-transparent hover:text-primary dark:hover:text-primary"
                  }`}
                >
                  Dashboard
                </Link>
              </>
            )}
          </div>

          {/* Desktop Right Section */}
          <div className="hidden md:flex items-center ml-8 space-x-4">
            {token ? (
              <>
                {/* Avatar Dropdown */}
                <div className="relative">
                  <button
                    onClick={toggleAvatarDropdown}
                    className="flex items-center space-x-2 hover:bg-slate-100 dark:hover:bg-slate-800 px-3 py-2 rounded-lg transition"
                    aria-label="User menu"
                    aria-expanded={isAvatarOpen}
                  >
                    <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-xs font-bold text-white">
                      {user?.username?.[0]?.toUpperCase() ||
                        user?.email?.[0]?.toUpperCase() ||
                        "U"}
                    </div>
                  </button>

                  {/* Dropdown Menu */}
                  {isAvatarOpen && (
                    <div className="absolute right-0 mt-2 w-48 rounded-lg bg-white dark:bg-slate-800 shadow-lg border border-slate-200 dark:border-slate-700 overflow-hidden">
                      <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-700">
                        <p className="text-sm font-semibold text-slate-900 dark:text-white truncate">
                          {user?.username || user?.email || "User"}
                        </p>
                        <p className="text-xs text-slate-600 dark:text-slate-400 truncate">
                          {user?.email}
                        </p>
                      </div>
                      <Link
                        to="/profile"
                        className="block px-4 py-2 text-sm text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 transition"
                        onClick={() => setIsAvatarOpen(false)}
                      >
                        👤 Profile
                      </Link>
                      <Link
                        to="/settings"
                        className="block px-4 py-2 text-sm text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 transition"
                        onClick={() => setIsAvatarOpen(false)}
                      >
                        ⚙️ Settings
                      </Link>
                      <button
                        onClick={handleLogout}
                        className="w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition border-t border-slate-200 dark:border-slate-700"
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
                  className="px-4 py-2 text-slate-700 dark:text-slate-300 hover:text-primary dark:hover:text-primary font-semibold transition"
                >
                  Login
                </Link>
                <Link
                  to="/signup"
                  className="px-6 py-2 bg-primary hover:bg-primary-600 text-white rounded-lg font-semibold transition"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={toggleMenu}
            className="md:hidden inline-flex items-center justify-center p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition"
            aria-label="Menu"
            aria-expanded={isMenuOpen}
          >
            <svg
              className="w-6 h-6 text-slate-900 dark:text-white"
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
          <div className="md:hidden pb-4 space-y-1 border-t border-slate-200 dark:border-slate-700">
            <Link
              to="/"
              className={`block px-3 py-2 rounded-md text-base font-medium transition ${
                isActive("/")
                  ? "bg-primary/10 text-primary"
                  : "text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
              }`}
              onClick={() => setIsMenuOpen(false)}
            >
              Home
            </Link>

            {isAuthenticated && (
              <>
                <Link
                  to="/analyze"
                  className={`block px-3 py-2 rounded-md text-base font-medium transition ${
                    isActive("/analyze")
                      ? "bg-primary/10 text-primary"
                      : "text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
                  }`}
                  onClick={() => setIsMenuOpen(false)}
                >
                  Analyze
                </Link>
                <Link
                  to="/dashboard"
                  className={`block px-3 py-2 rounded-md text-base font-medium transition ${
                    isActive("/dashboard")
                      ? "bg-primary/10 text-primary"
                      : "text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
                  }`}
                  onClick={() => setIsMenuOpen(false)}
                >
                  Dashboard
                </Link>
              </>
            )}

            <div className="border-t border-slate-200 dark:border-slate-700 pt-2 mt-2">
              {token ? (
                <>
                  <Link
                    to="/profile"
                    className="block px-3 py-2 rounded-md text-base font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    👤 Profile
                  </Link>
                  <Link
                    to="/settings"
                    className="block px-3 py-2 rounded-md text-base font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    ⚙️ Settings
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="w-full text-left px-3 py-2 rounded-md text-base font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition"
                  >
                    🚪 Logout
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="block px-3 py-2 rounded-md text-base font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Login
                  </Link>
                  <Link
                    to="/signup"
                    className="block px-3 py-2 rounded-md text-base font-medium bg-primary text-white hover:bg-primary-600 font-semibold rounded-lg transition mt-1"
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
