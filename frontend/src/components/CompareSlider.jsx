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

        <div className="compare-after" style={{ width: `${position}%` }}>
          <img src={afterUrl} alt="After enhancement" className="compare-image" />
        </div>

        <div className="compare-divider" style={{ left: `${position}%` }}>
          <span className="compare-handle" />
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
