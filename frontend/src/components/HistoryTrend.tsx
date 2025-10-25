import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import * as api from "../lib/api";

interface AnalysisPoint {
  id?: number;
  date?: string;
  timestamp?: string;
  skin_score?: number;
  hair_score?: number;
  skin_type?: string;
  hair_type?: string;
  conditions_detected?: string[];
}

interface ChartData {
  date: string;
  skin_score: number;
  hair_score: number;
}

export default function HistoryTrend() {
  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true);
        setError(null);
        const history = await api.getAnalysisHistory();

        // Handle both array and object responses
        const analyses = Array.isArray(history)
          ? history
          : history.analyses || history.data || [];

        // Transform last 5 analyses into chart data
        const transformed = analyses
          .slice(0, 5)
          .map((analysis: AnalysisPoint) => ({
            date: analysis.date
              ? new Date(analysis.date).toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                })
              : analysis.timestamp
              ? new Date(analysis.timestamp).toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                })
              : "Unknown",
            skin_score: analysis.skin_score || (analysis.skin_type ? 75 : 0),
            hair_score: analysis.hair_score || (analysis.hair_type ? 70 : 0),
          }))
          .reverse(); // Oldest first

        setChartData(transformed);
      } catch (err) {
        console.error("Error fetching analysis history:", err);
        // Fallback: generate mock data or show empty state
        setError(
          err instanceof Error ? err.message : "Failed to fetch history"
        );
        setChartData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  if (loading) {
    return (
      <div className="bg-white/80 dark:bg-white/10 backdrop-blur-md rounded-xl shadow-lg p-8 border border-white/20 dark:border-white/10">
        <h3 className="text-2xl font-bold text-gray-800 dark:text-white mb-6">
          📈 Analysis Trends
        </h3>
        <div className="flex flex-col items-center justify-center h-64 gap-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400"></div>
          <p className="text-gray-600 dark:text-gray-300">
            Loading your analysis history...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white/80 dark:bg-white/10 backdrop-blur-md rounded-xl shadow-lg p-8 border border-white/20 dark:border-white/10">
        <h3 className="text-2xl font-bold text-gray-800 dark:text-white mb-6">
          📈 Analysis Trends
        </h3>
        <div className="bg-blue-100 dark:bg-blue-900/30 border border-blue-300 dark:border-blue-700 rounded-lg p-6 text-center">
          <p className="text-blue-800 dark:text-blue-200 mb-2 font-semibold">
            📊 No analysis history available
          </p>
          <p className="text-blue-700 dark:text-blue-300">
            Start by capturing your first photo to see trends over time.
          </p>
        </div>
      </div>
    );
  }

  if (chartData.length === 0) {
    return (
      <div className="bg-white/80 dark:bg-white/10 backdrop-blur-md rounded-xl shadow-lg p-8 border border-white/20 dark:border-white/10">
        <h3 className="text-2xl font-bold text-gray-800 dark:text-white mb-6">
          📈 Analysis Trends
        </h3>
        <div className="bg-blue-100 dark:bg-blue-900/30 border border-blue-300 dark:border-blue-700 rounded-lg p-6 text-center">
          <p className="text-blue-800 dark:text-blue-200 mb-2 font-semibold">
            📊 No analysis history available
          </p>
          <p className="text-blue-700 dark:text-blue-300">
            Start by capturing your first photo to see trends over time.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white/80 dark:bg-white/10 backdrop-blur-md rounded-xl shadow-lg p-8 border border-white/20 dark:border-white/10">
      <div className="mb-6">
        <h3 className="text-2xl font-bold text-gray-800 dark:text-white">
          📈 Analysis Trends
        </h3>
        <p className="text-gray-600 dark:text-gray-300 text-sm mt-1">
          Last {chartData.length} analyses
        </p>
      </div>

      <div className="w-full h-80 bg-white/50 dark:bg-white/5 rounded-lg p-4">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.1)" />
            <XAxis dataKey="date" stroke="#666" />
            <YAxis domain={[0, 100]} stroke="#666" />
            <Tooltip
              contentStyle={{
                backgroundColor: "rgba(255, 255, 255, 0.95)",
                border: "2px solid #3b82f6",
                borderRadius: "8px",
              }}
              formatter={(value) => `${value}%`}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="skin_score"
              stroke="#06b6d4"
              dot={{ fill: "#06b6d4", r: 5 }}
              activeDot={{ r: 7 }}
              name="Skin Score"
              strokeWidth={3}
            />
            <Line
              type="monotone"
              dataKey="hair_score"
              stroke="#3b82f6"
              dot={{ fill: "#3b82f6", r: 5 }}
              activeDot={{ r: 7 }}
              name="Hair Score"
              strokeWidth={3}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-6 p-4 bg-cyan-100 dark:bg-cyan-900/30 border border-cyan-300 dark:border-cyan-700 rounded-lg">
        <p className="text-cyan-800 dark:text-cyan-200 text-sm">
          <span className="font-semibold">💡 Tip:</span> These scores track
          improvements in your skin and hair health over time based on your
          analyses.
        </p>
      </div>
    </div>
  );
}
