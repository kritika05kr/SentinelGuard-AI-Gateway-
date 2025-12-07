import { useState } from "react";
import { askCompliance } from "../utils/api";

function CompliancePage() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [policies, setPolicies] = useState([]);
  const [alignment, setAlignment] = useState(null);
  const [loading, setLoading] = useState(false);
  const [backendError, setBackendError] = useState(null);

  const handleAsk = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setBackendError(null);
    setAnswer("");
    setPolicies([]);
    setAlignment(null);

    try {
      const res = await askCompliance(question);
      setAnswer(res.answer);
      setPolicies(res.policies || []);
      setAlignment(res.alignment_score ?? null);
    } catch (err) {
      console.error(err);
      setBackendError(err.message || "Something went wrong talking to backend");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-4 md:p-6 space-y-4">
      <header className="mb-2">
        <h1 className="text-xl md:text-2xl font-semibold text-slate-50">
          Ask Compliance
        </h1>
        <p className="text-sm text-slate-400">
          Ask questions about what is allowed or not. Answers are based only on the
          company handbook and policies indexed by SentinelGuard.
        </p>
      </header>

      {backendError && (
        <div className="text-sm text-red-400 bg-red-900/30 border border-red-700/40 px-3 py-2 rounded-lg">
          {backendError}
        </div>
      )}

      <div className="space-y-3">
        <div>
          <label className="block text-xs text-slate-400 mb-1">
            Your question to Compliance
          </label>
          <textarea
            className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 resize-none h-24 focus:outline-none focus:ring-2 focus:ring-blue-500/70"
            placeholder='Example: "Can I share anonymized customer screenshots on LinkedIn?"'
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
        </div>

        <div className="flex justify-end">
          <button
            onClick={handleAsk}
            disabled={loading}
            className="px-4 py-1.5 text-sm rounded-full bg-blue-600 hover:bg-blue-500 disabled:bg-slate-600 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? "Consulting handbook..." : "Ask Compliance"}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-3">
        {/* Answer pane */}
        <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-3 text-xs text-slate-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400">Compliance answer</span>
            {alignment !== null && (
              <span className="text-[11px] text-blue-300">
                Policy alignment: {(alignment * 100).toFixed(0)}%
              </span>
            )}
          </div>
          {answer ? (
            <pre className="whitespace-pre-wrap text-slate-200">
              {answer}
            </pre>
          ) : (
            <p className="text-slate-500">
              Ask a question above to see an answer grounded in policy.
            </p>
          )}
        </div>

        {/* Policies pane */}
        <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-3 text-xs text-slate-200">
          <div className="text-slate-400 mb-2">Relevant policy sections</div>
          {policies.length === 0 ? (
            <p className="text-slate-500">
              No specific sections shown yet. Ask a question to see related policies.
            </p>
          ) : (
            <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
              {policies.map((p) => (
                <div
                  key={p.id}
                  className="bg-slate-900/80 border border-slate-800 rounded-lg p-2.5"
                >
                  <div className="flex items-center justify-between mb-1">
                    <div className="text-[11px] text-blue-300 font-semibold">
                      Section {p.section}
                    </div>
                    {p.category && (
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-200">
                        {p.category}
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-slate-100 font-medium mb-1">
                    {p.title}
                  </div>
                  <div className="text-[11px] text-slate-400">
                    {p.snippet}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default CompliancePage;
