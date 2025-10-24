import React, { useEffect, useRef, useState } from "react";

type Props = {
  onCapture: (base64: string) => void;
};

export default function CameraCapture({ onCapture }: Props) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [lightHint, setLightHint] = useState("");

  useEffect(() => {
    let stream: MediaStream | null = null;

    async function startCamera() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "environment" },
          audio: false,
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          // Don't await play() - it can be interrupted. Just call it.
          videoRef.current.play().catch((err) => {
            console.warn("Video play() call interrupted or failed:", err);
            // This is usually not critical - video will play automatically
          });
        }
      } catch (err: any) {
        console.error("camera error", err);
        setError(err?.message || "Unable to access camera");
        if (
          err &&
          (err.name === "NotAllowedError" ||
            err.name === "PermissionDeniedError")
        ) {
          setPermissionDenied(true);
        }
      }
    }

    startCamera();

    const interval = setInterval(() => {
      evaluateLighting();
    }, 1000);

    return () => {
      clearInterval(interval);
      if (stream) {
        stream.getTracks().forEach((t) => t.stop());
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const evaluateLighting = () => {
    try {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      if (!video || !canvas) return;

      const w = video.videoWidth;
      const h = video.videoHeight;
      if (!w || !h) return;

      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      // sample a centered square region
      const size = Math.min(w, h) * 0.4;
      const sx = (w - size) / 2;
      const sy = (h - size) / 2;
      ctx.drawImage(video, 0, 0, w, h);
      const imageData = ctx.getImageData(sx, sy, size, size);
      let total = 0;
      for (let i = 0; i < imageData.data.length; i += 4) {
        // luminance
        const r = imageData.data[i];
        const g = imageData.data[i + 1];
        const b = imageData.data[i + 2];
        const lum = 0.2126 * r + 0.7152 * g + 0.0722 * b;
        total += lum;
      }
      const avg = total / (imageData.data.length / 4);
      if (avg > 90) {
        setLightHint("GOOD LIGHT");
      } else if (avg > 50) {
        setLightHint("Move closer / More light");
      } else {
        setLightHint("Too dark — add light");
      }
    } catch (e) {
      // ignore
    }
  };

  const handleCapture = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;

    const w = video.videoWidth;
    const h = video.videoHeight;
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, w, h);
    const dataUrl = canvas.toDataURL("image/jpeg", 0.9);
    onCapture(dataUrl);
  };

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files && e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const base64 = reader.result as string;
      onCapture(base64);
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="w-full max-w-xl mx-auto">
      <div className="relative bg-black rounded overflow-hidden">
        <video
          ref={videoRef}
          className="w-full h-auto object-cover"
          playsInline
          autoPlay
          muted
        />

        {/* circular overlay */}
        <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
          <div className="w-56 h-56 rounded-full border-4 border-white/60 shadow-lg"></div>
        </div>

        {/* top hint */}
        <div className="absolute top-2 left-2 text-white text-sm bg-black/40 px-2 py-1 rounded">
          {lightHint}
        </div>

        {/* canvas for internal processing (hidden) */}
        <canvas ref={canvasRef} className="hidden" />
      </div>

      <div className="mt-3 flex items-center justify-between">
        <div className="text-sm text-gray-600">
          {permissionDenied ? "Camera access denied" : ""}
        </div>
        <div className="flex items-center gap-2">
          <label className="bg-white border px-3 py-2 rounded cursor-pointer text-sm">
            Upload
            <input
              type="file"
              accept="image/*"
              onChange={handleFile}
              className="hidden"
            />
          </label>
          <button
            onClick={handleCapture}
            className="bg-indigo-600 text-white px-4 py-2 rounded shadow hover:bg-indigo-700"
          >
            Capture
          </button>
        </div>
      </div>

      {error && (
        <div className="mt-2 text-sm text-red-600">
          {permissionDenied ? (
            <>
              Camera permission denied. Please allow camera access or upload an
              image using the Upload button.
            </>
          ) : (
            <>{error}</>
          )}
        </div>
      )}
    </div>
  );
}
