import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import * as api from "../lib/api";
import type { RecommendationsResponse } from "../lib/api";
import { useAuth } from "../context/useAuth";

export default function Recommendations() {
  const location = useLocation();
  const navigate = useNavigate();
  const { token } = useAuth();

  const [recommendations, setRecommendations] =
    useState<RecommendationsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<"helpful" | "not-helpful" | null>(
    null
  );
  const [feedbackSent, setFeedbackSent] = useState(false);

  // Get analysis from location state (passed from Analyze page)
  const analysisData = location.state?.result || location.state?.analysis;
  const analysisId = analysisData?.analysis_id || analysisData?.id;

  // Fetch recommendations on mount if we have analysis data
  useEffect(() => {
    if (analysisId && !recommendations) {
      fetchRecommendations();
    }
  }, [analysisId, recommendations]);

  const fetchRecommendations = async () => {
    if (!analysisId) {
      setError("No analysis data available");
      return;
    }

    if (!token) {
      navigate("/login");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await api.getRecommendations(analysisId);
      setRecommendations(data);
    } catch (err) {
      const errorMsg =
        err instanceof Error ? err.message : "Failed to fetch recommendations";
      setError(errorMsg);
      console.error("Error fetching recommendations:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (helpful: boolean) => {
    if (!recommendations || feedbackSent) return;

    setFeedback(helpful ? "helpful" : "not-helpful");

    try {
      await api.postFeedback(
        recommendations.recommendation_id,
        helpful ? 5 : 1,
        helpful
          ? "These recommendations were helpful!"
          : "These recommendations were not helpful."
      );
      setFeedbackSent(true);
    } catch (err) {
      console.error("Error submitting feedback:", err);
    }
  };

  // Show upload/no data state
  if (!analysisId) {
    return (
      <div className="w-full py-12 md:py-16">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 border-2 border-blue-200 dark:border-blue-800 rounded-xl shadow-lg p-8 md:p-12 text-center">
            <div className="text-6xl mb-4">🔍</div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
              No Analysis Available
            </h2>
            <p className="text-gray-700 dark:text-gray-300 mb-6 text-lg">
              To get personalized recommendations, please start by analyzing a
              photo of your skin or hair.
            </p>
            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={() => navigate("/analyze")}
                className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-semibold py-3 px-6 rounded-lg transition shadow-lg"
              >
                📸 Start Analysis
              </button>
              <button
                onClick={() => navigate("/dashboard")}
                className="flex-1 bg-white/80 dark:bg-white/10 hover:bg-white/90 dark:hover:bg-white/20 text-gray-800 dark:text-white font-semibold py-3 px-6 rounded-lg transition border border-blue-200 dark:border-blue-800"
              >
                ← Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Loading state
  if (loading) {
    return (
      <div className="w-full py-12 md:py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-block">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400 mx-auto"></div>
          </div>
          <p className="text-gray-600 dark:text-gray-300 mt-4 text-lg">
            Loading personalized recommendations...
          </p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="w-full py-12 md:py-16">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-600 dark:border-red-400 p-6 rounded-lg">
            <h2 className="text-xl font-bold text-red-900 dark:text-red-200 mb-2">
              ❌ Failed to Load Recommendations
            </h2>
            <p className="text-red-800 dark:text-red-300 mb-4">{error}</p>
            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={fetchRecommendations}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition"
              >
                🔄 Retry
              </button>
              <button
                onClick={() => navigate("/analyze")}
                className="flex-1 bg-white/80 dark:bg-white/10 hover:bg-white/90 dark:hover:bg-white/20 text-gray-800 dark:text-white font-semibold py-2 px-4 rounded-lg transition border"
              >
                ← Go Back
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Success state - show recommendations
  if (!recommendations) {
    return null;
  }

  const hasEscalation =
    recommendations.escalation && recommendations.escalation.level !== "none";

  return (
    <div className="w-full py-8 md:py-12">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 dark:from-green-400 dark:to-emerald-400 bg-clip-text text-transparent mb-2">
            ✨ Personalized Recommendations
          </h1>
          <p className="text-gray-600 dark:text-gray-300 text-lg">
            Based on your skin and hair analysis
          </p>
        </div>

        {/* Escalation Alert Banner */}
        {hasEscalation && (
          <div
            className={`border-l-4 rounded-lg p-6 ${
              recommendations.escalation?.level === "emergency" ||
              recommendations.escalation?.level === "urgent"
                ? "bg-red-50 dark:bg-red-900/20 border-red-600 dark:border-red-400"
                : "bg-yellow-50 dark:bg-yellow-900/20 border-yellow-600 dark:border-yellow-400"
            }`}
          >
            <div className="flex items-start gap-4">
              <div className="text-3xl flex-shrink-0">
                {recommendations.escalation?.level === "emergency"
                  ? "🚨"
                  : recommendations.escalation?.level === "urgent"
                  ? "⚠️"
                  : "⚡"}
              </div>
              <div className="flex-1">
                <h3
                  className={`font-bold text-lg mb-2 ${
                    recommendations.escalation?.level === "emergency" ||
                    recommendations.escalation?.level === "urgent"
                      ? "text-red-900 dark:text-red-200"
                      : "text-yellow-900 dark:text-yellow-200"
                  }`}
                >
                  {recommendations.escalation?.level === "emergency"
                    ? "Medical Attention Needed"
                    : recommendations.escalation?.level === "urgent"
                    ? "Important: Consult a Dermatologist"
                    : "Caution: Consider Professional Advice"}
                </h3>
                <p
                  className={
                    recommendations.escalation?.level === "emergency" ||
                    recommendations.escalation?.level === "urgent"
                      ? "text-red-800 dark:text-red-300"
                      : "text-yellow-800 dark:text-yellow-300"
                  }
                >
                  {recommendations.escalation?.message}
                </p>
                {recommendations.escalation?.see_dermatologist && (
                  <p className="text-sm mt-3 font-semibold">
                    🏥 Please schedule an appointment with a dermatologist for
                    professional diagnosis and treatment.
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Daily Routine Section */}
        {recommendations.routines && recommendations.routines.length > 0 && (
          <div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
              <span className="text-4xl">🔄</span>
              Daily Routine
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Morning Routine */}
              {recommendations.routines.some((r) =>
                r.name?.toLowerCase().includes("morning")
              ) && (
                <div className="bg-gradient-to-br from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 border-2 border-yellow-200 dark:border-yellow-800 rounded-xl overflow-hidden shadow-lg hover:shadow-xl transition">
                  <div className="bg-gradient-to-r from-yellow-400 to-orange-400 px-6 py-4">
                    <h3 className="text-2xl font-bold text-white flex items-center gap-2">
                      <span>🌅</span>
                      Morning Routine
                    </h3>
                  </div>
                  <div className="p-6 space-y-4">
                    {recommendations.routines
                      .filter((r) => r.name?.toLowerCase().includes("morning"))
                      .map((routine, idx) => (
                        <div key={idx}>
                          {routine.description && (
                            <p className="text-gray-700 dark:text-gray-300 mb-3">
                              {routine.description}
                            </p>
                          )}
                          {routine.steps && routine.steps.length > 0 && (
                            <ol className="space-y-2 ml-4">
                              {routine.steps.map((step, stepIdx) => (
                                <li
                                  key={stepIdx}
                                  className="text-gray-700 dark:text-gray-300 flex items-start gap-2"
                                >
                                  <span className="font-bold text-yellow-600 dark:text-yellow-400 flex-shrink-0">
                                    {stepIdx + 1}.
                                  </span>
                                  <span>{step}</span>
                                </li>
                              ))}
                            </ol>
                          )}
                          {routine.frequency && (
                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-3 italic">
                              📍 Frequency: {routine.frequency}
                            </p>
                          )}
                        </div>
                      ))}
                  </div>
                </div>
              )}

              {/* Evening Routine */}
              {recommendations.routines.some((r) =>
                r.name?.toLowerCase().includes("evening")
              ) && (
                <div className="bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 border-2 border-indigo-200 dark:border-indigo-800 rounded-xl overflow-hidden shadow-lg hover:shadow-xl transition">
                  <div className="bg-gradient-to-r from-indigo-400 to-purple-400 px-6 py-4">
                    <h3 className="text-2xl font-bold text-white flex items-center gap-2">
                      <span>🌙</span>
                      Evening Routine
                    </h3>
                  </div>
                  <div className="p-6 space-y-4">
                    {recommendations.routines
                      .filter((r) => r.name?.toLowerCase().includes("evening"))
                      .map((routine, idx) => (
                        <div key={idx}>
                          {routine.description && (
                            <p className="text-gray-700 dark:text-gray-300 mb-3">
                              {routine.description}
                            </p>
                          )}
                          {routine.steps && routine.steps.length > 0 && (
                            <ol className="space-y-2 ml-4">
                              {routine.steps.map((step, stepIdx) => (
                                <li
                                  key={stepIdx}
                                  className="text-gray-700 dark:text-gray-300 flex items-start gap-2"
                                >
                                  <span className="font-bold text-indigo-600 dark:text-indigo-400 flex-shrink-0">
                                    {stepIdx + 1}.
                                  </span>
                                  <span>{step}</span>
                                </li>
                              ))}
                            </ol>
                          )}
                          {routine.frequency && (
                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-3 italic">
                              📍 Frequency: {routine.frequency}
                            </p>
                          )}
                        </div>
                      ))}
                  </div>
                </div>
              )}

              {/* Other Routines */}
              {recommendations.routines
                .filter(
                  (r) =>
                    !r.name?.toLowerCase().includes("morning") &&
                    !r.name?.toLowerCase().includes("evening")
                )
                .map((routine, idx) => (
                  <div
                    key={idx}
                    className="bg-gradient-to-br from-cyan-50 to-blue-50 dark:from-cyan-900/20 dark:to-blue-900/20 border-2 border-cyan-200 dark:border-cyan-800 rounded-xl overflow-hidden shadow-lg hover:shadow-xl transition"
                  >
                    <div className="bg-gradient-to-r from-cyan-400 to-blue-400 px-6 py-4">
                      <h3 className="text-2xl font-bold text-white">
                        {routine.name || "Routine"}
                      </h3>
                    </div>
                    <div className="p-6 space-y-4">
                      {routine.description && (
                        <p className="text-gray-700 dark:text-gray-300">
                          {routine.description}
                        </p>
                      )}
                      {routine.steps && routine.steps.length > 0 && (
                        <ol className="space-y-2 ml-4">
                          {routine.steps.map((step, stepIdx) => (
                            <li
                              key={stepIdx}
                              className="text-gray-700 dark:text-gray-300 flex items-start gap-2"
                            >
                              <span className="font-bold text-cyan-600 dark:text-cyan-400 flex-shrink-0">
                                {stepIdx + 1}.
                              </span>
                              <span>{step}</span>
                            </li>
                          ))}
                        </ol>
                      )}
                      {routine.frequency && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-3 italic">
                          📍 Frequency: {routine.frequency}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}

        {/* Products Section */}
        {recommendations.recommended_products &&
          recommendations.recommended_products.length > 0 && (
            <div>
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                <span className="text-4xl">🛍️</span>
                Recommended Products ({recommendations.product_count})
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {recommendations.recommended_products.map((product, idx) => (
                  <div
                    key={idx}
                    className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-2 border-green-200 dark:border-green-800 rounded-xl overflow-hidden shadow-lg hover:shadow-xl hover:scale-105 transition-transform"
                  >
                    <div className="bg-gradient-to-r from-green-400 to-emerald-400 px-4 py-3">
                      <h3 className="font-bold text-white text-lg">
                        {product.name || "Product"}
                      </h3>
                      {product.brand && (
                        <p className="text-green-100 text-sm">
                          by {product.brand}
                        </p>
                      )}
                    </div>
                    <div className="p-4 space-y-3">
                      {product.category && (
                        <span className="inline-block bg-green-200 dark:bg-green-800 text-green-900 dark:text-green-200 px-3 py-1 rounded-full text-xs font-semibold">
                          {product.category}
                        </span>
                      )}
                      {product.description && (
                        <p className="text-sm text-gray-700 dark:text-gray-300">
                          {product.description}
                        </p>
                      )}
                      {product.reason && (
                        <div className="bg-white/50 dark:bg-white/5 rounded-lg p-3 border border-green-200 dark:border-green-800">
                          <p className="text-xs text-gray-700 dark:text-gray-300">
                            <strong>Why:</strong> {product.reason}
                          </p>
                        </div>
                      )}
                      <div className="flex items-center justify-between pt-2">
                        {product.price && (
                          <span className="text-lg font-bold text-green-700 dark:text-green-300">
                            {product.price}
                          </span>
                        )}
                        {product.link && (
                          <a
                            href={product.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-green-600 hover:text-green-800 dark:text-green-400 dark:hover:text-green-200 font-semibold text-sm"
                          >
                            View →
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

        {/* Diet Section */}
        {recommendations.diet_recommendations &&
          recommendations.diet_recommendations.length > 0 && (
            <div>
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
                <span className="text-4xl">🥗</span>
                Diet Suggestions
              </h2>
              <div className="space-y-4">
                {recommendations.diet_recommendations.map((diet, idx) => (
                  <div
                    key={idx}
                    className="bg-gradient-to-r from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20 border-l-4 border-orange-500 dark:border-orange-400 rounded-lg p-4 hover:shadow-lg transition"
                  >
                    <div className="flex items-start gap-4">
                      <div className="text-3xl flex-shrink-0">🍎</div>
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-orange-900 dark:text-orange-200">
                          {diet.food}
                        </h3>
                        {diet.frequency && (
                          <p className="text-sm text-orange-800 dark:text-orange-300 mt-1">
                            <strong>Frequency:</strong> {diet.frequency}
                          </p>
                        )}
                        {diet.benefits && (
                          <p className="text-sm text-gray-700 dark:text-gray-300 mt-2">
                            <strong>Benefits:</strong> {diet.benefits}
                          </p>
                        )}
                        {diet.reason && (
                          <p className="text-sm text-gray-700 dark:text-gray-300 mt-2">
                            <strong>Why:</strong> {diet.reason}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

        {/* Warnings Section */}
        {recommendations.warnings && recommendations.warnings.length > 0 && (
          <div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
              <span className="text-4xl">⚠️</span>
              Important Warnings
            </h2>
            <div className="space-y-4">
              {recommendations.warnings.map((warning, idx) => (
                <div
                  key={idx}
                  className={`border-l-4 rounded-lg p-4 ${
                    warning.level === "urgent"
                      ? "bg-red-50 dark:bg-red-900/20 border-red-600 dark:border-red-400"
                      : warning.level === "warning"
                      ? "bg-yellow-50 dark:bg-yellow-900/20 border-yellow-600 dark:border-yellow-400"
                      : "bg-blue-50 dark:bg-blue-900/20 border-blue-600 dark:border-blue-400"
                  }`}
                >
                  <p
                    className={
                      warning.level === "urgent"
                        ? "text-red-900 dark:text-red-200 font-semibold"
                        : warning.level === "warning"
                        ? "text-yellow-900 dark:text-yellow-200 font-semibold"
                        : "text-blue-900 dark:text-blue-200"
                    }
                  >
                    {warning.message}
                  </p>
                  {warning.recommendation && (
                    <p className="text-sm text-gray-700 dark:text-gray-300 mt-2">
                      {warning.recommendation}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Applied Rules (Transparency) */}
        {recommendations.applied_rules &&
          recommendations.applied_rules.length > 0 && (
            <details className="bg-gray-100 dark:bg-gray-900 rounded-lg p-4">
              <summary className="cursor-pointer font-semibold text-gray-800 dark:text-gray-200">
                📋 Applied Rules ({recommendations.rules_count})
              </summary>
              <div className="mt-3 grid grid-cols-2 md:grid-cols-3 gap-2">
                {recommendations.applied_rules.map((rule, idx) => (
                  <span
                    key={idx}
                    className="bg-gray-200 dark:bg-gray-800 text-gray-800 dark:text-gray-200 px-3 py-1 rounded-full text-xs font-mono"
                  >
                    {rule}
                  </span>
                ))}
              </div>
            </details>
          )}

        {/* Feedback Section */}
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border-2 border-purple-200 dark:border-purple-800 rounded-xl p-6">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <span>💬</span>
            Was this helpful?
          </h3>
          <div className="flex gap-3">
            <button
              onClick={() => handleFeedback(true)}
              disabled={feedbackSent}
              className={`flex-1 font-semibold py-3 px-4 rounded-lg transition ${
                feedback === "helpful"
                  ? "bg-green-600 text-white"
                  : "bg-white dark:bg-gray-800 text-gray-800 dark:text-white hover:bg-green-100 dark:hover:bg-green-900/30"
              } ${feedbackSent ? "opacity-50 cursor-not-allowed" : ""}`}
            >
              👍{" "}
              {feedback === "helpful" ? "Thanks for feedback!" : "Yes, helpful"}
            </button>
            <button
              onClick={() => handleFeedback(false)}
              disabled={feedbackSent}
              className={`flex-1 font-semibold py-3 px-4 rounded-lg transition ${
                feedback === "not-helpful"
                  ? "bg-red-600 text-white"
                  : "bg-white dark:bg-gray-800 text-gray-800 dark:text-white hover:bg-red-100 dark:hover:bg-red-900/30"
              } ${feedbackSent ? "opacity-50 cursor-not-allowed" : ""}`}
            >
              👎 Not helpful
            </button>
          </div>
          {feedbackSent && (
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-3">
              ✓ Thank you for your feedback! It helps us improve
              recommendations.
            </p>
          )}
        </div>

        {/* Navigation Footer */}
        <div className="flex flex-col sm:flex-row gap-3 pt-8 border-t border-gray-200 dark:border-gray-800">
          <button
            onClick={() => navigate("/analyze")}
            className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-semibold py-3 px-6 rounded-lg transition shadow-lg"
          >
            📸 Analyze Another Photo
          </button>
          <button
            onClick={() => navigate("/dashboard")}
            className="flex-1 bg-white/80 dark:bg-white/10 hover:bg-white/90 dark:hover:bg-white/20 text-gray-800 dark:text-white font-semibold py-3 px-6 rounded-lg transition border border-gray-300 dark:border-gray-700"
          >
            📊 Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
}
