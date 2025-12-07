import { useState } from "react";
import ChatWindow from "../components/ChatWindow";
import SafetyPanel from "../components/SafetyPanel";
import { analyzePrompt, completeChat } from "../utils/api";

function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [backendError, setBackendError] = useState(null);

  const userId = "kritika"; // you can change later
  const role = "analyst";

  const handleSend = async () => {
    if (!input.trim()) return;

    setBackendError(null);

    const userMessage = {
      id: Date.now(),
      sender: "user",
      text: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      // 1) Analyze with SentinelGuard backend
      const analyzeRes = await analyzePrompt({
        userId,
        role,
        prompt: userMessage.text,
      });

      setAnalysis(analyzeRes);

      // 2) If not blocked, call complete endpoint
      if (analyzeRes.decision.action !== "BLOCK") {
        const completeRes = await completeChat({
          sanitizedPrompt: analyzeRes.sanitized_prompt,
          decision: analyzeRes.decision,
          userId,
        });

        const botMessage = {
          id: Date.now() + 1,
          sender: "bot",
          text: completeRes.answer,
        };

        setMessages((prev) => [...prev, botMessage]);
      } else {
        const botMessage = {
          id: Date.now() + 1,
          sender: "bot",
          text:
            "⛔ Your request was blocked by SentinelGuard based on policies. Please remove secrets/PII and try again.",
        };
        setMessages((prev) => [...prev, botMessage]);
      }
    } catch (err) {
      console.error(err);
      setBackendError(err.message || "Something went wrong talking to backend");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-4 md:p-6 space-y-4">
      <header className="flex items-center justify-between mb-2">
        <div>
          <h1 className="text-xl md:text-2xl font-semibold text-slate-50">
            SentinelGuard – AI Gateway
          </h1>
          <p className="text-sm text-slate-400">
            Safety-first layer between your prompts and any LLM.
          </p>
        </div>
      </header>

      {backendError && (
        <div className="mb-2 text-sm text-red-400 bg-red-900/30 border border-red-700/40 px-3 py-2 rounded-lg">
          {backendError}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ChatWindow
          messages={messages}
          input={input}
          setInput={setInput}
          onSend={handleSend}
          loading={loading}
        />

        <SafetyPanel analysis={analysis} />
      </div>
    </div>
  );
}

export default ChatPage;
