function TimelineStep({ text, isLast }) {
  return (
    <div className="flex items-start gap-2">
      <div className="flex flex-col items-center">
        <div className="w-2 h-2 rounded-full bg-blue-400" />
        {!isLast && <div className="flex-1 w-px bg-slate-700 mt-1" />}
      </div>
      <p className="text-xs text-slate-200">{text}</p>
    </div>
  );
}

export default TimelineStep;
