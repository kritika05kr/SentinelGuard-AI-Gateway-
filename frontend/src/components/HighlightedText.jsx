function HighlightedText({ text, spans }) {
  if (!spans || spans.length === 0) {
    return <span className="whitespace-pre-wrap">{text}</span>;
  }

  const sorted = [...spans].sort((a, b) => a.start - b.start);
  const parts = [];
  let currentIndex = 0;

  sorted.forEach((span, idx) => {
    if (span.start > currentIndex) {
      parts.push({
        type: "normal",
        text: text.slice(currentIndex, span.start),
        key: `n-${idx}-${currentIndex}`,
      });
    }
    parts.push({
      type: "highlight",
      text: text.slice(span.start, span.end),
      key: `h-${idx}-${span.start}`,
    });
    currentIndex = span.end;
  });

  if (currentIndex < text.length) {
    parts.push({
      type: "normal",
      text: text.slice(currentIndex),
      key: `n-last-${currentIndex}`,
    });
  }

  return (
    <span className="whitespace-pre-wrap">
      {parts.map((p) =>
        p.type === "normal" ? (
          <span key={p.key}>{p.text}</span>
        ) : (
          <mark
            key={p.key}
            className="bg-amber-500/30 text-amber-100 rounded px-0.5"
          >
            {p.text}
          </mark>
        )
      )}
    </span>
  );
}

export default HighlightedText;
