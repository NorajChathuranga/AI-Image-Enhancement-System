export default function JobStatus({ status, stage, processingTimeMs, error }) {
  return (
    <section className="card">
      <h2>Job Status</h2>
      <div className="status-grid">
        <div>
          <span className="muted">Status</span>
          <p className="status-value">{status}</p>
        </div>
        <div>
          <span className="muted">Stage</span>
          <p className="status-value">{stage ?? "waiting"}</p>
        </div>
        <div>
          <span className="muted">Processing Time</span>
          <p className="status-value">
            {processingTimeMs ? `${(processingTimeMs / 1000).toFixed(2)}s` : "-"}
          </p>
        </div>
      </div>
      {error ? <p className="error-message">{error}</p> : null}
    </section>
  );
}
