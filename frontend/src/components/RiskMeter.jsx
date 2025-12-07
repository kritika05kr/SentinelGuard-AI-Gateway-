function RiskMeter({ score, level }) {
  if (score == null) return null;

  let color = "bg-emerald-500";
  if (score >= 70) color = "bg-red-500";
  else if (score >= 30) color = "bg-amber-400";

  return (
    <div>
      <div className="flex justify-between text-xs text-slate-400 mb-1">
        <span>Risk score</span>
        <span>
          {level} ({score}/100)
        </span>
      </div>
      <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
        <div
          className={`h-full ${color} transition-all`}
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );
}

export default RiskMeter;
