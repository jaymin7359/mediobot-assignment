"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { Loader } from "../loader";
import { normalizeMarkdown } from "../markdown";

const API = "http://localhost:8000";

type Source = {
  source_document: string;
  section_title: string;
  collection: string;
};

type Message = {
  question: string;
  answer: string;
  sources: Source[];
  retrieval_type: string;
  blocked?: boolean;
};

export default function ChatPage() {
  const router = useRouter();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [role, setRole] = useState("");
  const [collections, setCollections] = useState<string[]>([]);
  const [pageLoading, setPageLoading] = useState(true);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [pendingQuestion, setPendingQuestion] = useState("");
  const [chatError, setChatError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("medibot_token");
    const savedRole = localStorage.getItem("medibot_role");
    if (!token || !savedRole) {
      router.push("/");
      return;
    }
    setRole(savedRole);
    fetch(`${API}/collections/${savedRole}`)
      .then((r) => r.json())
      .then((d) => setCollections(d.collections || []))
      .finally(() => setPageLoading(false));
  }, [router]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, pendingQuestion]);

  async function sendQuestion(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim() || loading) return;

    const token = localStorage.getItem("medibot_token");
    const asked = question.trim();
    setChatError("");
    setPendingQuestion(asked);
    setQuestion("");
    setLoading(true);

    try {
      const res = await fetch(`${API}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ question: asked }),
      });

      if (!res.ok) {
        throw new Error("Request failed");
      }

      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        {
          question: asked,
          answer: data.answer,
          sources: data.sources || [],
          retrieval_type: data.retrieval_type,
          blocked: data.blocked,
        },
      ]);
    } catch {
      setChatError("Failed to get a response. Check that the backend is running.");
      setQuestion(asked);
    } finally {
      setPendingQuestion("");
      setLoading(false);
    }
  }

  if (pageLoading) {
    return (
      <div className="page-loader">
        <Loader label="Loading your session..." />
      </div>
    );
  }

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <aside style={{ width: 260, background: "#0d47a1", color: "#fff", padding: 20 }}>
        <h2>MediBot</h2>
        <p><strong>Role:</strong> {role.replace("_", " ")}</p>
        <p><strong>Collections you can access:</strong></p>
        <ul>
          {collections.map((c) => <li key={c}>{c}</li>)}
        </ul>
        <button
          onClick={() => { localStorage.clear(); router.push("/"); }}
          style={{ marginTop: 20, padding: 8, width: "100%" }}
        >
          Logout
        </button>
      </aside>

      <main style={{ flex: 1, padding: 24, display: "flex", flexDirection: "column" }}>
        <h1>Chat</h1>
        <div style={{ flex: 1, display: "grid", gap: 16, marginBottom: 24, alignContent: "start" }}>
          {messages.map((m, i) => (
            <div key={i} style={{ background: "#fff", padding: 16, borderRadius: 8, boxShadow: "0 1px 4px #0001" }}>
              <p><strong>You:</strong> {m.question}</p>
              <span style={{
                fontSize: 12,
                background: m.retrieval_type === "sql_rag" ? "#ede7f6" : "#e0f2f1",
                padding: "2px 8px",
                borderRadius: 4,
              }}>
                {m.retrieval_type === "sql_rag" ? "SQL RAG" : "Hybrid RAG"}
              </span>
              <div style={{ marginTop: 8 }}>
                <strong>MediBot:</strong>
                <div className={`markdown-body${m.blocked ? " blocked" : ""}`}>
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      table: ({ children }) => (
                        <div className="table-wrap">
                          <table>{children}</table>
                        </div>
                      ),
                    }}
                  >
                    {normalizeMarkdown(m.answer)}
                  </ReactMarkdown>
                </div>
              </div>
              {m.sources.length > 0 && (
                <div style={{ marginTop: 8, fontSize: 14 }}>
                  <strong>Sources:</strong>
                  <ul>
                    {m.sources.map((s, j) => (
                      <li key={j}>
                        {s.source_document} — {s.section_title} ({s.collection})
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}

          {loading && pendingQuestion && (
            <div className="chat-typing">
              <p><strong>You:</strong> {pendingQuestion}</p>
              <Loader label="MediBot is thinking..." />
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {chatError && <p style={{ color: "crimson", marginBottom: 12 }}>{chatError}</p>}

        <form onSubmit={sendQuestion} style={{ display: "flex", gap: 8 }}>
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question..."
            style={{ flex: 1, padding: 10 }}
            disabled={loading}
          />
          <button type="submit" className="btn-primary" disabled={loading || !question.trim()}>
            {loading ? (
              <>
                <Loader size="sm" inline />
                Sending...
              </>
            ) : (
              "Send"
            )}
          </button>
        </form>
      </main>
    </div>
  );
}
