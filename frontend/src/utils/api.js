const BASE_URL = "http://localhost:8000/api"; // FastAPI backend

export async function analyzePrompt({ userId, role, prompt }) {
  const res = await fetch(`${BASE_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: userId,
      role,
      prompt,
    }),
  });

  if (!res.ok) {
    throw new Error("Failed to analyze prompt");
  }

  return res.json();
}

export async function completeChat({ sanitizedPrompt, decision, userId }) {
  const res = await fetch(`${BASE_URL}/complete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sanitized_prompt: sanitizedPrompt,
      decision,
      user_id: userId,
      conversation_id: null,
    }),
  });

  if (!res.ok) {
    throw new Error("Failed to complete chat");
  }

  return res.json();
}

export async function askCompliance(question, userId = "kritika") {
  const res = await fetch(`${BASE_URL}/compliance/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: userId,
      question,
    }),
  });

  if (!res.ok) {
    throw new Error("Failed to contact compliance assistant");
  }

  return res.json();
}
