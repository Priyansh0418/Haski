import React, { useState } from "react";
import CameraCapture from "../components/CameraCapture";
import AnalysisCard from "../components/AnalysisCard";

type Analysis = {
  skin_type: string;
  hair_type: string;
  conditions_detected: string[];
  confidence_scores: Record<string, number>;
};

const API_BASE = (() => {
  // Try to get from env first
  const envUrl = (import.meta as any).env.VITE_API_URL;
  if (envUrl) return envUrl;

  // Fallback: use current hostname with port 8000
  // This handles both localhost and 127.0.0.1
  return `http://${window.location.hostname}:8000`;
})();

export default function Capture() {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(false);

  const onCapture = async (dataUrl: string) => {
    setLoading(true);
    const sep = "=".repeat(50);
    console.log(sep, "CAPTURE START", sep);
    try {
      // Convert base64 data URL to blob directly
      console.log("1. Converting base64 to blob...");
      const arr = dataUrl.split(",");
      const mime = arr[0].match(/:(.*?);/)?.[1] || "image/jpeg";
      const bstr = atob(arr[1]);
      let n = bstr.length;
      const u8arr = new Uint8Array(n);
      while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
      }
      const blob = new Blob([u8arr], { type: mime });
      console.log(
        "   Blob created: size=" + blob.size + " bytes, type=" + mime
      );

      const form = new FormData();
      form.append("image", blob, "capture.jpg");
      console.log("2. FormData created with image field");

      const url = `${API_BASE}/api/v1/analyze/image`;
      console.log("3. API_BASE config:", API_BASE);
      console.log("4. Full URL:", url);
      console.log("5. Fetching with 60s timeout...");

      // Create abort controller for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout

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
      // Parse response body first, before checking status
      let json: any;
      try {
        json = await resp.json();
        console.log("   Response JSON parsed:", json);
      } catch (parseErr) {
        console.error("   Failed to parse JSON:", parseErr);
        throw new Error(`Failed to parse response: ${parseErr}`);
      }

      if (!resp.ok) {
        console.log("8. Response NOT OK, throwing error...");
        const errorMsg = json?.detail || json?.error || `HTTP ${resp.status}`;
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
      alert("Analysis failed: " + errorMsg);
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
