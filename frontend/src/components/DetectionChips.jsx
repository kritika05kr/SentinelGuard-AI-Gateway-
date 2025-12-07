function DetectionChips({ detectionSummary }) {
  if (!detectionSummary) return null;
  const entries = Object.entries(detectionSummary.detection_counts || {});
  if (entries.length === 0) {
    return (
      <p className="text-xs text-slate-500">
        No sensitive patterns detected.
      </p>
    );
  }

  return (
    <div className="flex flex-wrap gap-1.5">
      {entries.map(([type, count]) => (
        <span
          key={type}
          className="inline-flex items-center px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-[11px] text-slate-100"
        >
          <span className="font-mono text-[10px] mr-1">{type}</span>
          <span className="text-slate-300">×{count}</span>
        </span>
      ))}
    </div>
  );
}

export default DetectionChips;
