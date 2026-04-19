import ReactCompareImage from "react-compare-image";

export default function CompareSlider({ beforeUrl, afterUrl }) {
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
      <ReactCompareImage leftImage={beforeUrl} rightImage={afterUrl} />
    </section>
  );
}
