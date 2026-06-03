// ========== 面试对话页 ==========

import { useState, useEffect, useRef } from "react";
import { useNavigate, useParams } from "react-router-dom";
import * as api from "../api/client";
import type { SSEEvent, RoundScore } from "../types";

interface ChatMessage {
  role: "ai" | "user";
  content: string;
  score?: RoundScore;
}

const s = {
  page: {
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column" as const,
    background: "var(--bg-primary)",
  },
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "14px 24px",
    background: "var(--bg-card)",
    borderBottom: "1px solid var(--border)",
  },
  headerInfo: {
    display: "flex",
    alignItems: "center",
    gap: "16px",
    fontSize: "0.84rem",
  } as React.CSSProperties,
  pill: {
    padding: "4px 12px",
    borderRadius: "20px",
    fontSize: "0.78rem",
    fontWeight: 500,
  } as React.CSSProperties,
  chatArea: {
    flex: 1,
    overflowY: "auto" as const,
    padding: "24px 16px 40px",
  },
  chatInner: {
    maxWidth: "680px",
    margin: "0 auto",
    display: "flex",
    flexDirection: "column" as const,
    gap: "20px",
  },
  bubble: (role: "ai" | "user") =>
    ({
      maxWidth: "82%",
      alignSelf: role === "user" ? "flex-end" : "flex-start",
      padding: role === "user" ? "12px 18px" : "16px 20px",
      borderRadius:
        role === "user" ? "var(--radius-lg) var(--radius-lg) 4px var(--radius-lg)" : "var(--radius-lg) var(--radius-lg) var(--radius-lg) 4px",
      background: role === "user" ? "var(--accent)" : "var(--bg-card)",
      border: role === "user" ? "none" : "1px solid var(--border)",
      color: role === "user" ? "white" : "var(--text-primary)",
      fontSize: "0.9rem",
      lineHeight: 1.7,
      boxShadow: role === "user" ? "var(--shadow-sm)" : "none",
    } as React.CSSProperties),
  scoreCard: {
    marginTop: "12px",
    padding: "12px 14px",
    background: "var(--bg-secondary)",
    borderRadius: "var(--radius-sm)",
    display: "flex",
    gap: "14px",
    fontSize: "0.78rem",
    flexWrap: "wrap" as const,
  } as React.CSSProperties,
  inputArea: {
    padding: "16px 24px",
    background: "var(--bg-card)",
    borderTop: "1px solid var(--border)",
  },
  inputRow: {
    maxWidth: "680px",
    margin: "0 auto",
    display: "flex",
    gap: "10px",
  },
  input: {
    flex: 1,
    padding: "12px 16px",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius)",
    background: "var(--bg-secondary)",
    color: "var(--text-primary)",
    fontSize: "0.9rem",
  } as React.CSSProperties,
  sendBtn: (disabled: boolean) =>
    ({
      padding: "12px 22px",
      background: disabled ? "var(--text-muted)" : "var(--accent)",
      color: "white",
      border: "none",
      borderRadius: "var(--radius)",
      fontWeight: 500,
      fontSize: "0.9rem",
      cursor: disabled ? "not-allowed" : "pointer",
      opacity: disabled ? 0.4 : 1,
      transition: "background 0.15s",
      whiteSpace: "nowrap" as const,
    } as React.CSSProperties),
  endBtn: {
    padding: "8px 16px",
    background: "transparent",
    color: "var(--text-muted)",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius-sm)",
    fontSize: "0.82rem",
    cursor: "pointer",
    transition: "all 0.15s",
  } as React.CSSProperties,
};

export default function Interview() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const chatEndRef = useRef<HTMLDivElement>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [currentRound, setCurrentRound] = useState(1);
  const [mainIdx, setMainIdx] = useState(0);
  const [followupCount, setFollowupCount] = useState(0);
  const [nextType, setNextType] = useState<"main" | "followup">("main");
  const [error, setError] = useState("");

  useEffect(() => {
    const saved = sessionStorage.getItem("interview_state");
    if (saved) {
      const state = JSON.parse(saved);
      if (state.messages) {
        setMessages(
          state.messages.map((m: any) => ({
            role: m.type === "human" ? "user" : "ai",
            content: m.content,
          }))
        );
      }
      setCurrentRound(state.currentRound || 1);
      setMainIdx(state.mainQuestionIndex || 0);
      setFollowupCount(state.followupCount || 0);
    }
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async () => {
    if (!input.trim() || loading || !sessionId) return;
    const answer = input.trim();
    setInput("");
    setError("");
    setMessages((prev) => [...prev, { role: "user", content: answer }]);
    setLoading(true);

    await api.submitAnswerSSE(
      sessionId,
      answer,
      (event: SSEEvent) => {
        switch (event.node) {
          case "evaluate":
            if (event.round_scores?.[0]) {
              setMessages((prev) => {
                const updated = [...prev];
                const idx = updated.map((m) => m.role).lastIndexOf("user");
                if (idx >= 0) updated[idx] = { ...updated[idx], score: event.round_scores![event.round_scores!.length - 1] };
                return updated;
              });
            }
            break;
          case "advance_question":
            setNextType((event.next_question_type || "main") as "main" | "followup");
            setMainIdx(event.main_question_index || 0);
            setFollowupCount(event.followup_count || 0);
            break;
          case "ask_question":
            if (event.question) {
              setMessages((prev) => [...prev, { role: "ai", content: event.question! }]);
            }
            break;
          case "final_report":
            if (event.final_report) {
              sessionStorage.setItem("final_report", JSON.stringify(event.final_report));
            }
            break;
          case "increment_round":
            setCurrentRound(event.current_round || currentRound + 1);
            break;
        }
      },
      () => {
        setLoading(false);
        const report = sessionStorage.getItem("final_report");
        if (report) navigate(`/report/${sessionId}`);
      },
      (err) => {
        setError(err);
        setLoading(false);
      }
    );
  };

  const handleEnd = async () => {
    if (!sessionId || loading) return;
    setLoading(true);
    await api.endInterviewSSE(
      sessionId,
      (event) => {
        if (event.node === "final_report" && event.final_report) {
          sessionStorage.setItem("final_report", JSON.stringify(event.final_report));
        }
      },
      () => navigate(`/report/${sessionId}`),
      (err) => setError(err)
    );
  };

  return (
    <div style={s.page}>
      {/* 顶栏 */}
      <div style={s.header}>
        <div style={s.headerInfo}>
          <span style={{ color: "var(--text-muted)" }}>
            第 <b style={{ color: "var(--text-primary)" }}>{currentRound}</b> 轮
          </span>
          <span style={{ color: "var(--border)" }}>·</span>
          <span style={{ color: "var(--text-muted)" }}>
            主问题 <b style={{ color: "var(--text-primary)" }}>{mainIdx + 1}</b>/5
          </span>
          {nextType === "followup" && (
            <span style={{ ...s.pill, background: "rgba(245,158,11,0.1)", color: "#f59e0b" }}>
              追问 {followupCount}/3
            </span>
          )}
        </div>
        <button
          style={s.endBtn}
          onClick={handleEnd}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = "#ef4444";
            e.currentTarget.style.color = "#ef4444";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = "var(--border)";
            e.currentTarget.style.color = "var(--text-muted)";
          }}
        >
          结束面试
        </button>
      </div>

      {/* 对话区 */}
      <div style={s.chatArea}>
        <div style={s.chatInner}>
          {messages.map((msg, i) => (
            <div key={i} style={s.bubble(msg.role)}>
              <p style={{ margin: 0, whiteSpace: "pre-wrap" }}>{msg.content}</p>
              {msg.score && (
                <div style={s.scoreCard}>
                  <span style={{ color: "#10b981", fontWeight: 500 }}>技术 {msg.score.tech_score}/10</span>
                  <span style={{ color: "#6366f1", fontWeight: 500 }}>沟通 {msg.score.communication_score}/10</span>
                  <span style={{ color: "#8b5cf6", fontWeight: 500 }}>逻辑 {msg.score.logic_score}/10</span>
                  {msg.score.brief_comment && (
                    <span style={{ width: "100%", color: "var(--text-muted)", fontSize: "0.76rem", marginTop: "4px" }}>
                      {msg.score.brief_comment}
                    </span>
                  )}
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div style={{ ...s.bubble("ai"), display: "flex", gap: "8px", alignItems: "center", padding: "14px 20px" }}>
              <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--text-muted)", animation: "pulse 1.4s infinite" }} />
              <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--text-muted)", animation: "pulse 1.4s infinite 0.2s" }} />
              <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--text-muted)", animation: "pulse 1.4s infinite 0.4s" }} />
            </div>
          )}

          {error && (
            <div style={{ textAlign: "center", padding: "12px", fontSize: "0.82rem", color: "#ef4444", background: "rgba(239,68,68,0.06)", borderRadius: "var(--radius-sm)" }}>
              {error}
            </div>
          )}

          <div ref={chatEndRef} />
        </div>
      </div>

      {/* 输入区 */}
      <div style={s.inputArea}>
        <div style={s.inputRow}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSubmit()}
            placeholder={loading ? "面试官思考中..." : "输入你的回答..."}
            disabled={loading}
            style={s.input}
          />
          <button
            onClick={handleSubmit}
            disabled={loading || !input.trim()}
            style={s.sendBtn(loading || !input.trim())}
          >
            发送
          </button>
        </div>
      </div>

      {/* CSS 动画 */}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 0.3; }
          50% { opacity: 1; }
        }
      `}</style>
    </div>
  );
}
