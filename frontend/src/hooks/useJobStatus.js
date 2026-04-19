import { useEffect, useRef, useState } from "react";

import { fetchJobStatus } from "../services/apiClient";

export function useJobStatus(jobId, options = {}) {
  const { onComplete } = options;

  const [status, setStatus] = useState("idle");
  const [progressPct, setProgressPct] = useState(0);
  const [stage, setStage] = useState(null);
  const [processingTimeMs, setProcessingTimeMs] = useState(null);
  const [error, setError] = useState("");

  const completedJobRef = useRef(null);
  const onCompleteRef = useRef(onComplete);

  useEffect(() => {
    onCompleteRef.current = onComplete;
  }, [onComplete]);

  useEffect(() => {
    if (!jobId) {
      setStatus("idle");
      setProgressPct(0);
      setStage(null);
      setProcessingTimeMs(null);
      setError("");
      completedJobRef.current = null;
      return;
    }

    const pollingIntervalMs = Number(import.meta.env.VITE_POLL_INTERVAL_MS ?? 2000);
    let active = true;

    const poll = async () => {
      try {
        const payload = await fetchJobStatus(jobId);
        if (!active) {
          return;
        }

        setStatus(payload.status);
        setProgressPct(payload.progress_pct ?? 0);
        setStage(payload.stage ?? null);
        setProcessingTimeMs(payload.processing_time_ms ?? null);
        setError(payload.error ?? "");

        if (payload.status === "complete" && completedJobRef.current !== jobId) {
          completedJobRef.current = jobId;
          if (onCompleteRef.current) {
            onCompleteRef.current(payload);
          }
        }
      } catch (pollError) {
        if (!active) {
          return;
        }
        setError(pollError.message);
        setStatus("failed");
      }
    };

    poll();
    const intervalId = window.setInterval(poll, pollingIntervalMs);

    return () => {
      active = false;
      window.clearInterval(intervalId);
    };
  }, [jobId]);

  return {
    status,
    progressPct,
    stage,
    processingTimeMs,
    error,
  };
}
