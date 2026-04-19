import { useState } from "react";

export default function DownloadButton({ canDownload, onDownload, isDownloading }) {
  const [format, setFormat] = useState("webp");

  const handleDownload = () => {
    if (!canDownload || isDownloading) {
      return;
    }
    onDownload(format);
  };

  return (
    <div className="download-controls">
      <select
        className="format-select"
        value={format}
        onChange={(event) => setFormat(event.target.value)}
        disabled={!canDownload || isDownloading}
        aria-label="Download format"
      >
        <option value="webp">WebP</option>
        <option value="png">PNG</option>
        <option value="jpg">JPG</option>
      </select>
      <button className="action-button secondary" onClick={handleDownload} disabled={!canDownload || isDownloading}>
        {isDownloading ? "Downloading..." : "Download"}
      </button>
    </div>
  );
}
