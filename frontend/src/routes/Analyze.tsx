import { useState } from "react";
import { useNavigate } from "react-router-dom";
import CameraCapture from "../components/CameraCapture";
import ResultCard from "../components/ResultCard";
import { useAuth } from "../context/useAuth";

export default function Analyze() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuth();
  const navigate = useNavigate();

  const handleCapture = async (file: File) => {
    if (!token) {
      navigate("/login");
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("image", file);

      const apiUrl =
        import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
      const response = await fetch(apiUrl + "/api/v1/analyze/image", {
        method: "POST",
        headers: {
          Authorization: "Bearer " + token,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Analysis failed");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Unknown error";
      console.error("Analysis error:", err);
      setError(errorMsg);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleRecommend = () => {
    console.log("Recommendations requested for analysis");
  };

  return (
    <div className="w-full py-8 md:py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 dark:from-blue-400 dark:to-cyan-400 bg-clip-text text-transparent mb-2">
            Analyze Your Photo
          </h1>
          <p className="text-gray-600 dark:text-gray-300 text-lg">
            Upload or capture a photo of your skin or hair for AI analysis
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Result Card Modal */}
            {result && (
              <ResultCard
                data={result}
                onClose={() => setResult(null)}
                onRecommend={handleRecommend}
              />
            )}

            {!result ? (
              <>
                {/* Camera Capture Component */}
                <CameraCapture onCapture={handleCapture} />

                {/* Loading State */}
                {isAnalyzing && (
                  <div className="bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-600 dark:border-blue-400 p-6 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-blue-400"></div>
                      <div>
                        <p className="font-semibold text-blue-900 dark:text-blue-200">
                          Analyzing your photo...
                        </p>
                        <p className="text-sm text-blue-800 dark:text-blue-300">
                          This may take a few seconds
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Error State */}
                {error && (
                  <div className="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-600 dark:border-red-400 p-4 rounded-lg">
                    <p className="text-red-900 dark:text-red-200 font-semibold">
                      ❌ Analysis Failed
                    </p>
                    <p className="text-red-800 dark:text-red-300 text-sm mt-1">
                      {error}
                    </p>
                    <button
                      onClick={() => setError(null)}
                      className="mt-3 text-red-700 dark:text-red-300 hover:text-red-900 dark:hover:text-red-100 font-medium text-sm"
                    >
                      Dismiss
                    </button>
                  </div>
                )}
              </>
            ) : (
              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={() => setResult(null)}
                  className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-semibold py-3 px-6 rounded-lg transition shadow-lg"
                >
                  🔄 Analyze Another Photo
                </button>
                <button
                  onClick={() => navigate("/dashboard")}
                  className="flex-1 bg-white/80 dark:bg-white/10 hover:bg-white/90 dark:hover:bg-white/20 text-gray-800 dark:text-white font-semibold py-3 px-6 rounded-lg transition border border-white/20 dark:border-white/10"
                >
                  📊 Back to Dashboard
                </button>
              </div>
            )}
          </div>

          {/* Tips Section - Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 border border-amber-200 dark:border-amber-800/50 rounded-lg p-6 sticky top-20">
              <h3 className="text-lg font-bold text-amber-900 dark:text-amber-200 mb-4 flex items-center gap-2">
                <span className="text-2xl">💡</span>
                Photography Tips
              </h3>

              <div className="space-y-4">
                {/* Lighting Tip */}
                <div className="bg-white/50 dark:bg-white/5 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <span className="text-2xl flex-shrink-0">☀️</span>
                    <div>
                      <h4 className="font-semibold text-amber-900 dark:text-amber-200 mb-1">
                        Good Lighting
                      </h4>
                      <p className="text-sm text-amber-800 dark:text-amber-300">
                        Use natural daylight or bright indoor lighting. Avoid
                        shadows on your face.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Distance Tip */}
                <div className="bg-white/50 dark:bg-white/5 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <span className="text-2xl flex-shrink-0">📏</span>
                    <div>
                      <h4 className="font-semibold text-amber-900 dark:text-amber-200 mb-1">
                        Proper Distance
                      </h4>
                      <p className="text-sm text-amber-800 dark:text-amber-300">
                        Keep the camera 6-12 inches away from your face for
                        accurate analysis.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Makeup Tip */}
                <div className="bg-white/50 dark:bg-white/5 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <span className="text-2xl flex-shrink-0">🚫</span>
                    <div>
                      <h4 className="font-semibold text-amber-900 dark:text-amber-200 mb-1">
                        Clean Skin
                      </h4>
                      <p className="text-sm text-amber-800 dark:text-amber-300">
                        For best results, avoid heavy makeup or filters that
                        obscure your skin.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Head Position Tip */}
                <div className="bg-white/50 dark:bg-white/5 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <span className="text-2xl flex-shrink-0">📸</span>
                    <div>
                      <h4 className="font-semibold text-amber-900 dark:text-amber-200 mb-1">
                        Face the Camera
                      </h4>
                      <p className="text-sm text-amber-800 dark:text-amber-300">
                        Position your face directly toward the camera for better
                        detection.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Hair Tips */}
                <div className="bg-white/50 dark:bg-white/5 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <span className="text-2xl flex-shrink-0">💇</span>
                    <div>
                      <h4 className="font-semibold text-amber-900 dark:text-amber-200 mb-1">
                        Hair Analysis
                      </h4>
                      <p className="text-sm text-amber-800 dark:text-amber-300">
                        Pull hair back or use a full-face photo for better
                        hair-type detection.
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Info Box */}
              <div className="mt-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <p className="text-xs text-blue-900 dark:text-blue-300">
                  <strong>💬 Tip:</strong> Better photos lead to more accurate
                  analysis and better recommendations!
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
