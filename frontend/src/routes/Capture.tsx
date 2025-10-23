import React from "react";

import React, { useState } from "react";
import CameraCapture from "../components/CameraCapture";
import AnalysisCard from "../components/AnalysisCard";

type Analysis = {
  skin_type: string;
  hair_type: string;
  conditions_detected: string[];
  confidence_scores: Record<string, number>;
};

export default function Capture() {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(false);

  const onCapture = async (dataUrl: string) => {
    setLoading(true);
    try {
      // convert base64 dataUrl to blob
      const res = await fetch(dataUrl);
      const blob = await res.blob();

      const form = new FormData();
      form.append("image", blob, "capture.jpg");

      const resp = await fetch("/api/v1/analyze/image", {
        method: "POST",
        body: form,
      });

      if (!resp.ok) {
        const txt = await resp.text();
        throw new Error(txt || "Analyze failed");
      }

      const json = await resp.json();
      setAnalysis(json);
    } catch (err: any) {
      console.error(err);
      alert("Analysis failed: " + (err?.message || err));
    } finally {
      setLoading(false);
    }
  };

  const handleSave = () => {
    // placeholder: save to history endpoint
    alert("Saved to history (stub)");
  };

  const handleRecommend = () => {
    // placeholder: call recommendation service
    alert("Get recommendation (stub)");
  };

  return (
    <div>
      {!analysis && (
        <div>
          <CameraCapture onCapture={onCapture} />
        </div>
      )}

      {loading && <div className="mt-3">Analyzing...</div>}

      {analysis && (
        <div className="mt-4">
          <AnalysisCard
            analysis={analysis}
            onSave={handleSave}
            onRecommend={handleRecommend}
          />
        </div>
      )}
    </div>
  );
}
