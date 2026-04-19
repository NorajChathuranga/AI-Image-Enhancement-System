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

function outputFilename(originalName, format = "webp") {
  const baseName = (originalName ?? "enhanced")
    .replace(/\.[A-Za-z0-9]+$/, "")
    .replace(/[^A-Za-z0-9_-]/g, "_");
  const extension = format === "jpeg" ? "jpg" : format;
  return `${baseName || "enhanced"}_enhanced.${extension}`;
}

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [jobId, setJobId] = useState("");
  const [enhancedBlob, setEnhancedBlob] = useState(null);
  const [resultError, setResultError] = useState("");
  const [isDownloading, setIsDownloading] = useState(false);

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
        const blob = await fetchJobResult(jobId, "webp");
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

  const handleDownload = useCallback(
    async (format) => {
      if (!jobId) {
        return;
      }

      try {
        setIsDownloading(true);
        const blob = await fetchJobResult(jobId, format);
        const objectUrl = URL.createObjectURL(blob);
        const anchor = document.createElement("a");
        anchor.href = objectUrl;
        anchor.download = outputFilename(selectedFile?.name, format);
        anchor.click();
        URL.revokeObjectURL(objectUrl);
        setResultError("");
      } catch (error) {
        setResultError(error.message);
      } finally {
        setIsDownloading(false);
      }
    },
    [jobId, selectedFile]
  );

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
              canDownload={Boolean(jobId && status === "complete")}
              onDownload={handleDownload}
              isDownloading={isDownloading}
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
