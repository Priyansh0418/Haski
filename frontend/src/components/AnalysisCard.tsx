import React from "react";

type Analysis = {
  skin_type: string;
  hair_type: string;
  conditions_detected: string[];
  confidence_scores: Record<string, number>;
};

type Props = {
  analysis: Analysis;
  onSave?: () => void;
  onRecommend?: () => void;
};

export default function AnalysisCard({ analysis, onSave, onRecommend }: Props) {
  return (
    <div className="border rounded p-4 bg-white shadow">
      <h3 className="text-lg font-semibold mb-2">Analysis Result</h3>
      <div className="grid grid-cols-2 gap-2">
        <div>
          <div className="text-sm text-gray-500">Skin Type</div>
          <div className="text-md font-medium">{analysis.skin_type}</div>
        </div>
        <div>
          <div className="text-sm text-gray-500">Hair Type</div>
          <div className="text-md font-medium">{analysis.hair_type}</div>
        </div>
      </div>

      <div className="mt-3">
        <div className="text-sm text-gray-500">Conditions Detected</div>
        <ul className="list-disc list-inside">
          {analysis.conditions_detected.map((c) => (
            <li key={c}>{c}</li>
          ))}
        </ul>
      </div>

      <div className="mt-3">
        <div className="text-sm text-gray-500">Confidence Scores</div>
        <div className="flex gap-3 flex-wrap mt-1">
          {Object.entries(analysis.confidence_scores).map(([k, v]) => (
            <div key={k} className="px-2 py-1 bg-gray-100 rounded text-sm">
              {k}: {(v * 100).toFixed(0)}%
            </div>
          ))}
        </div>
      </div>

      <div className="mt-4 flex gap-2">
        <button
          onClick={onSave}
          className="bg-green-600 text-white px-3 py-2 rounded"
        >
          Save to history
        </button>
        <button
          onClick={onRecommend}
          className="bg-blue-600 text-white px-3 py-2 rounded"
        >
          Get recommendation
        </button>
      </div>
    </div>
  );
}
