const PRESET_CONTENT = {
  fast: {
    title: "Fast",
    description: "Quicker result with light cleanup and 2x upscale.",
  },
  balanced: {
    title: "Balanced",
    description: "Recommended for most images and social uploads.",
  },
  quality: {
    title: "Quality",
    description: "Stronger restoration with higher output quality.",
  },
};

const PRESET_ORDER = ["fast", "balanced", "quality"];

const PRESET_LABELS = {
  fast: "Fast",
  balanced: "Balanced",
  quality: "Quality",
  custom: "Custom",
};

export default function EnhancementControls({
  options,
  onPresetChange,
  onOptionChange,
  disabled,
}) {
  return (
    <section className="card controls-card">
      <div className="controls-header">
        <h2>Enhancement Controls</h2>
        <span className="preset-pill">{PRESET_LABELS[options.preset] ?? "Custom"}</span>
      </div>

      <p className="muted">Select a preset or adjust each stage manually.</p>

      <div className="preset-grid" role="group" aria-label="Enhancement presets">
        {PRESET_ORDER.map((preset) => {
          const presetContent = PRESET_CONTENT[preset];
          const isActive = options.preset === preset;

          return (
            <button
              key={preset}
              type="button"
              className={`preset-button ${isActive ? "preset-button-active" : ""}`}
              onClick={() => onPresetChange(preset)}
              disabled={disabled}
              aria-pressed={isActive}
            >
              <span className="preset-title">{presetContent.title}</span>
              <span className="preset-description">{presetContent.description}</span>
            </button>
          );
        })}
      </div>

      <div className="control-group">
        <label className="control-field" htmlFor="scale-factor-select">
          <span className="control-label">Upscale Factor</span>
          <select
            id="scale-factor-select"
            className="format-select control-select"
            value={options.scaleFactor}
            onChange={(event) => onOptionChange("scaleFactor", Number(event.target.value))}
            disabled={disabled}
          >
            <option value={2}>2x</option>
            <option value={4}>4x</option>
          </select>
        </label>

        <label className="control-field" htmlFor="output-quality-range">
          <span className="control-label">Output Quality: {options.outputQuality}</span>
          <input
            id="output-quality-range"
            type="range"
            min="70"
            max="100"
            step="1"
            className="control-slider"
            value={options.outputQuality}
            onChange={(event) => onOptionChange("outputQuality", Number(event.target.value))}
            disabled={disabled}
          />
        </label>
      </div>

      <div className="toggle-grid">
        <label className="toggle-field" htmlFor="toggle-denoise">
          <input
            id="toggle-denoise"
            type="checkbox"
            checked={options.denoise}
            onChange={(event) => onOptionChange("denoise", event.target.checked)}
            disabled={disabled}
          />
          <span>Noise Reduction</span>
        </label>

        <label className="toggle-field" htmlFor="toggle-deblur">
          <input
            id="toggle-deblur"
            type="checkbox"
            checked={options.deblur}
            onChange={(event) => onOptionChange("deblur", event.target.checked)}
            disabled={disabled}
          />
          <span>Deblur Sharpening</span>
        </label>

        <label className="toggle-field" htmlFor="toggle-face-enhance">
          <input
            id="toggle-face-enhance"
            type="checkbox"
            checked={options.faceEnhance}
            onChange={(event) => onOptionChange("faceEnhance", event.target.checked)}
            disabled={disabled}
          />
          <span>Face Restoration</span>
        </label>
      </div>
    </section>
  );
}