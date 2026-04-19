export default function DownloadButton({ blob, filename }) {
  const canDownload = Boolean(blob);

  const handleDownload = () => {
    if (!blob) {
      return;
    }
    const objectUrl = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = objectUrl;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(objectUrl);
  };

  return (
    <button className="action-button secondary" onClick={handleDownload} disabled={!canDownload}>
      Download Enhanced WebP
    </button>
  );
}
