import HighlightedText from "./HighlightedText";

function RedactionPreview({ original, sanitized, highlightSpans }) {
  if (!original) {
    return (
      <p className="text-xs text-slate-500">
        Send a prompt to see how SentinelGuard sanitizes it.
      </p>
    );
  }

  const changed = original !== sanitized;

  return (
    <div className="space-y-2">
      <div>
        <div className="text-xs text-slate-400 mb-1">Original prompt</div>
        <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-2 text-xs text-slate-200">
          <HighlightedText text={original} spans={highlightSpans} />
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
          <span>Sanitized prompt sent to LLM</span>
          {changed && (
            <span className="text-emerald-300 text-[11px]">
              Redactions applied
            </span>
          )}
        </div>
        <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-2 text-xs text-slate-200">
          {sanitized}
        </div>
      </div>
    </div>
  );
}

export default RedactionPreview;
