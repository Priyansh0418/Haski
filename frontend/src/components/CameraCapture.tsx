import { useRef, useState, useEffect, useCallback } from "react";

interface CameraCaptureProps {
  onCapture?: (file: File) => void;
  onError?: (error: string) => void;
}

type PermissionState = "idle" | "granted" | "denied" | "not-supported";
type LightingState = "good" | "poor" | "unknown";

export default function CameraCapture({
  onCapture,
  onError,
}: CameraCaptureProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  const [permissionState, setPermissionState] =
    useState<PermissionState>("idle");
  const [isStreaming, setIsStreaming] = useState(false);
  const [lightingState, setLightingState] = useState<LightingState>("unknown");
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [isCapturing, setIsCapturing] = useState(false);
  const [supportsMediaDevices, setSupportsMediaDevices] = useState(true);

  // Check browser support for getUserMedia
  useEffect(() => {
    const supported = !!(
      navigator.mediaDevices && navigator.mediaDevices.getUserMedia
    );
    setSupportsMediaDevices(supported);
  }, []);

  // Analyze frame brightness to provide lighting feedback
  const analyzeBrightness = useCallback((video: HTMLVideoElement) => {
    const canvas = document.createElement("canvas");
    canvas.width = 50;
    canvas.height = 50;
    const ctx = canvas.getContext("2d");

    if (!ctx) return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;

    let totalBrightness = 0;
    for (let i = 0; i < data.length; i += 4) {
      // Calculate luminance using standard formula
      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];
      const luminance = (r * 299 + g * 587 + b * 114) / 1000;
      totalBrightness += luminance;
    }

    const avgBrightness = totalBrightness / (canvas.width * canvas.height);
    setLightingState(avgBrightness > 80 ? "good" : "poor");
  }, []);

  // Monitor video stream for lighting updates
  useEffect(() => {
    if (!isStreaming || !videoRef.current) return;

    const updateLighting = () => {
      analyzeBrightness(videoRef.current!);
      animationFrameRef.current = requestAnimationFrame(updateLighting);
    };

    animationFrameRef.current = requestAnimationFrame(updateLighting);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isStreaming, analyzeBrightness]);

  // Request camera permission and start stream
  const startCamera = async () => {
    try {
      setPermissionState("idle");

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
        videoRef.current.onloadedmetadata = () => {
          videoRef.current?.play();
          setIsStreaming(true);
          setPermissionState("granted");
        };
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Unknown error";

      if (errorMsg.includes("NotAllowedError")) {
        setPermissionState("denied");
        onError?.(
          "Camera permission denied. Please enable it in your browser settings."
        );
      } else if (errorMsg.includes("NotFoundError")) {
        setPermissionState("not-supported");
        onError?.("No camera device found on this device.");
      } else {
        setPermissionState("not-supported");
        onError?.(errorMsg);
      }
    }
  };

  // Stop camera stream
  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setIsStreaming(false);
    setLightingState("unknown");

    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
  };

  // Capture current frame to File
  const capturePhoto = useCallback(() => {
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

      // Convert to blob and create File
      canvasRef.current.toBlob(
        (blob) => {
          if (!blob) {
            onError?.("Failed to capture image");
            setIsCapturing(false);
            return;
          }

          const file = new File([blob], "photo.jpg", { type: "image/jpeg" });
          setCapturedImage(canvasRef.current!.toDataURL("image/jpeg"));
          stopCamera();
          onCapture?.(file);
          setIsCapturing(false);
        },
        "image/jpeg",
        0.9
      );
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Capture failed";
      onError?.(errorMsg);
      setIsCapturing(false);
    }
  }, [onCapture, onError]);

  // Handle file selection from gallery
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setCapturedImage(e.target?.result as string);
        onCapture?.(file);
      };
      reader.readAsDataURL(file);
    }
  };

  // Reset to camera view
  const resetCapture = () => {
    setCapturedImage(null);
    startCamera();
  };

  // FALLBACK: Permission denied state
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
                <li>
                  1. Click the <strong>lock icon</strong> in your address bar
                </li>
                <li>
                  2. Find <strong>Camera</strong> in the permissions list
                </li>
                <li>
                  3. Change it to <strong>Allow</strong>
                </li>
                <li>4. Refresh this page and try again</li>
              </ol>
              <button
                onClick={() => {
                  setPermissionState("idle");
                  startCamera();
                }}
                className="bg-primary hover:bg-primary-600 dark:bg-primary-600 dark:hover:bg-primary text-white font-semibold py-2 px-4 rounded-lg transition mr-2"
              >
                🔄 Retry
              </button>
            </div>
          </div>
        </div>

        {/* Fallback file upload */}
        <div className="mt-6">
          <p className="text-center text-slate-600 dark:text-slate-400 mb-4 font-medium">
            Or upload a photo from your device:
          </p>
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
              � Choose from Gallery
            </button>
          </div>
        </div>
      </div>
    );
  }

  // FALLBACK: Not supported
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
                Your device or browser doesn't support camera access. Please use
                a different device or browser, or upload a photo manually.
              </p>
            </div>
          </div>
        </div>

        {/* Fallback file upload */}
        <div className="mt-6">
          <p className="text-center text-slate-600 dark:text-slate-400 mb-4 font-medium">
            Upload a photo from your device:
          </p>
          <div className="relative">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
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
        </div>
      </div>
    );
  }

  // IMAGE CAPTURED: Show preview
  if (capturedImage) {
    return (
      <div className="w-full max-w-2xl mx-auto space-y-4">
        <div className="rounded-2xl overflow-hidden shadow-xl border-2 border-gray-200 dark:border-slate-700">
          <img
            src={capturedImage}
            alt="Captured"
            className="w-full h-auto block"
          />
        </div>

        <div className="flex gap-3">
          <button
            onClick={resetCapture}
            className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 dark:from-blue-700 dark:to-cyan-700 dark:hover:from-blue-800 dark:hover:to-cyan-800 text-white font-bold py-3 px-4 rounded-xl transition shadow-lg hover:shadow-xl active:scale-95"
          >
            🔄 Retake Photo
          </button>
          <button
            onClick={() => setCapturedImage(null)}
            className="flex-1 bg-slate-500 hover:bg-slate-600 dark:bg-slate-600 dark:hover:bg-slate-700 text-white font-bold py-3 px-4 rounded-xl transition shadow-lg"
          >
            🗑️ Clear
          </button>
        </div>
      </div>
    );
  }

  // CAMERA ACTIVE: Show video stream with guidance overlay
  if (isStreaming) {
    return (
      <div className="w-full max-w-2xl mx-auto space-y-4">
        <div className="relative bg-black rounded-2xl overflow-hidden shadow-xl border-2 border-gray-200 dark:border-slate-700 aspect-video">
          {/* Video Stream */}
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
          />

          {/* Guidance Overlay */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            {/* Circle Mask Guide */}
            <div className="relative w-64 h-64 sm:w-72 sm:h-72">
              {/* Outer circle border */}
              <div className="absolute inset-0 rounded-full border-4 border-cyan-400/60 shadow-[0_0_20px_rgba(34,211,238,0.4)]" />

              {/* Inner circle (center guide) */}
              <div className="absolute inset-8 rounded-full border-2 border-cyan-400/30" />

              {/* Corner guides */}
              <div className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-cyan-400/60" />
              <div className="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-cyan-400/60" />
              <div className="absolute bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-cyan-400/60" />
              <div className="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-cyan-400/60" />
            </div>
          </div>

          {/* Lighting Status Badge */}
          <div className="absolute top-4 right-4 pointer-events-none">
            <div
              className={`px-4 py-2 rounded-full font-semibold text-sm flex items-center gap-2 backdrop-blur-sm ${
                lightingState === "good"
                  ? "bg-green-500/80 text-white"
                  : lightingState === "poor"
                  ? "bg-orange-500/80 text-white"
                  : "bg-gray-500/60 text-white"
              }`}
            >
              {lightingState === "good" && (
                <>
                  <span className="text-lg">✅</span>
                  <span>GOOD LIGHT</span>
                </>
              )}
              {lightingState === "poor" && (
                <>
                  <span className="text-lg">💡</span>
                  <span>NEED MORE LIGHT</span>
                </>
              )}
              {lightingState === "unknown" && (
                <>
                  <span className="text-lg">🔍</span>
                  <span>Analyzing</span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="flex gap-3">
          <button
            onClick={capturePhoto}
            disabled={isCapturing}
            className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 dark:from-green-700 dark:to-emerald-700 dark:hover:from-green-800 dark:hover:to-emerald-800 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-4 px-4 rounded-xl transition shadow-lg hover:shadow-xl active:scale-95 flex items-center justify-center gap-2"
          >
            {isCapturing ? (
              <>
                <span className="inline-block animate-spin">⏳</span>
                Capturing...
              </>
            ) : (
              <>
                <span>📸</span>
                <span>Capture Photo</span>
              </>
            )}
          </button>
          <button
            onClick={stopCamera}
            disabled={isCapturing}
            className="flex-1 bg-slate-500 hover:bg-slate-600 dark:bg-slate-600 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-4 px-4 rounded-xl transition shadow-lg"
          >
            ✕ Cancel
          </button>
        </div>

        {/* File Upload Fallback */}
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
            className="w-full border-2 border-dashed border-slate-400 dark:border-slate-600 hover:border-blue-600 dark:hover:border-cyan-400 text-slate-700 dark:text-slate-300 hover:text-blue-600 dark:hover:text-cyan-400 font-semibold py-3 px-4 rounded-xl transition"
          >
            📁 Choose from Gallery
          </button>
        </div>
      </div>
    );
  }

  // INITIAL STATE: Camera not started
  return (
    <div className="w-full max-w-2xl mx-auto space-y-4">
      <button
        onClick={startCamera}
        className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 dark:from-blue-700 dark:to-cyan-700 dark:hover:from-blue-800 dark:hover:to-cyan-800 text-white font-bold py-4 px-6 rounded-xl transition shadow-lg hover:shadow-xl active:scale-95 flex items-center justify-center gap-2"
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
    </div>
  );
}
