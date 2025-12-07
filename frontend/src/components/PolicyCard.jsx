function PolicyCard({ policy }) {
  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-lg p-2.5 mb-2">
      <div className="text-[11px] text-blue-300 font-semibold">
        Policy {policy.section}
      </div>
      <div className="text-sm text-slate-100 font-medium">{policy.title}</div>
      <div className="text-xs text-slate-400 mt-1">{policy.snippet}</div>
    </div>
  );
}

export default PolicyCard;
