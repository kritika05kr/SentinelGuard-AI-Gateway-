
import RiskMeter from "./RiskMeter";
import DetectionChips from "./DetectionChips";
import PolicyCard from "./PolicyCard";
import TimelineStep from "./TimelineStep";
import ConfidenceBox from "./ConfidenceBox";
import RedactionPreview from "./RedactionPreview";

function SafetyPanel({ analysis }) {
  const decision = analysis?.decision;

  return (
    <div className="flex flex-col h-[480px] bg-slate-950/60 border border-slate-800 rounded-xl p-3 md:p-4">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-sm font-semibold text-slate-100">Safety Inspector</h2>
        {decision && (
          <span
            className={`text-[11px] px-2 py-0.5 rounded-full border ${
              decision.action === "BLOCK"
                ? "bg-red-900/40 border-red-700/60 text-red-200"
                : decision.action === "REDACT"
                ? "bg-amber-900/40 border-amber-700/60 text-amber-200"
                : "bg-emerald-900/40 border-emerald-700/60 text-emerald-200"
            }`}
          >
            Action: {decision.action}
          </span>
        )}
      </div>

      {!analysis && (
        <div className="text-xs text-slate-500">
          No analysis yet. Once you send a prompt, SentinelGuard will show: risk
          score, guardrail confidence, detections, policies, and how your prompt
          was sanitized before reaching any LLM.
        </div>
      )}

      {analysis && (
        <>
          {/* Risk & Confidence */}
          <div className="space-y-2 mb-3">
            <RiskMeter
              score={decision?.risk?.score}
              level={decision?.risk?.level}
            />
            <ConfidenceBox confidence={decision?.confidence} />
          </div>

          {/* Detections & Policies */}
          <div className="grid grid-cols-1 gap-2 mb-3">
            <div>
              <div className="text-xs text-slate-400 mb-1">Detections</div>
              <DetectionChips detectionSummary={analysis.detection_summary} />
            </div>

            <div>
              <div className="text-xs text-slate-400 mb-1">Policies involved</div>
              {decision?.policy_refs?.length ? (
                <div className="max-h-28 overflow-y-auto pr-1">
                  {decision.policy_refs.map((p) => (
                    <PolicyCard key={p.id} policy={p} />
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-500">
                  No specific policy matches yet.
                </p>
              )}
            </div>
          </div>

          {/* Safety Timeline */}
          <div className="mb-3">
            <div className="text-xs text-slate-400 mb-1">Safety timeline</div>
            <div className="space-y-1 max-h-24 overflow-y-auto pr-1">
              {analysis.safety_timeline?.map((step, idx) => (
                <TimelineStep
                  key={idx}
                  text={step}
                  isLast={idx === analysis.safety_timeline.length - 1}
                />
              ))}
            </div>
          </div>

          {/* Redaction Preview */}
          <div className="mt-auto">
            <div className="text-xs text-slate-400 mb-1">Redaction preview</div>
            <RedactionPreview
              original={analysis.original_prompt}
              sanitized={analysis.sanitized_prompt}
              highlightSpans={analysis.highlight_spans}
            />
          </div>
        </>
      )}
    </div>
  );
}

export default SafetyPanel;
