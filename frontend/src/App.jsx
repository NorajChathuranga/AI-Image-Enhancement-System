import { useCallback, useMemo, useState } from "react";

import CompareSlider from "./components/CompareSlider";
import DownloadButton from "./components/DownloadButton";
import ImageUploader from "./components/ImageUploader";
import JobStatus from "./components/JobStatus";
import ProgressBar from "./components/ProgressBar";
import { useImageCompare } from "./hooks/useImageCompare";
import { useJobStatus } from "./hooks/useJobStatus";
import { useUpload } from "./hooks/useUpload";
import { fetchJobResult } from "./services/apiClient";

function outputFilename(originalName) {
  const baseName = (originalName ?? "enhanced")
    .replace(/\.[A-Za-z0-9]+$/, "")
    .replace(/[^A-Za-z0-9_-]/g, "_");
  return `${baseName || "enhanced"}_enhanced.webp`;
}

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [jobId, setJobId] = useState("");
  const [enhancedBlob, setEnhancedBlob] = useState(null);
  const [resultError, setResultError] = useState("");

  const {
    uploadImage,
    uploadProgress,
    isUploading,
    uploadError,
    resetUploadState,
    setUploadError,
  } = useUpload();

  const handleComplete = useCallback(
    async () => {
      if (!jobId) {
        return;
      }
      try {
        const blob = await fetchJobResult(jobId);
        setEnhancedBlob(blob);
        setResultError("");
      } catch (error) {
        setResultError(error.message);
      }
    },
    [jobId]
  );

  const { status, progressPct, stage, processingTimeMs, error: processingError } = useJobStatus(
    jobId,
    { onComplete: handleComplete }
  );

  const { beforeUrl, afterUrl } = useImageCompare(selectedFile, enhancedBlob);

  const busy = isUploading || status === "pending" || status === "processing";

  const handleSelectFile = (file) => {
    setSelectedFile(file);
    setJobId("");
    setEnhancedBlob(null);
    setResultError("");
    setUploadError("");
    resetUploadState();
  };

  const handleEnhance = async () => {
    if (!selectedFile || busy) {
      return;
    }

    setEnhancedBlob(null);
    setResultError("");
    setJobId("");

    try {
      const payload = await uploadImage(selectedFile);
      setJobId(payload.job_id);
    } catch (error) {
      setResultError(error.message);
    }
  };

  const computedError = useMemo(() => {
    if (uploadError) {
      return uploadError;
    }
    if (processingError) {
      return processingError;
    }
    return resultError;
  }, [uploadError, processingError, resultError]);

  return (
    <div className="app-shell">
      <div className="background-orb orb-one" />
      <div className="background-orb orb-two" />

      <main className="layout">
        <header className="hero card">
          <p className="eyebrow">AI Image Enhancement System</p>
          <h1>Restore details with GAN-powered super resolution</h1>
          <p>
            Upload a low-quality image, run asynchronous enhancement, and compare the
            result instantly.
          </p>
          <div className="hero-actions">
            <button className="action-button" onClick={handleEnhance} disabled={!selectedFile || busy}>
              {busy ? "Processing..." : "Enhance Image"}
            </button>
            <DownloadButton
              blob={enhancedBlob}
              filename={outputFilename(selectedFile?.name)}
            />
          </div>
        </header>

        <section className="grid">
          <ImageUploader selectedFile={selectedFile} onFileSelected={handleSelectFile} disabled={busy} />
          <ProgressBar uploadProgress={uploadProgress} processingProgress={progressPct} status={status} />
        </section>

        <JobStatus
          status={status}
          stage={stage}
          processingTimeMs={processingTimeMs}
          error={computedError}
        />

        <CompareSlider beforeUrl={beforeUrl} afterUrl={afterUrl} />
      </main>
    </div>
  );
}
