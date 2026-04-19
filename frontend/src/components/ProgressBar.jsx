export default function ProgressBar({ uploadProgress, processingProgress, status }) {
  const processingLabel =
    status === "complete"
      ? "Processing complete"
      : status === "failed"
      ? "Processing failed"
      : "Processing progress";

  return (
    <section className="card">
      <h2>Progress</h2>

      <div className="progress-row">
        <span>Upload</span>
        <span>{uploadProgress}%</span>
      </div>
      <div className="progress-track">
        <div className="progress-fill upload-fill" style={{ width: `${uploadProgress}%` }} />
      </div>

      <div className="progress-row">
        <span>{processingLabel}</span>
        <span>{processingProgress}%</span>
      </div>
      <div className="progress-track">
        <div
          className="progress-fill processing-fill"
          style={{ width: `${processingProgress}%` }}
        />
      </div>
    </section>
  );
}
