import { useState } from "react";
import ChatPage from "./pages/ChatPage";
import CompliancePage from "./pages/CompliancePage";

function App() {
  const [view, setView] = useState("chat"); // "chat" | "compliance"

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center">
      <div className="w-full max-w-6xl mx-auto p-4">
        {/* Top nav */}
        <div className="flex justify-between items-center mb-4">
          <div className="text-sm text-slate-400 font-mono">
            SentinelGuard AI Gateway
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setView("chat")}
              className={`px-3 py-1.5 text-xs rounded-full border ${
                view === "chat"
                  ? "bg-blue-600 text-white border-blue-500"
                  : "bg-slate-900 text-slate-300 border-slate-700"
              }`}
            >
              Guardrail Chat
            </button>
            <button
              onClick={() => setView("compliance")}
              className={`px-3 py-1.5 text-xs rounded-full border ${
                view === "compliance"
                  ? "bg-blue-600 text-white border-blue-500"
                  : "bg-slate-900 text-slate-300 border-slate-700"
              }`}
            >
              Ask Compliance
            </button>
          </div>
        </div>

        {view === "chat" ? <ChatPage /> : <CompliancePage />}
      </div>
    </div>
  );
}

export default App;
