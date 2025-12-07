function ChatWindow({ messages, input, setInput, onSend, loading }) {
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className="flex flex-col h-[480px] bg-slate-950/60 border border-slate-800 rounded-xl p-3 md:p-4">
      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {messages.length === 0 && (
          <div className="text-sm text-slate-500">
            Start typing a prompt. For now this is just a local chat test (no backend).
          </div>
        )}
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex ${
              m.sender === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[80%] px-3 py-2 rounded-2xl text-sm ${
                m.sender === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-slate-800 text-slate-100 border border-slate-700/60"
              }`}
            >
              <p className="whitespace-pre-wrap">{m.text}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 border-t border-slate-800 pt-3">
        <textarea
          className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 resize-none h-20 focus:outline-none focus:ring-2 focus:ring-blue-500/70"
          placeholder="Type something and press Enter or click Send..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <div className="mt-2 flex justify-end">
          <button
            onClick={onSend}
            disabled={loading}
            className="px-4 py-1.5 text-sm rounded-full bg-blue-600 hover:bg-blue-500 disabled:bg-slate-600 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? "Sending..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatWindow;
