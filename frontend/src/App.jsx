import { useState, useRef, useEffect } from "react";

const TOOLS_CONFIG = {
  github: { label: "GitHub", color: "#f97316", icon: "⬡" },
  notion: { label: "Notion", color: "#fb923c", icon: "◈" },
  whatsapp: { label: "WhatsApp", color: "#4ade80", icon: "◎" },
  gmail: { label: "Gmail", color: "#ef4444", icon: "✉" },
  calendar: { label: "Calendar", color: "#60a5fa", icon: "◷" },
  memory: { label: "Memory", color: "#c084fc", icon: "◆" },
};

const SUGGESTIONS = [
  { icon: "⬡", text: "Check GitHub notifications & create Notion tasks" },
  { icon: "◎", text: "Send me a WhatsApp status update" },
  { icon: "◈", text: "Show all my Notion tasks" },
  { icon: "◆", text: "What do you remember about me?" },
];

function detectTools(text) {
  const t = text.toLowerCase();
  const found = [];
  if (t.includes("github") || t.includes("notif") || t.includes("pr") || t.includes("workflow")) found.push("github");
  if (t.includes("notion") || t.includes("task")) found.push("notion");
  if (t.includes("whatsapp") || t.includes("message") || t.includes("sent")) found.push("whatsapp");
  if (t.includes("gmail") || t.includes("email")) found.push("gmail");
  if (t.includes("calendar") || t.includes("event") || t.includes("schedule")) found.push("calendar");
  if (t.includes("memor") || t.includes("remember")) found.push("memory");
  return found;
}

function TypingDots() {
  return (
    <div style={{ display: "flex", gap: 5, padding: "12px 0 4px" }}>
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          style={{
            width: 7,
            height: 7,
            borderRadius: "50%",
            background: "#f97316",
            display: "inline-block",
            animation: `bounce 1.2s ease-in-out ${i * 0.2}s infinite`,
          }}
        />
      ))}
    </div>
  );
}

function Message({ msg }) {
  const isUser = msg.role === "user";
  const tools = msg.role === "assistant" ? detectTools(msg.content) : [];

  return (
    <div
      style={{
        display: "flex",
        flexDirection: isUser ? "row-reverse" : "row",
        alignItems: "flex-start",
        gap: 12,
        marginBottom: 24,
        animation: "fadeSlideUp 0.35s ease both",
      }}
    >
      {/* Avatar */}
      <div
        style={{
          width: 36,
          height: 36,
          borderRadius: isUser ? "10px 10px 2px 10px" : "10px 10px 10px 2px",
          background: isUser
            ? "linear-gradient(135deg,#f97316,#fb923c)"
            : "linear-gradient(135deg,#1a1a2e,#16213e)",
          border: isUser ? "none" : "1.5px solid #f97316",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 14,
          flexShrink: 0,
          boxShadow: isUser ? "0 0 16px #f9731650" : "0 0 16px #f9731630",
        }}
      >
        {isUser ? "✦" : "◈"}
      </div>

      <div style={{ maxWidth: "72%", display: "flex", flexDirection: "column", gap: 6 }}>
        {/* Tool pills */}
        {tools.length > 0 && (
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            {tools.map((t) => (
              <span
                key={t}
                style={{
                  fontSize: 10,
                  padding: "2px 8px",
                  borderRadius: 20,
                  border: `1px solid ${TOOLS_CONFIG[t].color}60`,
                  color: TOOLS_CONFIG[t].color,
                  background: `${TOOLS_CONFIG[t].color}15`,
                  letterSpacing: "0.05em",
                  fontFamily: "'Space Mono', monospace",
                }}
              >
                {TOOLS_CONFIG[t].icon} {TOOLS_CONFIG[t].label}
              </span>
            ))}
          </div>
        )}

        {/* Bubble */}
        <div
          style={{
            padding: "12px 16px",
            borderRadius: isUser
              ? "16px 4px 16px 16px"
              : "4px 16px 16px 16px",
            background: isUser
              ? "linear-gradient(135deg,#f97316,#ea580c)"
              : "rgba(255,255,255,0.04)",
            border: isUser ? "none" : "1px solid rgba(249,115,22,0.18)",
            color: isUser ? "#fff" : "#e2e2e2",
            fontSize: 14,
            lineHeight: 1.65,
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
            backdropFilter: "blur(10px)",
          }}
        >
          {msg.content}
        </div>

        <span
          style={{
            fontSize: 10,
            color: "#555",
            alignSelf: isUser ? "flex-end" : "flex-start",
            fontFamily: "'Space Mono', monospace",
          }}
        >
          {msg.time}
        </span>
      </div>
    </div>
  );
}

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "I'm ARIA — your Autonomous Retrieval & Interaction Agent.\n\nI'm connected to GitHub, Notion, and WhatsApp. Give me a command and I'll execute it across all your tools automatically.",
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ commands: 0, tools: 0 });
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const send = async (text) => {
    const msg = text || input.trim();
    if (!msg || loading) return;
    setInput("");

    const userMsg = {
      role: "user",
      content: msg,
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg }),
      });
      const data = await res.json();
      const replyText = data.response || data.error || "No response.";
      const tools = detectTools(replyText);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: replyText,
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
      setStats((s) => ({ commands: s.commands + 1, tools: s.tools + tools.length }));
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "⚠ Could not reach the ARIA backend. Make sure the FastAPI server is running.",
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Syne:wght@400;600;700;800&display=swap');

        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        body {
          background: #08080f;
          font-family: 'Syne', sans-serif;
          color: #e2e2e2;
          height: 100vh;
          overflow: hidden;
        }

        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #f9731640; border-radius: 4px; }

        @keyframes fadeSlideUp {
          from { opacity: 0; transform: translateY(10px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes bounce {
          0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
          40%            { transform: scale(1);   opacity: 1; }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50%       { opacity: 0.4; }
        }
        @keyframes scanline {
          0%   { transform: translateY(-100%); }
          100% { transform: translateY(100vh); }
        }
        @keyframes gridFade {
          from { opacity: 0; }
          to   { opacity: 1; }
        }

        textarea {
          resize: none;
          outline: none;
          border: none;
          background: transparent;
          font-family: 'Syne', sans-serif;
          font-size: 14px;
          color: #e2e2e2;
          width: 100%;
          line-height: 1.5;
        }
        textarea::placeholder { color: #444; }

        button { cursor: pointer; border: none; outline: none; }

        .suggestion-btn {
          background: rgba(249,115,22,0.06);
          border: 1px solid rgba(249,115,22,0.2) !important;
          color: #ccc;
          padding: 8px 12px;
          border-radius: 10px;
          font-family: 'Syne', sans-serif;
          font-size: 12px;
          text-align: left;
          transition: all 0.2s;
          cursor: pointer;
        }
        .suggestion-btn:hover {
          background: rgba(249,115,22,0.12);
          border-color: rgba(249,115,22,0.5) !important;
          color: #f97316;
          transform: translateY(-1px);
        }

        .send-btn {
          width: 40px; height: 40px;
          border-radius: 12px;
          background: linear-gradient(135deg,#f97316,#ea580c);
          display: flex; align-items: center; justify-content: center;
          font-size: 16px;
          transition: all 0.2s;
          flex-shrink: 0;
        }
        .send-btn:hover { transform: scale(1.08); box-shadow: 0 0 20px #f9731660; }
        .send-btn:disabled { opacity: 0.4; transform: none; }
      `}</style>

      <div style={{ display: "flex", height: "100vh", position: "relative", overflow: "hidden" }}>

        {/* Background grid */}
        <div
          style={{
            position: "fixed", inset: 0, pointerEvents: "none", zIndex: 0,
            backgroundImage: `
              linear-gradient(rgba(249,115,22,0.04) 1px, transparent 1px),
              linear-gradient(90deg, rgba(249,115,22,0.04) 1px, transparent 1px)
            `,
            backgroundSize: "40px 40px",
            animation: "gridFade 2s ease both",
          }}
        />

        {/* Scanline */}
        <div
          style={{
            position: "fixed", left: 0, right: 0, height: "2px",
            background: "linear-gradient(90deg, transparent, rgba(249,115,22,0.15), transparent)",
            animation: "scanline 8s linear infinite",
            pointerEvents: "none", zIndex: 1,
          }}
        />

        {/* ── SIDEBAR ── */}
        <aside
          style={{
            width: 240,
            flexShrink: 0,
            borderRight: "1px solid rgba(249,115,22,0.12)",
            background: "rgba(10,10,20,0.8)",
            backdropFilter: "blur(20px)",
            display: "flex",
            flexDirection: "column",
            padding: "28px 20px",
            gap: 28,
            position: "relative",
            zIndex: 2,
          }}
        >
          {/* Logo */}
          <div>
            <div
              style={{
                fontSize: 26,
                fontWeight: 800,
                letterSpacing: "0.12em",
                color: "#f97316",
                textShadow: "0 0 30px #f9731660",
                fontFamily: "'Space Mono', monospace",
              }}
            >
              ◈ ARIA
            </div>
            <div style={{ fontSize: 10, color: "#555", letterSpacing: "0.2em", marginTop: 4, fontFamily: "'Space Mono', monospace" }}>
              AUTONOMOUS AGENT v1.0
            </div>
          </div>

          {/* Status */}
          <div>
            <div style={{ fontSize: 10, color: "#f97316", letterSpacing: "0.2em", marginBottom: 14, fontFamily: "'Space Mono', monospace" }}>
              SYSTEM STATUS
            </div>
            {[
              { label: "Core Engine", status: "ONLINE", color: "#4ade80" },
              { label: "Groq LLM", status: "ONLINE", color: "#4ade80" },
              { label: "Tool Router", status: "ACTIVE", color: "#f97316" },
              { label: "Memory", status: "ACTIVE", color: "#f97316" },
            ].map((s) => (
              <div key={s.label} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                <span style={{ fontSize: 12, color: "#888" }}>{s.label}</span>
                <span style={{ fontSize: 10, color: s.color, fontFamily: "'Space Mono', monospace", display: "flex", alignItems: "center", gap: 5 }}>
                  <span style={{ width: 5, height: 5, borderRadius: "50%", background: s.color, display: "inline-block", animation: "pulse 2s ease-in-out infinite" }} />
                  {s.status}
                </span>
              </div>
            ))}
          </div>

          {/* Tools */}
          <div>
            <div style={{ fontSize: 10, color: "#f97316", letterSpacing: "0.2em", marginBottom: 14, fontFamily: "'Space Mono', monospace" }}>
              CONNECTED TOOLS
            </div>
            {Object.entries(TOOLS_CONFIG).map(([key, t]) => (
              <div key={key} style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
                <span style={{ color: t.color, fontSize: 14 }}>{t.icon}</span>
                <span style={{ fontSize: 12, color: "#aaa" }}>{t.label}</span>
                <span style={{ marginLeft: "auto", width: 5, height: 5, borderRadius: "50%", background: t.color, animation: "pulse 2s ease-in-out infinite" }} />
              </div>
            ))}
          </div>

          {/* Stats */}
          <div style={{ marginTop: "auto" }}>
            <div style={{ fontSize: 10, color: "#f97316", letterSpacing: "0.2em", marginBottom: 14, fontFamily: "'Space Mono', monospace" }}>
              SESSION STATS
            </div>
            {[
              { label: "Commands", value: stats.commands },
              { label: "Tool Calls", value: stats.tools },
            ].map((s) => (
              <div key={s.label} style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                <span style={{ fontSize: 12, color: "#666" }}>{s.label}</span>
                <span style={{ fontSize: 12, color: "#f97316", fontFamily: "'Space Mono', monospace" }}>{s.value}</span>
              </div>
            ))}
          </div>
        </aside>

        {/* ── MAIN ── */}
        <main style={{ flex: 1, display: "flex", flexDirection: "column", position: "relative", zIndex: 2, overflow: "hidden" }}>

          {/* Header */}
          <div
            style={{
              padding: "18px 28px",
              borderBottom: "1px solid rgba(249,115,22,0.1)",
              background: "rgba(8,8,15,0.6)",
              backdropFilter: "blur(20px)",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <div>
              <div style={{ fontSize: 15, fontWeight: 700, letterSpacing: "0.05em" }}>Autonomous Session</div>
              <div style={{ fontSize: 11, color: "#555", fontFamily: "'Space Mono', monospace", marginTop: 2 }}>
                {new Date().toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "short" })}
              </div>
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              {Object.values(TOOLS_CONFIG).slice(0, 4).map((t) => (
                <div
                  key={t.label}
                  title={t.label}
                  style={{
                    width: 28, height: 28, borderRadius: 8,
                    border: `1px solid ${t.color}40`,
                    background: `${t.color}10`,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: 12, color: t.color,
                  }}
                >
                  {t.icon}
                </div>
              ))}
            </div>
          </div>

          {/* Messages */}
          <div
            style={{
              flex: 1,
              overflowY: "auto",
              padding: "28px 32px",
            }}
          >
            {messages.map((m, i) => <Message key={i} msg={m} />)}
            {loading && (
              <div style={{ display: "flex", alignItems: "flex-start", gap: 12, animation: "fadeSlideUp 0.3s ease" }}>
                <div style={{
                  width: 36, height: 36, borderRadius: "10px 10px 10px 2px",
                  background: "linear-gradient(135deg,#1a1a2e,#16213e)",
                  border: "1.5px solid #f97316",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 14, flexShrink: 0,
                }}>◈</div>
                <div style={{
                  padding: "10px 16px",
                  borderRadius: "4px 16px 16px 16px",
                  background: "rgba(255,255,255,0.04)",
                  border: "1px solid rgba(249,115,22,0.18)",
                }}>
                  <TypingDots />
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Suggestions */}
          {messages.length <= 1 && (
            <div style={{ padding: "0 32px 16px", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
              {SUGGESTIONS.map((s, i) => (
                <button key={i} className="suggestion-btn" onClick={() => send(s.text)}>
                  <span style={{ color: "#f97316", marginRight: 6 }}>{s.icon}</span>
                  {s.text}
                </button>
              ))}
            </div>
          )}

          {/* Input */}
          <div
            style={{
              padding: "16px 28px 20px",
              borderTop: "1px solid rgba(249,115,22,0.1)",
              background: "rgba(8,8,15,0.7)",
              backdropFilter: "blur(20px)",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "flex-end",
                gap: 12,
                background: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(249,115,22,0.25)",
                borderRadius: 16,
                padding: "12px 16px",
                transition: "border-color 0.2s",
              }}
              onFocus={(e) => e.currentTarget.style.borderColor = "rgba(249,115,22,0.6)"}
              onBlur={(e) => e.currentTarget.style.borderColor = "rgba(249,115,22,0.25)"}
            >
              <textarea
                ref={inputRef}
                rows={1}
                value={input}
                onChange={(e) => {
                  setInput(e.target.value);
                  e.target.style.height = "auto";
                  e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px";
                }}
                onKeyDown={handleKey}
                placeholder="Give ARIA a command..."
                disabled={loading}
              />
              <button className="send-btn" onClick={() => send()} disabled={loading || !input.trim()}>
                {loading ? (
                  <span style={{ fontSize: 12, animation: "pulse 1s infinite" }}>◈</span>
                ) : "→"}
              </button>
            </div>
            <div style={{ fontSize: 10, color: "#333", marginTop: 8, textAlign: "center", fontFamily: "'Space Mono', monospace" }}>
              ENTER to send · SHIFT+ENTER for new line · Powered by Groq Llama 3.3-70B
            </div>
          </div>
        </main>
      </div>
    </>
  );
}
