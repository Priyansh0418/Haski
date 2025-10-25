import { useRef, useState, useEffect } from "react";

interface CameraCaptureProps {
  onCapture?: (file: File) => void;
  onError?: (error: string) => void;
}

type PermissionState = "idle" | "granted" | "denied" | "not-supported";

/**
 * CameraCapture Component
 * 
 * Features:
 * - Reliable getUserMedia with proper constraints
 * - Canvas-based photo capture with JPEG compression
 * - Fallback file upload option
 * - Permission denied handling
 * - Track cleanup on unmount
 * - HTTPS/localhost support detection
 */
export default function CameraCapture({
  onCapture,
  onError,
}: CameraCaptureProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const [permissionState, setPermissionState] =
    useState<PermissionState>("idle");
  const [isStreaming, setIsStreaming] = useState(false);
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const [isCapturing, setIsCapturing] = useState(false);
  const [supportsMediaDevices, setSupportsMediaDevices] = useState(true);

  // Check browser support on mount
  useEffect(() => {
    const supported = !!(
      navigator.mediaDevices && navigator.mediaDevices.getUserMedia
    );
    setSupportsMediaDevices(supported);
    
    // Cleanup tracks on unmount
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      }
    };
  }, []);

  /**
   * Request camera permission and start stream
   */
  const startCamera = async () => {
    try {
      setPermissionState("idle");

      if (!supportsMediaDevices) {
        setPermissionState("not-supported");
        onError?.("Your device does not support camera access");
        return;
      }

      // Check if running on HTTPS or localhost
      const isSecureContext =
        window.location.protocol === "https:" ||
        window.location.hostname === "localhost" ||
        window.location.hostname === "127.0.0.1";

      if (!isSecureContext) {
        onError?.(
          "Camera requires HTTPS (except on localhost). Please use a secure connection."
        );
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "user",
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;

        // Handle both old and new browser APIs
        const playPromise = videoRef.current.play();
        if (playPromise !== undefined) {
          playPromise
            .then(() => {
              setIsStreaming(true);
              setIsCameraOpen(true);
              setPermissionState("granted");
              console.log("Camera stream started successfully");
            })
            .catch((err) => {
              console.error("Play error:", err);
              onError?.("Failed to start video playback");
              setPermissionState("not-supported");
            });
        } else {
          // Older browsers
          setIsStreaming(true);
          setIsCameraOpen(true);
          setPermissionState("granted");
        }
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Unknown error";
      console.error("Camera error:", errorMsg);

      if (errorMsg.includes("NotAllowedError")) {
        setPermissionState("denied");
        onError?.(
          "Camera permission denied. Please enable it in your browser settings."
        );
      } else if (
        errorMsg.includes("NotFoundError") ||
        errorMsg.includes("NotAvailable")
      ) {
        setPermissionState("not-supported");
        onError?.("No camera device found on this device");
      } else {
        setPermissionState("not-supported");
        onError?.(errorMsg);
      }
    }
  };

  /**
   * Stop camera stream
   */
  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setIsStreaming(false);
    setIsCameraOpen(false);
  };

  /**
   * Capture current frame from video to canvas
   * Convert to JPEG blob and create File
   */
  const capturePhoto = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    setIsCapturing(true);

    try {
      const ctx = canvasRef.current.getContext("2d");
      if (!ctx) throw new Error("Failed to get canvas context");

      // Set canvas size to match video
      canvasRef.current.width = videoRef.current.videoWidth;
      canvasRef.current.height = videoRef.current.videoHeight;

      // Draw video frame to canvas
      ctx.drawImage(videoRef.current, 0, 0);

      // Convert to blob with JPEG compression
      canvasRef.current.toBlob(
        (blob) => {
          if (!blob) {
            onError?.("Failed to capture image");
            setIsCapturing(false);
            return;
          }

          const file = new File([blob], "photo.jpg", {
            type: "image/jpeg",
            lastModified: Date.now(),
          });

          console.log(`Photo captured: ${(blob.size / 1024).toFixed(2)}KB`);
          stopCamera();
          onCapture?.(file);
          setIsCapturing(false);
        },
        "image/jpeg",
        0.92 // 92% quality
      );
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Capture failed";
      onError?.(errorMsg);
      setIsCapturing(false);
    }
  };

  /**
   * Handle file selection from gallery
   */
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onCapture?.(file);
      // Reset input so same file can be selected again
      event.target.value = "";
    }
  };

  // ========================================================================
  // RENDER: Permission Denied State
  // ========================================================================

  if (permissionState === "denied") {
    return (
      <div className="w-full max-w-2xl mx-auto">
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border-2 border-yellow-400 dark:border-yellow-600 rounded-2xl p-6 sm:p-8">
          <div className="flex items-start gap-4">
            <span className="text-4xl flex-shrink-0">🚫</span>
            <div>
              <h3 className="text-lg font-bold text-yellow-900 dark:text-yellow-200 mb-2">
                Camera Permission Denied
              </h3>
              <p className="text-yellow-800 dark:text-yellow-300 mb-4">
                To use the camera, you need to grant permission in your browser
                settings.
              </p>
              <ol className="text-yellow-800 dark:text-yellow-300 text-sm space-y-2 mb-4">
                <li>1. Click the lock icon in your address bar</li>
                <li>2. Find "Camera" in the permissions list</li>
                <li>3. Change it to "Allow"</li>
                <li>4. Refresh this page and try again</li>
              </ol>
              <div className="flex gap-2 flex-wrap">
                <button
                  onClick={() => {
                    setPermissionState("idle");
                    startCamera();
                  }}
                  className="bg-yellow-600 hover:bg-yellow-700 text-white font-semibold py-2 px-4 rounded-lg transition"
                >
                  🔄 Retry
                </button>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="bg-yellow-500 hover:bg-yellow-600 text-white font-semibold py-2 px-4 rounded-lg transition"
                >
                  📁 Choose from Gallery
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>
    );
  }

  // ========================================================================
  // RENDER: Not Supported State
  // ========================================================================

  if (permissionState === "not-supported" && !supportsMediaDevices) {
    return (
      <div className="w-full max-w-2xl mx-auto">
        <div className="bg-red-50 dark:bg-red-900/20 border-2 border-red-400 dark:border-red-600 rounded-2xl p-6 sm:p-8">
          <div className="flex items-start gap-4">
            <span className="text-4xl flex-shrink-0">⚠️</span>
            <div>
              <h3 className="text-lg font-bold text-red-900 dark:text-red-200 mb-2">
                Camera Not Supported
              </h3>
              <p className="text-red-800 dark:text-red-300 mb-4">
                Your device or browser doesn't support camera access. Please
                use a different device or browser, or upload a photo manually.
              </p>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition"
              >
                📁 Upload Photo
              </button>
            </div>
          </div>
        </div>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>
    );
  }

  // ========================================================================
  // RENDER: Camera Open Modal
  // ========================================================================

  if (isCameraOpen && isStreaming) {
    return (
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
        <div className="bg-gray-900 dark:bg-gray-950 rounded-2xl shadow-2xl border-2 border-cyan-500/50 overflow-hidden max-w-2xl w-full">
          {/* Modal Header */}
          <div className="bg-gradient-to-r from-blue-600 to-cyan-600 px-6 py-4 flex items-center justify-between">
            <h2 className="text-xl font-bold text-white">📷 Camera</h2>
            <button
              onClick={() => {
                setIsCameraOpen(false);
                stopCamera();
              }}
              className="text-white hover:bg-white/20 rounded-lg p-2 transition"
              aria-label="Close camera"
            >
              ✕
            </button>
          </div>

          {/* Modal Body - Camera View */}
          <div className="p-6 space-y-4 bg-black">
            <div className="relative bg-black rounded-xl overflow-hidden shadow-xl border-2 border-cyan-400/30 w-full" style={{ paddingBottom: "56.25%", position: "relative" }}>
              {/* Video Stream */}
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                style={{
                  position: "absolute",
                  top: 0,
                  left: 0,
                  width: "100%",
                  height: "100%",
                  objectFit: "cover",
                  transform: "scaleX(-1)",
                  backgroundColor: "#000",
                  display: "block",
                }}
              />

              {/* Hidden Canvas for Capture */}
              <canvas
                ref={canvasRef}
                style={{
                  display: "none",
                  position: "absolute",
                }}
              />
            </div>

            {/* Controls */}
            <div className="flex gap-3">
              <button
                onClick={capturePhoto}
                disabled={isCapturing}
                className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-4 px-4 rounded-xl transition shadow-lg hover:shadow-xl active:scale-95 flex items-center justify-center gap-2"
              >
                {isCapturing ? (
                  <>
                    <span className="inline-block animate-spin">⏳</span>
                    Processing...
                  </>
                ) : (
                  <>
                    <span>📸</span>
                    <span>Capture Photo</span>
                  </>
                )}
              </button>
              <button
                onClick={() => {
                  setIsCameraOpen(false);
                  stopCamera();
                }}
                disabled={isCapturing}
                className="flex-1 bg-slate-500 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-4 px-4 rounded-xl transition shadow-lg"
              >
                ✕ Close
              </button>
            </div>

            {/* File Upload Fallback */}
            <div className="relative pt-2 border-t border-slate-600">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                capture="environment"
                onChange={handleFileSelect}
                className="hidden"
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                className="w-full border-2 border-dashed border-slate-400 hover:border-blue-600 text-slate-300 hover:text-blue-400 font-semibold py-3 px-4 rounded-xl transition"
              >
                📁 Choose from Gallery
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ========================================================================
  // RENDER: Initial State - Buttons
  // ========================================================================

  return (
    <div className="w-full max-w-2xl mx-auto space-y-4">
      <button
        onClick={startCamera}
        className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-bold py-4 px-6 rounded-xl transition shadow-lg hover:shadow-xl active:scale-95 flex items-center justify-center gap-2"
      >
        <span className="text-2xl">📱</span>
        <span>Start Camera</span>
      </button>

      <div className="relative">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          onChange={handleFileSelect}
          className="hidden"
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          className="w-full border-2 border-dashed border-slate-400 dark:border-slate-600 hover:border-blue-600 dark:hover:border-cyan-400 text-slate-700 dark:text-slate-300 hover:text-blue-600 dark:hover:text-cyan-400 font-semibold py-4 px-6 rounded-xl transition"
        >
          📁 Choose from Gallery
        </button>
      </div>

      {/* Info note */}
      <p className="text-sm text-slate-500 dark:text-slate-400 text-center">
        💡 Tip: For best results, ensure good lighting and face the camera directly
      </p>
    </div>
  );
}
      
        