import { useState, useEffect } from "react";

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface PrivacySettings {
  allowImageImprovement: boolean;
}

type CameraPermission = "granted" | "denied" | "prompt" | null;

export default function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const [cameraPermission, setCameraPermission] =
    useState<CameraPermission>(null);
  const [storageSize, setStorageSize] = useState<string>("0 KB");
  const [confirmingAction, setConfirmingAction] = useState<string | null>(null);
  const [allowImageImprovement, setAllowImageImprovement] = useState(false);
  const [privacySaved, setPrivacySaved] = useState(false);

  // Calculate localStorage size
  useEffect(() => {
    calculateStorageSize();

    // Load privacy settings
    const savedPrivacy = localStorage.getItem("privacySettings");
    if (savedPrivacy) {
      try {
        const settings = JSON.parse(savedPrivacy) as PrivacySettings;
        setAllowImageImprovement(settings.allowImageImprovement);
      } catch (e) {
        console.error("Failed to parse privacy settings:", e);
      }
    }
  }, []);

  const calculateStorageSize = () => {
    let total = 0;
    for (const key in localStorage) {
      if (localStorage.hasOwnProperty(key)) {
        total += localStorage[key].length + key.length;
      }
    }
    // Convert bytes to KB
    const kb = Math.ceil(total / 1024);
    setStorageSize(`${kb} KB`);
  };

  // Check camera permission
  useEffect(() => {
    const checkCameraPermission = async () => {
      try {
        if ("permissions" in navigator) {
          const permission = await navigator.permissions.query({
            name: "camera" as PermissionName,
          });
          setCameraPermission(
            (permission.state as CameraPermission) || "prompt"
          );

          // Listen for permission changes
          permission.addEventListener("change", () => {
            setCameraPermission(
              (permission.state as CameraPermission) || "prompt"
            );
          });
        }
      } catch (e) {
        console.error("Failed to check camera permission:", e);
      }
    };

    if (isOpen) {
      checkCameraPermission();
    }
  }, [isOpen]);

  const handleRequestCameraPermission = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false,
      });
      // Stop the stream immediately
      stream.getTracks().forEach((track) => track.stop());
      // Re-check permission status
      if ("permissions" in navigator) {
        const permission = await navigator.permissions.query({
          name: "camera" as PermissionName,
        });
        setCameraPermission((permission.state as CameraPermission) || "prompt");
      }
    } catch (e) {
      console.error("Camera access failed:", e);
    }
  };

  const handleRevokeCameraPermission = () => {
    // Note: Revoking camera permission requires browser settings
    alert(
      "To revoke camera permissions, please update your browser settings:\n\n" +
        "Chrome: Settings → Privacy → Site Settings → Camera\n" +
        "Firefox: Preferences → Privacy → Permissions → Camera\n" +
        "Safari: Preferences → Websites → Camera"
    );
  };

  const handleClearHistory = () => {
    if (confirmingAction === "clear-history") {
      const reminderSettings = localStorage.getItem("reminderSettings");
      const authToken = localStorage.getItem("authToken");
      const user = localStorage.getItem("user");

      localStorage.clear();

      // Restore essential settings
      if (reminderSettings) {
        localStorage.setItem("reminderSettings", reminderSettings);
      }
      if (authToken) {
        localStorage.setItem("authToken", authToken);
      }
      if (user) {
        localStorage.setItem("user", user);
      }

      calculateStorageSize();
      setConfirmingAction(null);
      alert(
        "✅ Analysis history cleared. Your settings and login are preserved."
      );
    } else {
      setConfirmingAction("clear-history");
    }
  };

  const handleToggleImageImprovement = () => {
    const newValue = !allowImageImprovement;
    setAllowImageImprovement(newValue);

    const privacySettings: PrivacySettings = {
      allowImageImprovement: newValue,
    };
    localStorage.setItem("privacySettings", JSON.stringify(privacySettings));

    setPrivacySaved(true);
    setTimeout(() => setPrivacySaved(false), 3000);
  };

  const handleWipeLocalData = () => {
    if (confirmingAction === "wipe-data") {
      localStorage.clear();
      sessionStorage.clear();
      setStorageSize("0 KB");
      setConfirmingAction(null);
      alert("✅ All local data has been wiped. You will be logged out.");
      setTimeout(() => {
        window.location.href = "/";
      }, 1000);
    } else {
      setConfirmingAction("wipe-data");
    }
  };

  const handleDeleteAccount = () => {
    alert(
      "Account deletion will be implemented soon.\n\n" +
        "This will permanently delete your account, all analysis history, and personal data from our servers.\n\n" +
        "This action cannot be undone."
    );
  };

  const handleCancelConfirm = () => {
    setConfirmingAction(null);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-gray-700 to-gray-900 p-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-white">⚙️ Settings</h2>
          <button
            onClick={onClose}
            className="text-white hover:text-gray-200 text-2xl font-bold"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Storage Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm font-semibold text-blue-900 mb-1">
              💾 Local Storage Usage
            </p>
            <p className="text-2xl font-bold text-blue-600">{storageSize}</p>
            <p className="text-xs text-blue-700 mt-2">
              Includes: analysis history, settings, authentication tokens
            </p>
          </div>

          {/* Camera Permissions */}
          <div className="border rounded-lg p-6 space-y-4">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-2xl">📹</span>
              <h3 className="text-lg font-semibold text-gray-800">
                Camera Permissions
              </h3>
            </div>

            <div className="bg-gray-50 rounded p-4">
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm font-medium text-gray-700">
                  Permission Status:
                </p>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-semibold ${
                    cameraPermission === "granted"
                      ? "bg-green-100 text-green-800"
                      : cameraPermission === "denied"
                      ? "bg-red-100 text-red-800"
                      : "bg-gray-100 text-gray-800"
                  }`}
                >
                  {cameraPermission === "granted"
                    ? "✅ Granted"
                    : cameraPermission === "denied"
                    ? "❌ Denied"
                    : "⚪ Not Requested"}
                </span>
              </div>

              {cameraPermission === "granted" && (
                <div className="flex items-start gap-2 mb-4">
                  <span className="text-green-600 text-lg">✓</span>
                  <div>
                    <p className="text-sm text-gray-700">
                      Your camera access is enabled.
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      You can capture photos and record videos.
                    </p>
                  </div>
                </div>
              )}

              {cameraPermission === "denied" && (
                <div className="flex items-start gap-2 mb-4">
                  <span className="text-red-600 text-lg">✗</span>
                  <div>
                    <p className="text-sm text-gray-700">
                      Camera access is blocked.
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      Update your browser settings to enable camera access.
                    </p>
                  </div>
                </div>
              )}

              {cameraPermission === "prompt" && (
                <div className="flex items-start gap-2 mb-4">
                  <span className="text-gray-600 text-lg">?</span>
                  <div>
                    <p className="text-sm text-gray-700">
                      Camera permission not yet requested.
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      Click the button below to request access.
                    </p>
                  </div>
                </div>
              )}
            </div>

            <div className="flex gap-3">
              {cameraPermission !== "granted" && (
                <button
                  onClick={handleRequestCameraPermission}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg transition"
                >
                  Enable Camera Access
                </button>
              )}
              {cameraPermission === "granted" && (
                <button
                  onClick={handleRevokeCameraPermission}
                  className="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition"
                >
                  Revoke Camera Access
                </button>
              )}
            </div>
          </div>

          {/* Privacy & Policy */}
          <div className="border rounded-lg p-6 space-y-4">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-2xl">🔒</span>
              <h3 className="text-lg font-semibold text-gray-800">
                Privacy & Policy
              </h3>
            </div>

            {/* Image Improvement Toggle */}
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <p className="text-sm font-semibold text-purple-900 mb-1">
                    Allow Using Images to Improve Models
                  </p>
                  <p className="text-xs text-purple-800">
                    Help us improve our AI models by allowing your anonymized
                    images to be used for research and model training. This is
                    completely optional and you can change it anytime.
                  </p>
                </div>
                <button
                  onClick={handleToggleImageImprovement}
                  className={`relative inline-flex h-8 w-14 items-center rounded-full transition flex-shrink-0 ${
                    allowImageImprovement ? "bg-purple-600" : "bg-gray-300"
                  }`}
                >
                  <span
                    className={`inline-block h-6 w-6 transform rounded-full bg-white transition ${
                      allowImageImprovement ? "translate-x-7" : "translate-x-1"
                    }`}
                  />
                </button>
              </div>
              {privacySaved && (
                <div className="mt-3 text-xs text-purple-700 font-medium">
                  ✅ Preference saved
                </div>
              )}
            </div>

            {/* Policy Links */}
            <div className="space-y-2">
              <p className="text-sm font-semibold text-gray-800 mb-3">
                📄 Legal Documents
              </p>
              <a
                href="/privacy-policy"
                target="_blank"
                rel="noopener noreferrer"
                className="block w-full bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg p-3 transition"
              >
                <p className="text-sm font-medium text-blue-900">
                  Privacy Policy
                </p>
                <p className="text-xs text-blue-700">
                  Learn how we collect, use, and protect your data
                </p>
              </a>

              <a
                href="/disclaimer"
                target="_blank"
                rel="noopener noreferrer"
                className="block w-full bg-yellow-50 hover:bg-yellow-100 border border-yellow-200 rounded-lg p-3 transition"
              >
                <p className="text-sm font-medium text-yellow-900">
                  Medical Disclaimer
                </p>
                <p className="text-xs text-yellow-700">
                  Important disclaimer about medical advice and limitations
                </p>
              </a>
            </div>

            {/* Delete Account */}
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-sm font-semibold text-red-900 mb-2">
                🚨 Delete Account
              </p>
              <p className="text-xs text-red-800 mb-4">
                Permanently delete your account and all associated data. This
                action is irreversible.
              </p>
              <button
                onClick={handleDeleteAccount}
                className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition text-sm"
              >
                Delete My Account
              </button>
            </div>
          </div>

          {/* Data Management */}
          <div className="border rounded-lg p-6 space-y-4">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-2xl">🗑️</span>
              <h3 className="text-lg font-semibold text-gray-800">
                Data Management
              </h3>
            </div>

            {/* Wipe Local Data */}
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-sm font-semibold text-red-900 mb-2">
                Wipe All Local Data
              </p>
              <p className="text-xs text-red-800 mb-4">
                Remove all data stored locally on this device (token, cached
                analyses, settings). Server data will not be affected.
              </p>

              {confirmingAction === "wipe-data" ? (
                <div className="bg-red-100 border border-red-300 rounded p-3 mb-3">
                  <p className="text-sm font-semibold text-red-900">
                    ⚠️ Are you sure?
                  </p>
                  <p className="text-xs text-red-800 mt-1">
                    This will delete all local data and you will be logged out
                    immediately. This action cannot be undone.
                  </p>
                  <div className="flex gap-2 mt-3">
                    <button
                      onClick={handleWipeLocalData}
                      className="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-3 rounded text-sm transition"
                    >
                      Yes, Wipe Data
                    </button>
                    <button
                      onClick={handleCancelConfirm}
                      className="flex-1 bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 px-3 rounded text-sm transition"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  onClick={() => setConfirmingAction("wipe-data")}
                  className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition text-sm"
                >
                  Wipe Local Data
                </button>
              )}
            </div>

            {/* Clear History */}
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
              <p className="text-sm font-semibold text-orange-900 mb-2">
                Clear Analysis History
              </p>
              <p className="text-xs text-orange-800 mb-4">
                Remove all analysis results and history. Your settings and login
                will be preserved.
              </p>

              {confirmingAction === "clear-history" ? (
                <div className="bg-yellow-100 border border-yellow-300 rounded p-3 mb-3">
                  <p className="text-sm font-semibold text-yellow-900">
                    ⚠️ Are you sure?
                  </p>
                  <p className="text-xs text-yellow-800 mt-1">
                    This will delete all your analysis history. This action
                    cannot be undone.
                  </p>
                  <div className="flex gap-2 mt-3">
                    <button
                      onClick={handleClearHistory}
                      className="flex-1 bg-orange-600 hover:bg-orange-700 text-white font-semibold py-2 px-3 rounded text-sm transition"
                    >
                      Yes, Clear History
                    </button>
                    <button
                      onClick={handleCancelConfirm}
                      className="flex-1 bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 px-3 rounded text-sm transition"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  onClick={() => setConfirmingAction("clear-history")}
                  className="w-full bg-orange-500 hover:bg-orange-600 text-white font-semibold py-2 px-4 rounded-lg transition"
                >
                  Clear History
                </button>
              )}
            </div>
          </div>

          {/* Info Box */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <p className="text-xs text-gray-700">
              💡 <span className="font-medium">Need help?</span> These settings
              help you manage your privacy, storage, and device permissions. Be
              careful with data deletion as it cannot be reversed.
            </p>
          </div>

          {/* Close Button */}
          <button
            onClick={onClose}
            className="w-full bg-gray-600 hover:bg-gray-700 text-white font-semibold py-3 rounded-lg transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
