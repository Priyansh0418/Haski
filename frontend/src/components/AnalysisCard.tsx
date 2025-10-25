type Analysis = {
  skin_type: string;
  hair_type: string;
  conditions_detected: string[];
  confidence_scores: Record<string, number>;
};

interface AnalysisCardProps {
  analysis: Analysis;
  onSave: () => void;
  onRecommend: () => void;
}

export default function AnalysisCard({
  analysis,
  onSave,
  onRecommend,
}: AnalysisCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-2xl">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Analysis Results</h2>
      
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-gray-50 p-4 rounded">
          <p className="text-gray-600 text-sm font-medium">Skin Type</p>
          <p className="text-lg font-semibold text-gray-800">{analysis.skin_type}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded">
          <p className="text-gray-600 text-sm font-medium">Hair Type</p>
          <p className="text-lg font-semibold text-gray-800">{analysis.hair_type}</p>
        </div>
      </div>

      {analysis.conditions_detected.length > 0 && (
        <div className="mb-6">
          <p className="text-gray-600 text-sm font-medium mb-2">Conditions Detected</p>
          <div className="flex flex-wrap gap-2">
            {analysis.conditions_detected.map((condition) => (
              <span
                key={condition}
                className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm"
              >
                {condition}
              </span>
            ))}
          </div>
        </div>
      )}

      {Object.keys(analysis.confidence_scores).length > 0 && (
        <div className="mb-6">
          <p className="text-gray-600 text-sm font-medium mb-2">Confidence Scores</p>
          <div className="space-y-2">
            {Object.entries(analysis.confidence_scores).map(([key, score]) => (
              <div key={key} className="flex justify-between items-center">
                <span className="text-gray-700">{key}</span>
                <div className="bg-gray-200 rounded-full h-2 w-32">
                  <div
                    className="bg-blue-500 h-2 rounded-full"
                    style={{ width: score * 100 + "%" }}
                  ></div>
                </div>
                <span className="text-gray-600 text-sm">{(score * 100).toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex gap-3">
        <button
          onClick={onSave}
          className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg transition"
        >
          Save Results
        </button>
        <button
          onClick={onRecommend}
          className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition"
        >
          Get Recommendations
        </button>
      </div>
    </div>
  );
}
