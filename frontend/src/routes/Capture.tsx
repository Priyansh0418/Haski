import { useState } from "react";
import CameraCapture from "../components/CameraCapture";
import AnalysisCard from "../components/AnalysisCard";

type Analysis = {
  skin_type: string;
  hair_type: string;
  conditions_detected: string[];
  confidence_scores: Record<string, number>;
};

const API_BASE = (() => {
  const envUrl = (import.meta as any).env.VITE_API_URL;
  if (envUrl) return envUrl;
  return "http://" + window.location.hostname + ":8000";
})();

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
      console.log("1. File received:", file);
      console.log("   Name:", file.name);
      console.log("   Size:", file.size, "bytes");
      console.log("   Type:", file.type);

      const form = new FormData();
      form.append("image", file);
      console.log("2. FormData created with image field");

      const url = API_BASE + "/api/v1/analyze/image";
      console.log("3. API_BASE config:", API_BASE);
      console.log("4. Full URL:", url);
      console.log("5. Fetching with 60s timeout...");

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000);

      const resp = await fetch(url, {
        method: "POST",
        body: form,
        headers: {
          Accept: "application/json",
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      console.log("6. Response received!");
      console.log("   Status:", resp.status);
      console.log("   Status text:", resp.statusText);
      console.log("   Headers:", {
        "content-type": resp.headers.get("content-type"),
        "content-length": resp.headers.get("content-length"),
      });

      console.log("7. Reading response body...");
      let json: any;
      try {
        json = await resp.json();
        console.log("   Response JSON parsed:", json);
      } catch (parseErr) {
        console.error("   Failed to parse JSON:", parseErr);
        throw new Error("Failed to parse response: " + String(parseErr));
      }

      if (!resp.ok) {
        console.log("8. Response NOT OK, throwing error...");
        const errorMsg = json?.detail || json?.error || "HTTP " + resp.status;
        console.error("   Error message:", errorMsg);
        throw new Error(errorMsg);
      }

      console.log("8. Success! Analysis result:", json);
      console.log(sep, "CAPTURE SUCCESS", sep);
      setAnalysis(json);
    } catch (err: any) {
      console.error("ERROR CAUGHT:", err);
      console.error("   Error type:", err.constructor.name);
      console.error("   Error message:", err.message);
      console.error("   Full error:", err);
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
