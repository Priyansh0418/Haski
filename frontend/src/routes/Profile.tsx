import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";

export default function Profile() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [formData, setFormData] = useState({
    username: user?.username || "",
    email: user?.email || "",
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;

    setIsSaving(true);
    setError(null);

    try {
      const apiUrl =
        import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
      const response = await fetch(apiUrl + "/api/v1/profile", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + token,
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error("Failed to update profile");
      }

      setIsEditing(false);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update profile");
      console.error(err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      username: user?.username || "",
      email: user?.email || "",
    });
    setIsEditing(false);
    setError(null);
  };

  return (
    <div className="w-full py-8 md:py-12">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 dark:from-blue-400 dark:to-cyan-400 bg-clip-text text-transparent mb-2">
            My Profile
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Manage your account information
          </p>
        </div>

        {/* Success Message */}
        {success && (
          <div className="mb-6 p-4 bg-green-100 dark:bg-green-900/30 border-l-4 border-green-600 dark:border-green-400 rounded flex items-start gap-3">
            <span className="text-2xl">✅</span>
            <div>
              <p className="font-semibold text-green-800 dark:text-green-200">
                Profile Updated
              </p>
              <p className="text-green-700 dark:text-green-300 text-sm">
                Your changes have been saved successfully.
              </p>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-100 dark:bg-red-900/30 border-l-4 border-red-600 dark:border-red-400 rounded flex items-start gap-3">
            <span className="text-2xl">⚠️</span>
            <div>
              <p className="font-semibold text-red-800 dark:text-red-200">
                Update Failed
              </p>
              <p className="text-red-700 dark:text-red-300 text-sm">{error}</p>
            </div>
          </div>
        )}

        {/* Profile Card */}
        <div className="bg-white/80 dark:bg-white/10 backdrop-blur-md rounded-xl shadow-lg p-8 border border-white/20 dark:border-white/10">
          {isEditing ? (
            // Edit Form
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                  Username
                </label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-600 dark:focus:ring-blue-400 focus:border-transparent transition"
                  placeholder="Enter your username"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-slate-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-600 dark:focus:ring-blue-400 focus:border-transparent transition"
                  placeholder="Enter your email"
                />
              </div>

              <div className="flex flex-col sm:flex-row gap-3 pt-4">
                <button
                  type="submit"
                  disabled={isSaving}
                  className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition shadow-lg"
                >
                  {isSaving ? "💾 Saving..." : "💾 Save Changes"}
                </button>
                <button
                  type="button"
                  onClick={handleCancel}
                  className="flex-1 bg-gray-400 dark:bg-gray-600 hover:bg-gray-500 dark:hover:bg-gray-700 text-white font-semibold py-3 px-6 rounded-lg transition"
                >
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            // View Mode
            <div className="space-y-6">
              <div>
                <p className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-1 uppercase tracking-wide">
                  Username
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {user?.username || "N/A"}
                </p>
              </div>

              <div>
                <p className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-1 uppercase tracking-wide">
                  Email
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {user?.email || "N/A"}
                </p>
              </div>

              <div className="border-t border-gray-200 dark:border-gray-700 pt-6 flex flex-col sm:flex-row gap-3">
                <button
                  onClick={() => setIsEditing(true)}
                  className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-semibold py-3 px-6 rounded-lg transition shadow-lg"
                >
                  ✏️ Edit Profile
                </button>
                <button
                  onClick={() => navigate("/dashboard")}
                  className="flex-1 bg-white/80 dark:bg-white/10 hover:bg-white/90 dark:hover:bg-white/20 text-gray-800 dark:text-white font-semibold py-3 px-6 rounded-lg transition border border-white/20 dark:border-white/10"
                >
                  ← Back to Dashboard
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
