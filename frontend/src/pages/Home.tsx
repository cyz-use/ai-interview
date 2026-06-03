// ========== 首页 ==========

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import * as api from "../api/client";
import type { DemoResumeItem, SubscriptionStatus, PaymentInfo } from "../types";

const C = {
  page: { minHeight: "100vh", background: "var(--bg-base)", padding: "60px 16px" } as React.CSSProperties,
  wrap: { maxWidth: "620px", margin: "0 auto" } as React.CSSProperties,
  card: { background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: "var(--radius-lg)", padding: "28px 24px" } as React.CSSProperties,
  label: { display: "block", fontSize: "0.8rem", fontWeight: 500, color: "var(--text-secondary)", marginBottom: 6 } as React.CSSProperties,
  select: { width: "100%", padding: "11px 14px", border: "1px solid var(--border-light)", borderRadius: "var(--radius-sm)", background: "var(--bg-base)", color: "var(--text-primary)", fontSize: "0.88rem", outline: "none", appearance: "none" as const, cursor: "pointer" } as React.CSSProperties,
  input: { width: "100%", padding: "11px 14px", border: "1px solid var(--border-light)", borderRadius: "var(--radius-sm)", background: "var(--bg-base)", color: "var(--text-primary)", fontSize: "0.88rem", outline: "none" } as React.CSSProperties,
  textarea: { width: "100%", padding: "12px 14px", border: "1px solid var(--border-light)", borderRadius: "var(--radius-sm)", background: "var(--bg-base)", color: "var(--text-primary)", fontSize: "0.85rem", resize: "none" as const, lineHeight: 1.6, outline: "none" } as React.CSSProperties,
  btn: (d: boolean) => ({ width: "100%", padding: "13px", background: d ? "var(--text-muted)" : "var(--accent)", color: "white", border: "none", borderRadius: "var(--radius)", fontWeight: 500, fontSize: "0.93rem", cursor: d ? "not-allowed" : "pointer", opacity: d ? 0.5 : 1, transition: "background 0.15s" } as React.CSSProperties),
  tab: (a: boolean) => ({ flex: 1, padding: "10px", textAlign: "center" as const, fontSize: "0.84rem", fontWeight: a ? 500 : 400, color: a ? "var(--accent)" : "var(--text-muted)", background: a ? "var(--accent-glow)" : "transparent", border: "none", borderRadius: "var(--radius-sm)", cursor: "pointer", transition: "all 0.15s" } as React.CSSProperties),
  preview: { background: "var(--bg-base)", border: "1px solid var(--border)", borderRadius: "var(--radius-sm)", padding: "14px", maxHeight: "170px", overflowY: "auto" as const, fontSize: "0.8rem", color: "var(--text-secondary)", lineHeight: 1.7, whiteSpace: "pre-wrap" as const } as React.CSSProperties,
};

function PaymentModal({ onClose }: { onClose: () => void }) {
  const [info, setInfo] = useState<PaymentInfo | null>(null);
  useEffect(() => { api.getPaymentInfo().then(setInfo).catch(() => {}); }, []);

  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 100, display: "flex", alignItems: "center", justifyContent: "center", background: "rgba(0,0,0,0.7)", backdropFilter: "blur(4px)" }} onClick={onClose}>
      <div style={{ ...C.card, maxWidth: 360, width: "90%", textAlign: "center" }} onClick={e => e.stopPropagation()}>
        <h3 style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--text-primary)", marginBottom: 6 }}>升级会员</h3>
        <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", marginBottom: 22 }}>免费试用已用完</p>
        <div style={{ display: "flex", gap: 10, marginBottom: 22 }}>
          <div style={{ flex: 1, padding: "14px 10px", borderRadius: "var(--radius)", border: "1px solid var(--border)", background: "var(--bg-base)" }}>
            <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: 2 }}>月度</p>
            <p style={{ fontSize: "1.6rem", fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>¥{info?.price_monthly || 29}</p>
          </div>
          <div style={{ flex: 1, padding: "14px 10px", borderRadius: "var(--radius)", border: "2px solid var(--accent)", background: "var(--accent-glow)", position: "relative" }}>
            <span style={{ position: "absolute", top: -10, right: 10, background: "var(--accent)", color: "white", padding: "2px 8px", borderRadius: 10, fontSize: "0.68rem" }}>推荐</span>
            <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: 2 }}>年度</p>
            <p style={{ fontSize: "1.6rem", fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>¥{info?.price_yearly || 199}</p>
          </div>
        </div>
        <div style={{ padding: 12, borderRadius: "var(--radius-sm)", background: "var(--bg-base)", border: "1px solid var(--border)", fontSize: "0.78rem", color: "var(--text-secondary)", lineHeight: 1.7, textAlign: "left" }}>
          {info?.contact || "付款后联系客服升级会员"}
        </div>
        <button onClick={onClose} style={{ marginTop: 18, padding: "8px 28px", background: "transparent", color: "var(--text-muted)", border: "1px solid var(--border)", borderRadius: "var(--radius-sm)", cursor: "pointer", fontSize: "0.82rem" }}>稍后再说</button>
      </div>
    </div>
  );
}

export default function Home() {
  const nav = useNavigate();
  const [tab, setTab] = useState<"demo" | "upload" | "paste">("demo");
  const [cats, setCats] = useState<string[]>([]);
  const [cat, setCat] = useState("");
  const [resumes, setRes] = useState<DemoResumeItem[]>([]);
  const [idx, setIdx] = useState(-1);
  const [txt, setTxt] = useState("");
  const [job, setJob] = useState("");
  const [upTxt, setUp] = useState("");
  const [pasted, setPasted] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [sub, setSub] = useState<SubscriptionStatus | null>(null);
  const [pay, setPay] = useState(false);

  useEffect(() => { api.getDemoCategories().then(r => setCats(r.categories)).catch(() => {}); }, []);
  useEffect(() => { if (cat && tab === "demo") api.getDemoResumeList(cat).then(r => setRes(r.items)).catch(() => {}); }, [cat, tab]);
  useEffect(() => { if (idx >= 0 && cat && tab === "demo") { setLoading(true); api.getDemoResumeDetail(cat, idx).then(r => setTxt(r.text)).catch(e => setErr(e.message)).finally(() => setLoading(false)); } }, [idx, cat, tab]);
  useEffect(() => { api.getSubscriptionStatus().then(setSub).catch(() => {}); }, []);

  const text = tab === "demo" ? txt : tab === "upload" ? upTxt : pasted;
  const ok = text.trim().length > 0 && job.trim().length > 0;

  const go = async () => {
    if (!ok) return;
    if (sub && !sub.can_interview) { setPay(true); return; }
    setLoading(true); setErr("");
    try {
      const r = await api.startInterview(text, job);
      sessionStorage.setItem("interview_state", JSON.stringify({ sessionId: r.session_id, targetJob: job, candidateProfile: r.candidate_profile, messages: [{ type: "ai", content: r.first_question }], roundScores: [], mainQuestionIndex: 0, followupCount: 0, currentRound: 1, interviewCompleted: false }));
      api.getSubscriptionStatus().then(setSub).catch(() => {});
      nav(`/interview/${r.session_id}`);
    } catch (e: any) {
      if (e.message?.includes("试用") || e.message?.includes("402")) setPay(true);
      else setErr(e.message);
    } finally { setLoading(false); }
  };

  const pct = sub ? (sub.trial_interviews_used / sub.max_trial_interviews) * 100 : 0;
  const rem = sub?.trial_remaining ?? 3;

  return (
    <div style={C.page}>
      <div style={C.wrap}>
        {/* 头部 */}
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <div style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: 44, height: 44, background: "var(--accent-glow)", borderRadius: "var(--radius)", marginBottom: 14 }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
          </div>
          <h1 style={{ fontSize: "1.7rem", fontWeight: 600, color: "var(--text-primary)", letterSpacing: "-0.03em", margin: "0 0 6px" }}>AI 模拟面试</h1>
          <p style={{ fontSize: "0.88rem", color: "var(--text-muted)", margin: 0 }}>多智能体协同评估 · 自适应追问</p>
        </div>

        {/* 试用状态 */}
        {sub && (
          <div style={{ ...C.card, marginBottom: 18, padding: "16px 20px" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: sub.subscription_tier === "free" ? 8 : 0 }}>
              <span style={{ fontSize: "0.83rem", fontWeight: 500, color: sub.subscription_tier === "pro" ? "var(--green)" : "var(--text-primary)" }}>
                {sub.subscription_tier === "pro" ? "Pro 会员" : `免费试用 · 剩余 ${rem} 次`}
              </span>
              {sub.subscription_tier === "free" && (
                <button onClick={() => setPay(true)} style={{ padding: "5px 12px", background: "var(--accent-glow)", color: "var(--accent)", border: "1px solid var(--accent-glow)", borderRadius: 14, fontSize: "0.76rem", fontWeight: 500, cursor: "pointer" }}>升级</button>
              )}
            </div>
            {sub.subscription_tier === "free" && (
              <div style={{ height: 3, background: "var(--bg-base)", borderRadius: 2, overflow: "hidden" }}>
                <div style={{ height: "100%", width: `${pct}%`, background: pct >= 100 ? "var(--red)" : "var(--accent)", borderRadius: 2, transition: "width 0.4s ease" }} />
              </div>
            )}
          </div>
        )}

        {/* 主卡片 */}
        <div style={C.card}>
          <div style={{ display: "flex", gap: 4, padding: 3, background: "var(--bg-base)", borderRadius: "var(--radius-sm)", marginBottom: 24 }}>
            {(["demo", "upload", "paste"] as const).map(t => (
              <button key={t} style={C.tab(tab === t)} onClick={() => setTab(t)}>{t === "demo" ? "模拟简历" : t === "upload" ? "上传简历" : "粘贴内容"}</button>
            ))}
          </div>

          {tab === "demo" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
              <div><label style={C.label}>岗位类别</label>
                <select style={C.select} value={cat} onChange={e => { setCat(e.target.value); setIdx(-1); setTxt(""); }}>
                  <option value="">选择岗位（{cats.length} 个类别）</option>
                  {cats.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              {resumes.length > 0 && (
                <div><label style={C.label}>选择简历（{resumes.length} 份）</label>
                  <select style={C.select} value={idx} onChange={e => setIdx(Number(e.target.value))}>
                    <option value={-1}>选择一份简历</option>
                    {resumes.map(r => <option key={r.index} value={r.index}>#{String(r.index+1).padStart(3,"0")} — {r.preview.slice(0,55)}...</option>)}
                  </select>
                </div>
              )}
              {loading && <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", textAlign: "center", padding: 8 }}>加载中...</p>}
              {txt && !loading && <div style={C.preview}>{txt.slice(0, 550)}{txt.length > 550 ? "..." : ""}</div>}
            </div>
          )}

          {tab === "upload" && <div><label style={C.label}>上传简历文件</label><input type="file" accept=".txt,.md" onChange={async e => { const f = e.target.files?.[0]; if (f) setUp(await f.text()); }} style={{ ...C.input, padding: "8px" }} />{upTxt && <p style={{ marginTop: 6, fontSize: "0.8rem", color: "var(--accent)" }}>已读取 {upTxt.length} 字符</p>}</div>}

          {tab === "paste" && <div><label style={C.label}>粘贴简历内容</label><textarea value={pasted} onChange={e => setPasted(e.target.value)} placeholder="在这里粘贴你的简历..." rows={7} style={C.textarea} /></div>}

          <div style={{ marginTop: 22 }}><label style={C.label}>目标面试岗位</label><input type="text" value={job} onChange={e => setJob(e.target.value)} placeholder="如：后端开发工程师" style={C.input} /></div>

          {err && <div style={{ marginTop: 14, padding: "10px 12px", background: "rgba(248,113,113,0.08)", border: "1px solid rgba(248,113,113,0.2)", borderRadius: "var(--radius-sm)", fontSize: "0.8rem", color: "var(--red)" }}>{err}</div>}

          <button onClick={go} disabled={!ok || loading} style={{ ...C.btn(!ok || loading), marginTop: 24 }}
            onMouseEnter={e => { if (ok && !loading) e.currentTarget.style.background = "var(--accent-hover)"; }}
            onMouseLeave={e => { if (ok && !loading) e.currentTarget.style.background = "var(--accent)"; }}>
            {loading ? "正在分析简历..." : "开始面试"}
          </button>
        </div>

        <p style={{ textAlign: "center", marginTop: 22, fontSize: "0.76rem", color: "var(--text-muted)" }}>简历分析 → 动态提问 → 实时评估 → 综合报告</p>
      </div>
      {pay && <PaymentModal onClose={() => setPay(false)} />}
    </div>
  );
}
