// ========== 面试对话页（无抖动版）==========

import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate, useParams } from "react-router-dom";
import * as api from "../api/client";
import type { SSEEvent, RoundScore } from "../types";

interface ChatMessage {
  role: "ai" | "user";
  content: string;
  score?: RoundScore;
}

export default function Interview() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const scrollRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [currentRound, setCurrentRound] = useState(1);
  const [mainIdx, setMainIdx] = useState(0);
  const [followupCount, setFollowupCount] = useState(0);
  const [nextType, setNextType] = useState<"main" | "followup">("main");
  const [error, setError] = useState("");

  // 恢复状态
  useEffect(() => {
    const saved = sessionStorage.getItem("interview_state");
    if (saved) {
      const state = JSON.parse(saved);
      if (state.messages) {
        setMessages(state.messages.map((m: any) => ({ role: m.type === "human" ? "user" : "ai", content: m.content })));
      }
      setCurrentRound(state.currentRound || 1);
      setMainIdx(state.mainQuestionIndex || 0);
      setFollowupCount(state.followupCount || 0);
    }
  }, []);

  // 自动滚动 —— 使用 scrollTop 而不是 scrollIntoView，彻底消除抖动
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const handleSubmit = useCallback(async () => {
    if (!input.trim() || loading || !sessionId) return;
    const answer = input.trim();
    setInput("");
    setError("");
    setMessages(prev => [...prev, { role: "user", content: answer }]);
    setLoading(true);

    await api.submitAnswerSSE(sessionId, answer,
      (event: SSEEvent) => {
        switch (event.node) {
          case "evaluate":
            if (event.round_scores?.[event.round_scores.length - 1]) {
              setMessages(prev => {
                const updated = [...prev];
                const idx = updated.map(m => m.role).lastIndexOf("user");
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
            if (event.question) setMessages(prev => [...prev, { role: "ai", content: event.question! }]);
            break;
          case "final_report":
            if (event.final_report) sessionStorage.setItem("final_report", JSON.stringify(event.final_report));
            break;
          case "increment_round":
            setCurrentRound(event.current_round || currentRound + 1);
            break;
        }
      },
      () => {
        setLoading(false);
        if (sessionStorage.getItem("final_report")) navigate(`/report/${sessionId}`);
      },
      (err) => { setError(err); setLoading(false); }
    );
  }, [input, loading, sessionId, currentRound, navigate]);

  const handleEnd = useCallback(async () => {
    if (!sessionId || loading) return;
    setLoading(true);
    await api.endInterviewSSE(sessionId,
      (event) => { if (event.node === "final_report" && event.final_report) sessionStorage.setItem("final_report", JSON.stringify(event.final_report)); },
      () => navigate(`/report/${sessionId}`),
      (err) => setError(err)
    );
  }, [sessionId, loading, navigate]);

  const s = {
    page: { minHeight: "100vh", display: "flex", flexDirection: "column" as const, background: "var(--bg-base)" },
    header: { display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 20px", background: "var(--bg-surface)", borderBottom: "1px solid var(--border)" },
    pill: { padding: "3px 10px", borderRadius: 12, fontSize: "0.74rem", fontWeight: 500 } as React.CSSProperties,
    chat: { flex: 1, overflowY: "auto" as const, padding: "20px 16px 32px" },
    chatInner: { maxWidth: "660px", margin: "0 auto", display: "flex", flexDirection: "column" as const, gap: "16px" },
    bubble: (role: "ai" | "user") => ({
      maxWidth: "82%", alignSelf: role === "user" ? "flex-end" : "flex-start",
      padding: role === "user" ? "11px 16px" : "14px 18px",
      borderRadius: role === "user" ? "var(--radius-lg) var(--radius-lg) 4px var(--radius-lg)" : "var(--radius-lg) var(--radius-lg) var(--radius-lg) 4px",
      background: role === "user" ? "var(--accent)" : "var(--bg-card)",
      border: role === "user" ? "none" : "1px solid var(--border)",
      color: role === "user" ? "white" : "var(--text-primary)",
      fontSize: "0.88rem", lineHeight: 1.65,
    } as React.CSSProperties),
    scoreRow: { marginTop: 10, display: "flex", gap: 12, flexWrap: "wrap" as const, fontSize: "0.74rem", color: "var(--text-muted)" } as React.CSSProperties,
    footer: { padding: "14px 20px", background: "var(--bg-surface)", borderTop: "1px solid var(--border)" },
    footerRow: { maxWidth: "660px", margin: "0 auto", display: "flex", gap: 10 },
    inp: { flex: 1, padding: "11px 16px", border: "1px solid var(--border-light)", borderRadius: "var(--radius)", background: "var(--bg-base)", color: "var(--text-primary)", fontSize: "0.88rem", outline: "none" } as React.CSSProperties,
    snd: (d: boolean) => ({ padding: "11px 20px", background: d ? "var(--text-muted)" : "var(--accent)", color: "white", border: "none", borderRadius: "var(--radius)", fontWeight: 500, fontSize: "0.88rem", cursor: d ? "not-allowed" : "pointer", opacity: d ? 0.4 : 1, whiteSpace: "nowrap" as const, transition: "background 0.15s" } as React.CSSProperties),
    endBtn: { padding: "6px 14px", background: "transparent", color: "var(--text-muted)", border: "1px solid var(--border)", borderRadius: "var(--radius-sm)", fontSize: "0.8rem", cursor: "pointer" } as React.CSSProperties,
  };

  return (
    <div style={s.page}>
      {/* 顶栏 */}
      <div style={s.header}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, fontSize: "0.82rem" }}>
          <span style={{ color: "var(--text-muted)" }}>第 <b style={{ color: "var(--text-primary)" }}>{currentRound}</b> 轮</span>
          <span style={{ color: "var(--border)" }}>·</span>
          <span style={{ color: "var(--text-muted)" }}>主问题 <b style={{ color: "var(--text-primary)" }}>{mainIdx + 1}</b>/5</span>
          {nextType === "followup" && <span style={{ ...s.pill, background: "rgba(245,158,11,0.1)", color: "var(--orange)" }}>追问 {followupCount}/3</span>}
        </div>
        <button style={s.endBtn} onClick={handleEnd}
          onMouseEnter={e => { e.currentTarget.style.borderColor = "var(--red)"; e.currentTarget.style.color = "var(--red)"; }}
          onMouseLeave={e => { e.currentTarget.style.borderColor = "var(--border)"; e.currentTarget.style.color = "var(--text-muted)"; }}>
          结束面试
        </button>
      </div>

      {/* 对话区 —— 关键：overflow-anchor 消除滚动抖动 */}
      <div ref={scrollRef} style={s.chat}>
        <div style={s.chatInner}>
          {messages.map((msg, i) => (
            <div key={i} style={s.bubble(msg.role)}>
              <p style={{ margin: 0, whiteSpace: "pre-wrap" }}>{msg.content}</p>
              {msg.score && (
                <div style={s.scoreRow}>
                  <span style={{ color: "var(--green)", fontWeight: 500 }}>技术 {msg.score.tech_score}/10</span>
                  <span style={{ color: "var(--accent-hover)", fontWeight: 500 }}>沟通 {msg.score.communication_score}/10</span>
                  <span style={{ color: "#a78bfa", fontWeight: 500 }}>逻辑 {msg.score.logic_score}/10</span>
                  {msg.score.brief_comment && <span style={{ width: "100%", fontSize: "0.72rem", marginTop: 2 }}>{msg.score.brief_comment}</span>}
                </div>
              )}
            </div>
          ))}

          {/* 加载指示器 — 固定高度避免布局跳动 */}
          {loading && (
            <div style={{ ...s.bubble("ai"), display: "flex", gap: 6, alignItems: "center", padding: "14px 18px", minHeight: 44 }}>
              <span style={{ width: 5, height: 5, borderRadius: "50%", background: "var(--text-muted)", animation: "dotPulse 1.4s infinite ease-in-out" }} />
              <span style={{ width: 5, height: 5, borderRadius: "50%", background: "var(--text-muted)", animation: "dotPulse 1.4s infinite ease-in-out 0.2s" }} />
              <span style={{ width: 5, height: 5, borderRadius: "50%", background: "var(--text-muted)", animation: "dotPulse 1.4s infinite ease-in-out 0.4s" }} />
            </div>
          )}

          {error && <div style={{ textAlign: "center", padding: 10, fontSize: "0.8rem", color: "var(--red)", background: "rgba(248,113,113,0.08)", borderRadius: "var(--radius-sm)" }}>{error}</div>}
          <div ref={bottomRef} />
        </div>
      </div>

      {/* 输入区 */}
      <div style={s.footer}>
        <div style={s.footerRow}>
          <input type="text" value={input} onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && !e.shiftKey && handleSubmit()}
            placeholder={loading ? "面试官思考中..." : "输入回答..."} disabled={loading} style={s.inp} />
          <button onClick={handleSubmit} disabled={loading || !input.trim()} style={s.snd(loading || !input.trim())}>发送</button>
        </div>
      </div>

      <style>{`@keyframes dotPulse { 0%,100%{opacity:0.2} 50%{opacity:1} }`}</style>
    </div>
  );
}
