import { useEffect, useState } from "react";
import { fetchLogs, fetchPolicies } from "../utils/api";

function AdminPage() {
  const [tab, setTab] = useState("logs"); // "logs" | "policies"
  const [logs, setLogs] = useState([]);
  const [policies, setPolicies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchLogs(50);
      setLogs(data);
    } catch (err) {
      setError(err.message || "Failed to load logs");
    } finally {
      setLoading(false);
    }
  };

  const loadPolicies = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchPolicies();
      setPolicies(data);
    } catch (err) {
      setError(err.message || "Failed to load policies");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (tab === "logs") {
      loadLogs();
    } else {
      loadPolicies();
    }
  }, [tab]);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-4 md:p-6 space-y-4">
      <header className="flex items-center justify-between mb-2">
        <div>
          <h1 className="text-xl md:text-2xl font-semibold text-slate-50">
            SentinelGuard – Admin
          </h1>
          <p className="text-sm text-slate-400">
            View audit logs and policy coverage.
          </p>
        </div>
      </header>

      {/* Tabs */}
      <div className="flex gap-2 mb-2">
        <button
          onClick={() => setTab("logs")}
          className={`px-3 py-1.5 text-xs rounded-full border ${
            tab === "logs"
              ? "bg-blue-600 text-white border-blue-500"
              : "bg-slate-900 text-slate-300 border-slate-700"
          }`}
        >
          Audit Logs
        </button>
        <button
          onClick={() => setTab("policies")}
          className={`px-3 py-1.5 text-xs rounded-full border ${
            tab === "policies"
              ? "bg-blue-600 text-white border-blue-500"
              : "bg-slate-900 text-slate-300 border-slate-700"
          }`}
        >
          Policies
        </button>
      </div>

      {error && (
        <div className="text-sm text-red-400 bg-red-900/30 border border-red-700/50 px-3 py-2 rounded-lg">
          {error}
        </div>
      )}

      {loading && (
        <div className="text-sm text-slate-400">Loading...</div>
      )}

      {!loading && tab === "logs" && (
        <div className="max-h-[420px] overflow-y-auto space-y-3 pr-1 text-xs">
          {logs.length === 0 && (
            <p className="text-slate-500">
              No logs yet. Use the main chat to generate some activity.
            </p>
          )}
          {logs.map((log, idx) => (
            <div
              key={idx}
              className="bg-slate-950/70 border border-slate-800 rounded-lg p-3"
            >
              <div className="flex justify-between mb-1">
                <div className="text-[11px] text-slate-400">
                  {log.timestamp} — user:{" "}
                  <span className="font-mono text-slate-200">
                    {log.user_id}
                  </span>
                </div>
                <div className="text-[11px]">
                  <span className="px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-200">
                    {log.decision?.action || log.decision?.Action}
                  </span>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                <div>
                  <div className="text-[11px] text-slate-400 mb-0.5">
                    Original prompt
                  </div>
                  <div className="bg-slate-900/80 border border-slate-800 rounded p-2 text-[11px] text-slate-200 max-h-28 overflow-y-auto">
                    {log.original_prompt}
                  </div>
                </div>
                <div>
                  <div className="text-[11px] text-slate-400 mb-0.5">
                    Sanitized prompt
                  </div>
                  <div className="bg-slate-900/80 border border-slate-800 rounded p-2 text-[11px] text-slate-200 max-h-28 overflow-y-auto">
                    {log.sanitized_prompt}
                  </div>
                </div>
              </div>
              <div className="mt-2 text-[11px] text-slate-400">
                Risk:{" "}
                <span className="text-slate-200">
                  {log.decision?.risk?.score} ({log.decision?.risk?.level})
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && tab === "policies" && (
        <div className="max-h-[420px] overflow-y-auto space-y-2 pr-1 text-xs">
          {policies.length === 0 && (
            <p className="text-slate-500">
              No policy chunks found. Ensure you have
              <span className="font-mono"> policies/chunked_policies.json</span>.
            </p>
          )}
          {policies.map((p) => (
            <div
              key={p.id}
              className="bg-slate-950/70 border border-slate-800 rounded-lg p-3"
            >
              <div className="text-[11px] text-blue-300 font-semibold mb-0.5">
                Policy {p.section}
              </div>
              <div className="text-sm text-slate-100 font-medium">
                {p.title}
              </div>
              <div className="mt-1 text-[11px] text-slate-400">
                {p.snippet}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default AdminPage;
