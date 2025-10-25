import { useState } from "react";
import CameraCapture from "../components/CameraCapture";
import AnalysisCard from "../components/AnalysisCard";

type Analysis = {
  skin_type: string;
  hair_type: string;
  conditions_detected: string[];
  confidence_scores: Record<string, number>;
};

// API Configuration
const API_BASE = (() => {
  const envUrl = (import.meta as any).env.VITE_API_URL;
  if (envUrl) return envUrl;
  return "http://" + window.location.hostname + ":8000/api/v1";
})();

/**
 * Resize image to reduce payload size while maintaining quality
 * @param file - Original image file
 * @param maxWidth - Maximum width (default: 1024px)
 * @param maxHeight - Maximum height (default: 1024px)
 * @param quality - JPEG quality (default: 0.9)
 * @returns Promise resolving to resized File
 */
async function resizeImage(
  file: File,
  maxWidth: number = 1024,
  maxHeight: number = 1024,
  quality: number = 0.9
): Promise<File> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = (event) => {
      const img = new Image();
      img.src = event.target?.result as string;
      img.onload = () => {
        const canvas = document.createElement("canvas");
        let width = img.width;
        let height = img.height;

        // Calculate new dimensions maintaining aspect ratio
        if (width > height) {
          if (width > maxWidth) {
            height = Math.round((height * maxWidth) / width);
            width = maxWidth;
          }
        } else {
          if (height > maxHeight) {
            width = Math.round((width * maxHeight) / height);
            height = maxHeight;
          }
        }

        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext("2d");
        if (!ctx) {
          reject(new Error("Failed to get canvas context"));
          return;
        }

        ctx.drawImage(img, 0, 0, width, height);
        canvas.toBlob(
          (blob) => {
            if (!blob) {
              reject(new Error("Failed to create blob"));
              return;
            }
            const resizedFile = new File([blob], file.name, {
              type: "image/jpeg",
              lastModified: Date.now(),
            });
            resolve(resizedFile);
          },
          "image/jpeg",
          quality
        );
      };
      img.onerror = () => reject(new Error("Failed to load image"));
    };
    reader.onerror = () => reject(new Error("Failed to read file"));
  });
}

/**
 * Analyze image by sending to backend API
 * Automatically resizes image to keep payload < 2MB
 * @param file - Image file to analyze
 * @returns Promise resolving to analysis results
 */
async function analyzeImageFile(file: File) {
  // Resize image to optimize payload size
  const optimizedFile = await resizeImage(file);
  console.log(
    `Image resized: ${(file.size / 1024 / 1024).toFixed(2)}MB → ${(
      optimizedFile.size /
      1024 /
      1024
    ).toFixed(2)}MB`
  );

  const form = new FormData();
  // Note: Do NOT set Content-Type header for FormData
  // Browser will automatically set multipart/form-data with correct boundary
  form.append("image", optimizedFile);

  const response = await fetch(`${API_BASE}/analyze/image`, {
    method: "POST",
    body: form,
    // Do NOT include Content-Type header - browser handles it
    headers: {
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData?.detail ||
        errorData?.error ||
        `HTTP ${response.status}: ${response.statusText}`
    );
  }

  return response.json();
}

export default function Capture() {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onCapture = async (file: File) => {
    setLoading(true);
    setError(null);
    const sep = "=".repeat(50);
    console.log(sep, "CAPTURE START", sep);
    try {
      console.log("1. File received:", file.name);
      console.log("   Size:", (file.size / 1024 / 1024).toFixed(2), "MB");
      console.log("   Type:", file.type);

      console.log("2. Analyzing image...");
      const json = await analyzeImageFile(file);

      console.log("3. Analysis complete!");
      console.log("   Result:", json);
      console.log(sep, "CAPTURE SUCCESS", sep);
      setAnalysis(json);
    } catch (err: any) {
      console.error("ERROR CAUGHT:", err);
      console.error("   Error message:", err.message);
      console.log(sep, "CAPTURE FAILED", sep);
      const errorMsg = err?.message || String(err) || "Unknown error";
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = () => {
    alert("Saved to history (stub)");
  };

  const handleRecommend = () => {
    alert("Get recommendation (stub)");
  };

  return (
    <div className="w-full py-8 md:py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 dark:from-blue-400 dark:to-cyan-400 bg-clip-text text-transparent mb-2">
            Capture & Analyze
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Take photos or upload images for AI analysis
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-100 dark:bg-red-900/30 border-l-4 border-red-600 dark:border-red-400 rounded-lg flex items-start gap-3">
            <span className="text-2xl flex-shrink-0">⚠️</span>
            <div>
              <p className="font-semibold text-red-800 dark:text-red-200">
                Analysis Failed
              </p>
              <p className="text-red-700 dark:text-red-300 text-sm mt-1">
                {error}
              </p>
            </div>
          </div>
        )}

        {/* Content Area */}
        {!analysis && (
          <div className="bg-white/80 dark:bg-white/10 backdrop-blur-md rounded-xl shadow-lg p-8 border border-white/20 dark:border-white/10">
            <CameraCapture onCapture={onCapture} />

            {loading && (
              <div className="mt-6 text-center">
                <div className="inline-block">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400"></div>
                </div>
                <p className="text-gray-600 dark:text-gray-300 mt-4">
                  Analyzing your photo...
                </p>
              </div>
            )}
          </div>
        )}

        {/* Analysis Results */}
        {analysis && (
          <div className="mt-8">
            <div className="bg-white/80 dark:bg-white/10 backdrop-blur-md rounded-xl shadow-lg p-8 border border-white/20 dark:border-white/10 mb-6">
              <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-6">
                ✅ Analysis Results
              </h2>
              <AnalysisCard
                analysis={analysis}
                onSave={handleSave}
                onRecommend={handleRecommend}
              />
            </div>

            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={() => {
                  setAnalysis(null);
                  setError(null);
                }}
                className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-semibold py-3 px-6 rounded-lg transition shadow-lg"
              >
                🔄 Analyze Another
              </button>
              <button
                onClick={() => window.history.back()}
                className="flex-1 bg-white/80 dark:bg-white/10 hover:bg-white/90 dark:hover:bg-white/20 text-gray-800 dark:text-white font-semibold py-3 px-6 rounded-lg transition border border-white/20 dark:border-white/10"
              >
                ← Back
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
