import { useState } from "react";

export default function CompareSlider({ beforeUrl, afterUrl }) {
  const [position, setPosition] = useState(50);

  if (!beforeUrl || !afterUrl) {
    return (
      <section className="card compare-card">
        <h2>Before and After</h2>
        <p className="muted">Run an enhancement to preview comparison.</p>
      </section>
    );
  }

  return (
    <section className="card compare-card">
      <h2>Before and After</h2>
      <div className="compare-wrapper">
        <img src={beforeUrl} alt="Before enhancement" className="compare-image" />
        <span className="compare-badge before-badge">Before</span>

        <div className="compare-after" style={{ width: `${position}%` }}>
          <img src={afterUrl} alt="After enhancement" className="compare-image" />
          <span className="compare-badge after-badge">After</span>
        </div>

        <div className="compare-divider" style={{ left: `${position}%` }}>
          <div className="compare-handle">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </div>
        </div>

        <input
          type="range"
          min="0"
          max="100"
          value={position}
          onChange={(event) => setPosition(Number(event.target.value))}
          className="compare-range"
          aria-label="Before after comparison slider"
        />
      </div>
    </section>
  );
}
