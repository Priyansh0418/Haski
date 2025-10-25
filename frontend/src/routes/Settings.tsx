import { useNavigate } from "react-router-dom";
import { useState } from "react";
import SettingsModal from "../components/SettingsModal";

/**
 * Settings Page - Full page version of settings
 * Features:
 * - Privacy toggles (image improvement opt-in)
 * - Data management (wipe local, clear history)
 * - Legal links (privacy policy, disclaimer)
 * - Delete account button (placeholder)
 * - Back to dashboard button
 */
export default function Settings() {
  const navigate = useNavigate();
  const [isOpen] = useState(true); // Always open when on this page

  return (
    <div className="w-full py-8 md:py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 flex items-center gap-4">
          <button
            onClick={() => navigate("/dashboard")}
            className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 transition"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white">
            ⚙️ Settings
          </h1>
        </div>

        {/* Settings Content - Using modal component adapted for full page */}
        <div className="bg-white/80 dark:bg-white/10 backdrop-blur-md rounded-xl shadow-lg border border-white/20 dark:border-white/10">
          <SettingsModal
            isOpen={isOpen}
            onClose={() => navigate("/dashboard")}
          />
        </div>
      </div>
    </div>
  );
}
