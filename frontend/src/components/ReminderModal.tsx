import { useState, useEffect } from "react";

interface ReminderSettings {
  enabled: boolean;
  time: string; // HH:MM format
  notificationGranted: boolean;
}

interface ReminderModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ReminderModal({ isOpen, onClose }: ReminderModalProps) {
  const [settings, setSettings] = useState<ReminderSettings>({
    enabled: false,
    time: "09:00",
    notificationGranted: false,
  });
  const [saved, setSaved] = useState(false);
  const [permissionStatus, setPermissionStatus] = useState<
    "default" | "granted" | "denied"
  >("default");

  // Load settings from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem("reminderSettings");
    if (stored) {
      try {
        setSettings(JSON.parse(stored));
      } catch (e) {
        console.error("Failed to parse reminder settings:", e);
      }
    }

    // Check notification permission status
    if ("Notification" in window) {
      setPermissionStatus(
        Notification.permission as "default" | "granted" | "denied"
      );
    }
  }, []);

  // Monitor and check reminder time
  useEffect(() => {
    if (!settings.enabled) return;

    const checkReminder = () => {
      const now = new Date();
      const currentTime = `${String(now.getHours()).padStart(2, "0")}:${String(
        now.getMinutes()
      ).padStart(2, "0")}`;

      if (currentTime === settings.time) {
        // Show notification if permission granted
        if (settings.notificationGranted && "Notification" in window) {
          try {
            new Notification("Haski Reminder", {
              body: "Time for your skincare routine! 🧴",
              icon: "/favicon.ico",
              tag: "haski-reminder",
              requireInteraction: false,
            });
          } catch (e) {
            console.error("Failed to show notification:", e);
          }
        }
        // Show in-app alert as backup
        alert("🧴 Time for your skincare routine!");
      }
    };

    // Check every minute
    const interval = setInterval(checkReminder, 60000);

    // Initial check
    checkReminder();

    return () => clearInterval(interval);
  }, [settings.enabled, settings.time, settings.notificationGranted]);

  const handleRequestNotificationPermission = async () => {
    if (!("Notification" in window)) {
      alert("Your browser does not support notifications");
      return;
    }

    try {
      const permission = await Notification.requestPermission();
      setPermissionStatus(permission);

      if (permission === "granted") {
        setSettings((prev) => ({
          ...prev,
          notificationGranted: true,
        }));
        // Test notification
        new Notification("Haski", {
          body: "Notifications enabled! ✅",
          icon: "/favicon.ico",
        });
      }
    } catch (e) {
      console.error("Failed to request notification permission:", e);
    }
  };

  const handleToggle = () => {
    setSettings((prev) => ({
      ...prev,
      enabled: !prev.enabled,
    }));
    setSaved(false);
  };

  const handleTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSettings((prev) => ({
      ...prev,
      time: e.target.value,
    }));
    setSaved(false);
  };

  const handleSave = () => {
    localStorage.setItem("reminderSettings", JSON.stringify(settings));
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleClose = () => {
    handleSave();
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-sm w-full">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-cyan-600 p-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-white">⏰ Daily Reminder</h2>
          <button
            onClick={handleClose}
            className="text-white hover:text-gray-200 text-2xl font-bold"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Toggle */}
          <div className="flex items-center justify-between">
            <label className="text-lg font-semibold text-gray-800">
              Enable Reminders
            </label>
            <button
              onClick={handleToggle}
              className={`relative inline-flex h-8 w-14 items-center rounded-full transition ${
                settings.enabled ? "bg-blue-600" : "bg-gray-300"
              }`}
            >
              <span
                className={`inline-block h-6 w-6 transform rounded-full bg-white transition ${
                  settings.enabled ? "translate-x-7" : "translate-x-1"
                }`}
              />
            </button>
          </div>

          {/* Time Picker */}
          {settings.enabled && (
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-gray-800">
                Reminder Time
              </label>
              <input
                type="time"
                value={settings.time}
                onChange={handleTimeChange}
                className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none text-lg"
              />
              <p className="text-xs text-gray-600">
                You will receive a reminder at {settings.time} every day.
              </p>
            </div>
          )}

          {/* Notification Permission */}
          {settings.enabled && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm font-semibold text-blue-900 mb-3">
                🔔 Notifications
              </p>

              {permissionStatus === "granted" &&
                settings.notificationGranted && (
                  <div className="flex items-start gap-2">
                    <span className="text-green-600 text-xl">✅</span>
                    <div>
                      <p className="text-sm text-blue-800 font-medium">
                        Notifications Enabled
                      </p>
                      <p className="text-xs text-blue-700">
                        You'll get browser notifications at your reminder time.
                      </p>
                    </div>
                  </div>
                )}

              {permissionStatus !== "granted" && (
                <button
                  onClick={handleRequestNotificationPermission}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition"
                >
                  Enable Browser Notifications
                </button>
              )}

              {permissionStatus === "denied" && (
                <div className="flex items-start gap-2">
                  <span className="text-red-600 text-xl">⚠️</span>
                  <div>
                    <p className="text-sm text-red-800 font-medium">
                      Notifications Blocked
                    </p>
                    <p className="text-xs text-red-700">
                      Update your browser settings to enable notifications.
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Info Box */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <p className="text-xs text-gray-700">
              💡 <span className="font-medium">How it works:</span> Enable this
              feature to get a daily reminder for your skincare routine. The
              reminder uses your browser's notification system (if enabled) or
              displays an in-app alert.
            </p>
          </div>

          {/* Save Feedback */}
          {saved && (
            <div className="bg-green-100 text-green-800 p-3 rounded-lg text-sm font-medium text-center">
              ✅ Reminder settings saved!
            </div>
          )}

          {/* Buttons */}
          <div className="flex gap-3">
            <button
              onClick={handleSave}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition"
            >
              Save Settings
            </button>
            <button
              onClick={handleClose}
              className="flex-1 bg-gray-500 hover:bg-gray-600 text-white font-semibold py-3 rounded-lg transition"
            >
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
