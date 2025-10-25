import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/useAuth";

export default function Navbar() {
  const { user, logout } = useAuth();
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
    <nav className="sticky top-0 z-50 bg-white dark:bg-[#101922] border-b border-[#233648]">
      <div className="px-4 sm:px-10 md:px-20 lg:px-40">
        <div className="max-w-[960px] mx-auto flex justify-between items-center h-16">
          {/* Brand Logo */}
          <Link to="/" className="flex items-center space-x-2 flex-shrink-0">
            <div className="size-6 text-[#137fec]">
              <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                <g clipPath="url(#clip0_6_319)">
                  <path
                    d="M8.57829 8.57829C5.52816 11.6284 3.451 15.5145 2.60947 19.7452C1.76794 23.9758 2.19984 28.361 3.85056 32.3462C5.50128 36.3314 8.29667 39.7376 11.8832 42.134C15.4698 44.5305 19.6865 45.8096 24 45.8096C28.3135 45.8096 32.5302 44.5305 36.1168 42.134C39.7033 39.7375 42.4987 36.3314 44.1494 32.3462C45.8002 28.361 46.2321 23.9758 45.3905 19.7452C44.549 15.5145 42.4718 11.6284 39.4217 8.57829L24 24L8.57829 8.57829Z"
                    fill="currentColor"
                  ></path>
                </g>
                <defs>
                  <clipPath id="clip0_6_319">
                    <rect fill="white" height="48" width="48"></rect>
                  </clipPath>
                </defs>
              </svg>
            </div>
            <h2 className="text-white dark:text-white text-lg font-bold leading-tight tracking-[-0.015em]">
              Haski
            </h2>
          </Link>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex items-center flex-1 justify-center space-x-9">
            <Link
              to="/"
              className={`text-sm font-medium leading-normal transition-colors hover:text-[#137fec] ${
                isActive("/")
                  ? "text-slate-900 dark:text-white border-b-2 border-[#137fec]"
                  : "text-slate-600 dark:text-white border-b-2 border-transparent"
              }`}
            >
              Home
            </Link>
            <Link
              to="/analyze"
              className={`text-sm font-medium leading-normal transition-colors hover:text-[#137fec] ${
                isActive("/analyze")
                  ? "text-slate-900 dark:text-white border-b-2 border-[#137fec]"
                  : "text-slate-600 dark:text-white border-b-2 border-transparent"
              }`}
            >
              Analyze
            </Link>
            <Link
              to="/dashboard"
              className={`text-sm font-medium leading-normal transition-colors hover:text-[#137fec] ${
                isActive("/dashboard")
                  ? "text-slate-900 dark:text-white border-b-2 border-[#137fec]"
                  : "text-slate-600 dark:text-white border-b-2 border-transparent"
              }`}
            >
              Dashboard
            </Link>
          </div>

          {/* Desktop Right Section */}
          <div className="hidden md:flex items-center space-x-4">
            {token ? (
              <>
                {/* Avatar Dropdown */}
                <div className="relative">
                  <button
                    onClick={toggleAvatarDropdown}
                    className="flex items-center space-x-2 hover:bg-slate-100 dark:hover:bg-slate-700/50 px-3 py-2 rounded-lg transition"
                    aria-label="User menu"
                    aria-expanded={isAvatarOpen}
                  >
                    <div className="w-8 h-8 rounded-full bg-[#137fec] flex items-center justify-center text-xs font-bold text-white">
                      {user?.username?.[0]?.toUpperCase() ||
                        user?.email?.[0]?.toUpperCase() ||
                        "U"}
                    </div>
                  </button>

                  {/* Dropdown Menu */}
                  {isAvatarOpen && (
                    <div className="absolute right-0 mt-2 w-48 rounded-lg bg-white dark:bg-[#192633] shadow-lg border border-[#233648] overflow-hidden">
                      <div className="px-4 py-3 border-b border-[#233648]">
                        <p className="text-sm font-semibold text-slate-900 dark:text-white truncate">
                          {user?.username || user?.email || "User"}
                        </p>
                        <p className="text-xs text-[#92adc9] truncate">
                          {user?.email}
                        </p>
                      </div>
                      <Link
                        to="/profile"
                        className="block px-4 py-2 text-sm text-slate-700 dark:text-[#92adc9] hover:bg-slate-100 dark:hover:bg-[#233648] transition"
                        onClick={() => setIsAvatarOpen(false)}
                      >
                        👤 Profile
                      </Link>
                      <Link
                        to="/settings"
                        className="block px-4 py-2 text-sm text-slate-700 dark:text-[#92adc9] hover:bg-slate-100 dark:hover:bg-[#233648] transition"
                        onClick={() => setIsAvatarOpen(false)}
                      >
                        ⚙️ Settings
                      </Link>
                      <button
                        onClick={handleLogout}
                        className="w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition border-t border-[#233648]"
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
                  className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 bg-[#137fec] text-white text-sm font-bold leading-normal tracking-[0.015em] hover:bg-opacity-90 transition-opacity"
                >
                  <span className="truncate">Login</span>
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={toggleMenu}
            className="md:hidden inline-flex items-center justify-center p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700/50 transition"
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
          <div className="md:hidden pb-4 space-y-1 border-t border-[#233648]">
            <Link
              to="/"
              className={`block px-3 py-2 rounded-md text-base font-medium transition ${
                isActive("/")
                  ? "bg-[#137fec]/10 text-[#137fec]"
                  : "text-slate-700 dark:text-[#92adc9] hover:bg-slate-100 dark:hover:bg-[#233648]"
              }`}
              onClick={() => setIsMenuOpen(false)}
            >
              Home
            </Link>
            <Link
              to="/analyze"
              className={`block px-3 py-2 rounded-md text-base font-medium transition ${
                isActive("/analyze")
                  ? "bg-[#137fec]/10 text-[#137fec]"
                  : "text-slate-700 dark:text-[#92adc9] hover:bg-slate-100 dark:hover:bg-[#233648]"
              }`}
              onClick={() => setIsMenuOpen(false)}
            >
              Analyze
            </Link>
            <Link
              to="/dashboard"
              className={`block px-3 py-2 rounded-md text-base font-medium transition ${
                isActive("/dashboard")
                  ? "bg-[#137fec]/10 text-[#137fec]"
                  : "text-slate-700 dark:text-[#92adc9] hover:bg-slate-100 dark:hover:bg-[#233648]"
              }`}
              onClick={() => setIsMenuOpen(false)}
            >
              Dashboard
            </Link>

            <div className="border-t border-[#233648] pt-2 mt-2">
              {token ? (
                <>
                  <Link
                    to="/profile"
                    className="block px-3 py-2 rounded-md text-base font-medium text-slate-700 dark:text-[#92adc9] hover:bg-slate-100 dark:hover:bg-[#233648] transition"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    👤 Profile
                  </Link>
                  <Link
                    to="/settings"
                    className="block px-3 py-2 rounded-md text-base font-medium text-slate-700 dark:text-[#92adc9] hover:bg-slate-100 dark:hover:bg-[#233648] transition"
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
                    className="block px-3 py-2 rounded-md text-base font-medium text-slate-700 dark:text-[#92adc9] hover:bg-slate-100 dark:hover:bg-[#233648] transition"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Login
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
