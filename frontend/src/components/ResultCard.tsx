interface AnalysisResult {
  skin_type?: string;
  hair_type?: string;
  conditions_detected?: string[];
  confidence_scores?: {
    skin_type?: number;
    hair_type?: number;
  };
  model_version?: string;
  status?: string;
  analysis_id?: number;
  photo_id?: number;
}

interface ResultCardProps {
  data: AnalysisResult;
  onClose: () => void;
  onRecommend?: () => void;
}

import { useState } from "react";
import * as api from "../lib/api";
import type { RecommendationsResponse } from "../lib/api";
import RecommendationsDisplay from "./RecommendationsDisplay";

export default function ResultCard({
  data,
  onClose,
  onRecommend,
}: ResultCardProps) {
  const [recommendations, setRecommendations] =
    useState<RecommendationsResponse | null>(null);
  const [loadingRecs, setLoadingRecs] = useState(false);
  const [recError, setRecError] = useState<string | null>(null);
  const [savedToHistory, setSavedToHistory] = useState(false);

  const handleGetRecommendations = async () => {
    if (!data.analysis_id) {
      setRecError("Analysis ID not available");
      return;
    }
    try {
      setLoadingRecs(true);
      setRecError(null);
      const recs = await api.getRecommendations(data.analysis_id);
      setRecommendations(recs);
      // Call optional onRecommend callback
      onRecommend?.();
    } catch (err) {
      setRecError(
        err instanceof Error ? err.message : "Failed to fetch recommendations"
      );
    } finally {
      setLoadingRecs(false);
    }
  };

  const handleSaveToHistory = async () => {
    try {
      setSavedToHistory(true);
      // TODO: Implement save to history functionality
      // This could call an API endpoint or store locally
      console.log("Saving analysis to history:", data);
    } catch (err) {
      console.error("Failed to save to history:", err);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-gradient-to-r from-indigo-600 to-purple-600 p-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-white">Analysis Results</h2>
          <button
            onClick={onClose}
            className="text-white hover:text-gray-200 text-2xl font-bold"
          >
            ✕
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Disclaimer */}
          <div className="bg-amber-50 border-l-4 border-amber-500 p-4 rounded">
            <p className="text-sm text-amber-900">
              <strong>⚠️ Disclaimer:</strong> These results are for
              informational purposes only and should not be considered medical
              advice. Please consult a dermatologist or healthcare professional
              for personalized skincare and health recommendations.
            </p>
          </div>
          {/* Skin Type */}
          {data.skin_type && (
            <div className="border-b pb-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Skin Type
              </h3>
              <div className="flex items-center gap-3">
                <span className="text-3xl">🧴</span>
                <div>
                  <p className="text-2xl font-bold text-indigo-600 capitalize">
                    {data.skin_type}
                  </p>
                  {data.confidence_scores?.skin_type && (
                    <p className="text-sm text-gray-600">
                      Confidence:{" "}
                      {(data.confidence_scores.skin_type * 100).toFixed(1)}%
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Hair Type */}
          {data.hair_type && (
            <div className="border-b pb-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Hair Type
              </h3>
              <div className="flex items-center gap-3">
                <span className="text-3xl">💇</span>
                <div>
                  <p className="text-2xl font-bold text-purple-600 capitalize">
                    {data.hair_type}
                  </p>
                  {data.confidence_scores?.hair_type && (
                    <p className="text-sm text-gray-600">
                      Confidence:{" "}
                      {(data.confidence_scores.hair_type * 100).toFixed(1)}%
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Conditions Detected */}
          {data.conditions_detected && data.conditions_detected.length > 0 && (
            <div className="border-b pb-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Conditions Detected
              </h3>
              <div className="flex flex-wrap gap-2">
                {data.conditions_detected.map((condition, idx) => (
                  <span
                    key={idx}
                    className="inline-block bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium"
                  >
                    {condition}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Confidence Scores */}
          {data.confidence_scores && (
            <div className="border-b pb-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Confidence Scores
              </h3>
              <div className="space-y-2">
                {data.confidence_scores.skin_type && (
                  <div>
                    <p className="text-sm text-gray-700">Skin Type</p>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-indigo-600 h-2 rounded-full"
                        style={{
                          width: `${data.confidence_scores.skin_type * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                )}
                {data.confidence_scores.hair_type && (
                  <div>
                    <p className="text-sm text-gray-700">Hair Type</p>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-purple-600 h-2 rounded-full"
                        style={{
                          width: `${data.confidence_scores.hair_type * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Model Info */}
          {data.model_version && (
            <div className="text-xs text-gray-500 italic">
              Model: {data.model_version}
            </div>
          )}

          {/* Get Recommendations Button */}
          {!recommendations && (
            <div className="flex gap-3">
              <button
                onClick={handleGetRecommendations}
                disabled={loadingRecs || !data.analysis_id}
                className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-semibold py-3 rounded-lg transition disabled:opacity-50"
              >
                {loadingRecs
                  ? "Loading Recommendations..."
                  : "Get Recommendations"}
              </button>
              <button
                onClick={handleSaveToHistory}
                disabled={savedToHistory}
                className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-semibold py-3 rounded-lg transition disabled:opacity-50"
              >
                {savedToHistory ? "✓ Saved to History" : "Save to History"}
              </button>
            </div>
          )}

          {/* Recommendations Display */}
          {recError && (
            <div className="p-3 bg-yellow-100 text-yellow-800 rounded-lg text-sm">
              ⚠️ {recError}
            </div>
          )}

          {recommendations && (
            <div className="border-t pt-6">
              <RecommendationsDisplay
                data={recommendations}
                onClear={() => setRecommendations(null)}
              />
            </div>
          )}

          {/* Raw JSON */}
          <details className="bg-gray-100 rounded p-3">
            <summary className="cursor-pointer font-semibold text-gray-700">
              Raw JSON Data
            </summary>
            <pre className="mt-2 text-xs overflow-auto max-h-48 bg-gray-900 text-gray-100 p-3 rounded">
              {JSON.stringify(data, null, 2)}
            </pre>
          </details>

          {/* Close Button */}
          <button
            onClick={onClose}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 rounded-lg transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
