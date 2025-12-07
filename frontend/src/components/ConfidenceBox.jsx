function ConfidenceBox({ confidence }) {
  if (!confidence) return null;
  const { score, factors } = confidence;

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-lg p-2.5 text-xs">
      <div className="flex items-center justify-between mb-1">
        <span className="font-semibold text-slate-100">
          Guardrail confidence
        </span>
        <span className="text-blue-300 font-semibold">{score}%</span>
      </div>
      <ul className="space-y-0.5 text-slate-400">
        <li>ML model confidence: {(factors.model_confidence * 100).toFixed(0)}%</li>
        <li>Detector agreement: {(factors.detector_agreement * 100).toFixed(0)}%</li>
        <li>Policy alignment: {(factors.policy_alignment * 100).toFixed(0)}%</li>
      </ul>
    </div>
  );
}

export default ConfidenceBox;
