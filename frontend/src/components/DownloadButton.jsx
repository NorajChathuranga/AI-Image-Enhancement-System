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
        {isDownloading ? (
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <svg className="spinner" viewBox="0 0 24 24" fill="none" style={{ width: '1.2rem', height: '1.2rem', animation: 'spin 1s linear infinite' }}>
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeDasharray="30 30" strokeLinecap="round" opacity="0.8"></circle>
            </svg>
            Downloading...
          </span>
        ) : (
          "Download"
        )}
      </button>
    </div>
  );
}
