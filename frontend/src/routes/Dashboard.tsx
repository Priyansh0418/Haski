import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import * as api from "../lib/api";
import { useAuth } from "../context/useAuth";
import HistoryTrend from "../components/HistoryTrend";
import ReminderModal from "../components/ReminderModal";
import SettingsModal from "../components/SettingsModal";

interface AnalysisRecord {
  id?: number;
  date?: string;
  timestamp?: string;
  skin_type?: string;
  hair_type?: string;
  skin_score?: number;
  hair_score?: number;
  conditions_detected?: string[];
}

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [reminderModalOpen, setReminderModalOpen] = useState(false);
  const [settingsModalOpen, setSettingsModalOpen] = useState(false);
  const [lastAnalysis, setLastAnalysis] = useState<AnalysisRecord | null>(null);
  const [thisWeekCount, setThisWeekCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      // Fetch analysis history
      try {
        const history = await api.getAnalysisHistory();
        const analyses = Array.isArray(history)
          ? history
          : history.analyses || history.data || [];

        if (analyses.length > 0) {
          // Get last analysis
          setLastAnalysis(analyses[0]);

          // Count analyses from this week
          const oneWeekAgo = new Date();
          oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);

          const thisWeek = analyses.filter((analysis: AnalysisRecord) => {
            const analysisDate = new Date(
              analysis.date || analysis.timestamp || 0
            );
            return analysisDate >= oneWeekAgo;
          });

          setThisWeekCount(thisWeek.length);
        }
      } catch (err) {
        console.warn("Failed to fetch analysis history:", err);
        // Try to load from localStorage
        loadFromLocalStorage();
      }
    } catch (err) {
      console.error("Error fetching dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  const loadFromLocalStorage = () => {
    try {
      const savedAnalyses = localStorage.getItem("analysis_history");
      if (savedAnalyses) {
        const analyses = JSON.parse(savedAnalyses);
        if (analyses.length > 0) {
          setLastAnalysis(analyses[0]);

          const oneWeekAgo = new Date();
          oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);

          const thisWeek = analyses.filter((analysis: AnalysisRecord) => {
            const analysisDate = new Date(analysis.date || 0);
            return analysisDate >= oneWeekAgo;
          });

          setThisWeekCount(thisWeek.length);
        }
      }
    } catch (err) {
      console.error("Error loading from localStorage:", err);
    }
  };

  return (
    <div className="w-full py-8 md:py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Welcome Card */}
        <div className="bg-white/80 dark:bg-white/10 backdrop-blur-md rounded-xl shadow-lg p-6 md:p-8 mb-8 border border-white/20 dark:border-white/10">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
            <div>
              <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 dark:from-blue-400 dark:to-cyan-400 bg-clip-text text-transparent mb-2">
                Welcome, {user?.username || "User"}!
              </h1>
              <p className="text-gray-600 dark:text-gray-300 text-lg">
                Track your skin and hair health with AI-powered analysis.
              </p>
            </div>
            <button
              onClick={() => navigate("/analyze")}
              className="w-full md:w-auto bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-semibold py-3 px-6 rounded-lg transition shadow-lg hover:shadow-xl"
            >
              🎯 Start New Analysis
            </button>
          </div>
        </div>

        {/* Last Analysis & This Week Cards */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Last Analysis Card */}
          <div className="bg-white/80 dark:bg-white/10 backdrop-blur-md rounded-xl shadow-md p-6 border border-white/20 dark:border-white/10">
            <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
              📊 Last Analysis
            </h2>
            {loading ? (
              <div className="animate-pulse space-y-3">
                <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-3/4"></div>
                <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-1/2"></div>
              </div>
            ) : lastAnalysis ? (
              <div className="space-y-3">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Date
                    </p>
                    <p className="text-lg font-semibold text-gray-800 dark:text-white">
                      {new Date(
                        lastAnalysis.date || lastAnalysis.timestamp || ""
                      ).toLocaleDateString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Skin Score
                    </p>
                    <p className="text-lg font-semibold text-blue-600 dark:text-blue-400">
                      {lastAnalysis.skin_score?.toFixed(1) || "N/A"}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Hair Score
                    </p>
                    <p className="text-lg font-semibold text-cyan-600 dark:text-cyan-400">
                      {lastAnalysis.hair_score?.toFixed(1) || "N/A"}
                    </p>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                    Types
                  </p>
                  <div className="flex gap-2 flex-wrap">
                    {lastAnalysis.skin_type && (
                      <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full text-sm font-medium">
                        {lastAnalysis.skin_type}
                      </span>
                    )}
                    {lastAnalysis.hair_type && (
                      <span className="px-3 py-1 bg-cyan-100 dark:bg-cyan-900/30 text-cyan-700 dark:text-cyan-300 rounded-full text-sm font-medium">
                        {lastAnalysis.hair_type}
                      </span>
                    )}
                  </div>
                </div>
                {lastAnalysis.conditions_detected &&
                  lastAnalysis.conditions_detected.length > 0 && (
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                        Conditions Detected
                      </p>
                      <div className="flex gap-2 flex-wrap">
                        {lastAnalysis.conditions_detected.map(
                          (cond: string) => (
                            <span
                              key={cond}
                              className="px-2 py-1 bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 rounded-full text-xs font-medium"
                            >
                              {cond}
                            </span>
                          )
                        )}
                      </div>
                    </div>
                  )}
              </div>
            ) : (
              <p className="text-gray-600 dark:text-gray-300">
                No analysis available yet. Start one to see results here.
              </p>
            )}
          </div>

          {/* This Week Card */}
          <div className="bg-white/80 dark:bg-white/10 backdrop-blur-md rounded-xl shadow-md p-6 border border-white/20 dark:border-white/10">
            <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
              📈 This Week
            </h2>
            {loading ? (
              <div className="animate-pulse space-y-3">
                <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-3/4"></div>
                <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-1/2"></div>
              </div>
            ) : thisWeekCount > 0 ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Analyses
                    </p>
                    <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                      {thisWeekCount}
                    </p>
                  </div>
                  <div className="text-4xl">📸</div>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  You've completed {thisWeekCount} analysis
                  {thisWeekCount !== 1 ? "es" : ""} this week. Keep up the
                  consistent monitoring!
                </p>
              </div>
            ) : (
              <p className="text-gray-600 dark:text-gray-300">
                No analyses this week. Start one to track your progress!
              </p>
            )}
          </div>
        </div>

        {/* History Trend Chart */}
        <div className="mb-8">
          <HistoryTrend />
        </div>

        {/* Action Cards Grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            onClick={() => navigate("/analyze")}
            className="group bg-white/80 dark:bg-white/10 backdrop-blur-md rounded-xl shadow-md hover:shadow-xl p-6 cursor-pointer transition-all border border-white/20 dark:border-white/10 hover:border-blue-400/50 dark:hover:border-blue-400/50"
          >
            <div className="text-3xl mb-3">📸</div>
            <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition">
              Analyze Photo
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Upload or capture a new photo for AI analysis
            </p>
          </div>

          <div
            onClick={() => navigate("/profile")}
            className="group bg-white/80 dark:bg-white/10 backdrop-blur-md rounded-xl shadow-md hover:shadow-xl p-6 cursor-pointer transition-all border border-white/20 dark:border-white/10 hover:border-cyan-400/50 dark:hover:border-cyan-400/50"
          >
            <div className="text-3xl mb-3">👤</div>
            <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-2 group-hover:text-cyan-600 dark:group-hover:text-cyan-400 transition">
              My Profile
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              View and manage your account settings
            </p>
          </div>

          <div
            onClick={() => navigate("/recommendations")}
            className="group bg-white/80 dark:bg-white/10 backdrop-blur-md rounded-xl shadow-md hover:shadow-xl p-6 cursor-pointer transition-all border border-white/20 dark:border-white/10 hover:border-purple-400/50 dark:hover:border-purple-400/50"
          >
            <div className="text-3xl mb-3">💡</div>
            <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-2 group-hover:text-purple-600 dark:group-hover:text-purple-400 transition">
              Recommendations
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              View personalized care recommendations
            </p>
          </div>

          <div
            onClick={() => setReminderModalOpen(true)}
            className="group bg-white/80 dark:bg-white/10 backdrop-blur-md rounded-xl shadow-md hover:shadow-xl p-6 cursor-pointer transition-all border border-white/20 dark:border-white/10 hover:border-yellow-400/50 dark:hover:border-yellow-400/50"
          >
            <div className="text-3xl mb-3">⏰</div>
            <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-2 group-hover:text-yellow-600 dark:group-hover:text-yellow-400 transition">
              Reminders
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Set care routine reminders
            </p>
          </div>

          <div
            onClick={() => setSettingsModalOpen(true)}
            className="group bg-white/80 dark:bg-white/10 backdrop-blur-md rounded-xl shadow-md hover:shadow-xl p-6 cursor-pointer transition-all border border-white/20 dark:border-white/10 hover:border-emerald-400/50 dark:hover:border-emerald-400/50"
          >
            <div className="text-3xl mb-3">⚙️</div>
            <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-2 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition">
              Settings
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Configure app preferences
            </p>
          </div>
        </div>
      </div>

      <ReminderModal
        isOpen={reminderModalOpen}
        onClose={() => setReminderModalOpen(false)}
      />
      <SettingsModal
        isOpen={settingsModalOpen}
        onClose={() => setSettingsModalOpen(false)}
      />
    </div>
  );
}
