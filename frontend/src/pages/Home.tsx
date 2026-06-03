// ========== 首页 ==========

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import * as api from "../api/client";
import type { DemoResumeItem, SubscriptionStatus, PaymentInfo } from "../types";

const s = {
  page: { minHeight: "100vh", background: "var(--bg-primary)", padding: "60px 16px" } as React.CSSProperties,
  container: { maxWidth: "640px", margin: "0 auto" } as React.CSSProperties,
  card: { background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: "var(--radius-lg)", padding: "32px", boxShadow: "var(--shadow-sm)" } as React.CSSProperties,
  label: { display: "block", fontSize: "0.8rem", fontWeight: 500, color: "var(--text-secondary)", marginBottom: "6px" } as React.CSSProperties,
  select: { width: "100%", padding: "10px 14px", border: "1px solid var(--border)", borderRadius: "var(--radius-sm)", background: "var(--bg-secondary)", color: "var(--text-primary)", fontSize: "0.9rem", appearance: "none" as const, cursor: "pointer" } as React.CSSProperties,
  input: { width: "100%", padding: "10px 14px", border: "1px solid var(--border)", borderRadius: "var(--radius-sm)", background: "var(--bg-secondary)", color: "var(--text-primary)", fontSize: "0.9rem" } as React.CSSProperties,
  textarea: { width: "100%", padding: "12px 14px", border: "1px solid var(--border)", borderRadius: "var(--radius-sm)", background: "var(--bg-secondary)", color: "var(--text-primary)", fontSize: "0.85rem", resize: "none" as const, lineHeight: 1.6 } as React.CSSProperties,
  btn: (disabled: boolean) => ({ width: "100%", padding: "14px", background: disabled ? "var(--text-muted)" : "var(--accent)", color: "white", border: "none", borderRadius: "var(--radius)", fontWeight: 500, fontSize: "0.95rem", cursor: disabled ? "not-allowed" : "pointer", opacity: disabled ? 0.5 : 1 } as React.CSSProperties),
  tab: (active: boolean) => ({ flex: 1, padding: "10px", textAlign: "center" as const, fontSize: "0.85rem", fontWeight: active ? 500 : 400, color: active ? "var(--accent)" : "var(--text-muted)", background: active ? "var(--accent-light)" : "transparent", border: "none", borderRadius: "var(--radius-sm)", cursor: "pointer", transition: "all 0.15s" } as React.CSSProperties),
  preview: { background: "var(--bg-secondary)", border: "1px solid var(--border)", borderRadius: "var(--radius-sm)", padding: "14px", maxHeight: "180px", overflowY: "auto" as const, fontSize: "0.82rem", color: "var(--text-secondary)", lineHeight: 1.7, whiteSpace: "pre-wrap" as const } as React.CSSProperties,
};

// ============ 支付弹窗 ============

function PaymentModal({ onClose }: { onClose: () => void }) {
  const [info, setInfo] = useState<PaymentInfo | null>(null);

  useEffect(() => {
    api.getPaymentInfo().then(setInfo).catch(() => {});
  }, []);

  return (
    <div
      style={{
        position: "fixed", inset: 0, zIndex: 100,
        display: "flex", alignItems: "center", justifyContent: "center",
        background: "rgba(0,0,0,0.6)", backdropFilter: "blur(4px)",
      }}
      onClick={onClose}
    >
      <div
        style={{
          ...s.card, maxWidth: "380px", width: "90%", textAlign: "center",
          animation: "slideUp 0.3s ease",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h3 style={{ fontSize: "1.2rem", fontWeight: 600, marginBottom: "8px", color: "var(--text-primary)" }}>
          升级会员
        </h3>
        <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: "24px" }}>
          试用次数已用完，升级即可无限使用
        </p>

        {/* 价格卡片 */}
        <div style={{ display: "flex", gap: "12px", marginBottom: "24px" }}>
          <div style={{ flex: 1, padding: "16px 12px", borderRadius: "var(--radius)", border: "2px solid var(--border)", background: "var(--bg-secondary)" }}>
            <p style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginBottom: "4px" }}>月度</p>
            <p style={{ fontSize: "1.8rem", fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>
              ¥{info?.price_monthly || 29}
            </p>
            <p style={{ fontSize: "0.72rem", color: "var(--text-muted)", margin: 0 }}>/月</p>
          </div>
          <div style={{ flex: 1, padding: "16px 12px", borderRadius: "var(--radius)", border: "2px solid var(--accent)", background: "var(--accent-light)", position: "relative" }}>
            <span style={{ position: "absolute", top: "-10px", right: "12px", background: "var(--accent)", color: "white", padding: "2px 8px", borderRadius: "10px", fontSize: "0.7rem" }}>推荐</span>
            <p style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginBottom: "4px" }}>年度</p>
            <p style={{ fontSize: "1.8rem", fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>
              ¥{info?.price_yearly || 199}
            </p>
            <p style={{ fontSize: "0.72rem", color: "var(--text-muted)", margin: 0 }}>/年</p>
          </div>
        </div>

        {/* 付款说明 */}
        <div style={{
          padding: "16px", borderRadius: "var(--radius-sm)",
          background: "var(--bg-secondary)", border: "1px solid var(--border)",
          fontSize: "0.82rem", color: "var(--text-secondary)", lineHeight: 1.8, textAlign: "left",
        }}>
          <p style={{ fontWeight: 500, marginBottom: "8px", color: "var(--text-primary)" }}>付款方式：</p>
          <p>1. 微信扫描下方收款码付款</p>
          <p>2. 付款后截图发给客服</p>
          <p style={{ marginTop: "4px", fontSize: "0.78rem", color: "var(--text-muted)" }}>
            {info?.contact || "客服微信/邮箱见付款说明"}
          </p>
        </div>

        <button
          onClick={onClose}
          style={{ marginTop: "20px", padding: "10px 32px", background: "var(--bg-secondary)", color: "var(--text-muted)", border: "1px solid var(--border)", borderRadius: "var(--radius-sm)", cursor: "pointer", fontSize: "0.85rem" }}
        >
          稍后再说
        </button>
      </div>

      <style>{`@keyframes slideUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }`}</style>
    </div>
  );
}

// ============ 主页面 ============

export default function Home() {
  const navigate = useNavigate();
  const [tab, setTab] = useState<"demo" | "upload" | "paste">("demo");
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [resumes, setResumes] = useState<DemoResumeItem[]>([]);
  const [selectedResumeIdx, setSelectedResumeIdx] = useState(-1);
  const [resumeText, setResumeText] = useState("");
  const [targetJob, setTargetJob] = useState("");
  const [uploadedText, setUploadedText] = useState("");
  const [pastedText, setPastedText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [sub, setSub] = useState<SubscriptionStatus | null>(null);
  const [showPayment, setShowPayment] = useState(false);

  useEffect(() => { api.getDemoCategories().then(r => setCategories(r.categories)).catch(() => {}); }, []);
  useEffect(() => { if (selectedCategory && tab === "demo") { api.getDemoResumeList(selectedCategory).then(r => setResumes(r.items)).catch(() => {}); } }, [selectedCategory, tab]);
  useEffect(() => { if (selectedResumeIdx >= 0 && selectedCategory && tab === "demo") { setLoading(true); api.getDemoResumeDetail(selectedCategory, selectedResumeIdx).then(r => setResumeText(r.text)).catch(e => setError(e.message)).finally(() => setLoading(false)); } }, [selectedResumeIdx, selectedCategory, tab]);
  useEffect(() => { api.getSubscriptionStatus().then(setSub).catch(() => {}); }, []);

  const handleStart = async () => {
    const text = tab === "demo" ? resumeText : tab === "upload" ? uploadedText : pastedText;
    if (!text.trim() || !targetJob.trim()) return;

    // 检查试用配额
    if (sub && !sub.can_interview) {
      setShowPayment(true);
      return;
    }

    setLoading(true); setError("");
    try {
      const result = await api.startInterview(text, targetJob);
      sessionStorage.setItem("interview_session", result.session_id);
      sessionStorage.setItem("interview_state", JSON.stringify({ sessionId: result.session_id, targetJob, candidateProfile: result.candidate_profile, messages: [{ type: "ai", content: result.first_question }], roundScores: [], mainQuestionIndex: 0, followupCount: 0, currentRound: 1, interviewCompleted: false }));
      // 刷新试用状态
      api.getSubscriptionStatus().then(setSub).catch(() => {});
      navigate(`/interview/${result.session_id}`);
    } catch (e: any) {
      if (e.message?.includes("402") || e.message?.includes("试用") || e.message?.includes("升级")) {
        setShowPayment(true);
      } else {
        setError(e.message);
      }
    } finally { setLoading(false); }
  };

  const canStart = (tab === "demo" ? resumeText : tab === "upload" ? uploadedText : pastedText).trim().length > 0 && targetJob.trim().length > 0;
  const remaining = sub?.trial_remaining ?? 3;
  const trialPct = sub ? ((sub.trial_interviews_used / sub.max_trial_interviews) * 100) : 0;

  return (
    <div style={s.page}>
      <div style={s.container}>
        {/* 头部 */}
        <div style={{ marginBottom: "32px", textAlign: "center" }}>
          <div style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: "48px", height: "48px", background: "var(--accent-light)", borderRadius: "var(--radius)", marginBottom: "16px" }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="1.8" strokeLinecap="round">
              <path d="M12 2L2 7l10 5 10-5-10-5z" /><path d="M2 17l10 5 10-5" /><path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          <h1 style={{ fontSize: "1.8rem", fontWeight: 600, letterSpacing: "-0.03em", color: "var(--text-primary)", margin: "0 0 8px" }}>AI 模拟面试</h1>
          <p style={{ fontSize: "0.9rem", color: "var(--text-muted)", margin: 0 }}>多智能体协同评估 · 自适应追问 · 深度分析</p>
        </div>

        {/* 试用进度 */}
        {sub && (
          <div style={{ ...s.card, marginBottom: "20px", padding: "20px 24px" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "10px" }}>
              <span style={{ fontSize: "0.84rem", fontWeight: 500, color: "var(--text-primary)" }}>
                {sub.subscription_tier === "pro" ? "Pro 会员 · 无限使用" : `免费试用 · 剩余 ${remaining} 次`}
              </span>
              {sub.subscription_tier === "free" && (
                <button
                  onClick={() => setShowPayment(true)}
                  style={{ padding: "6px 14px", background: "var(--accent)", color: "white", border: "none", borderRadius: "16px", fontSize: "0.78rem", fontWeight: 500, cursor: "pointer" }}
                >
                  升级
                </button>
              )}
            </div>
            {sub.subscription_tier === "free" && (
              <div style={{ height: "4px", background: "var(--bg-secondary)", borderRadius: "2px", overflow: "hidden" }}>
                <div style={{ height: "100%", width: `${trialPct}%`, background: trialPct >= 100 ? "#ef4444" : "var(--accent)", borderRadius: "2px", transition: "width 0.3s" }} />
              </div>
            )}
          </div>
        )}

        {/* 主卡片 */}
        <div style={s.card}>
          <div style={{ display: "flex", gap: "4px", padding: "4px", background: "var(--bg-secondary)", borderRadius: "var(--radius-sm)", marginBottom: "28px" }}>
            {(["demo", "upload", "paste"] as const).map(t => (
              <button key={t} style={s.tab(tab === t)} onClick={() => setTab(t)}>
                {t === "demo" ? "模拟简历" : t === "upload" ? "上传简历" : "粘贴内容"}
              </button>
            ))}
          </div>

          {tab === "demo" && (
            <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
              <div>
                <label style={s.label}>岗位类别</label>
                <select style={s.select} value={selectedCategory} onChange={e => { setSelectedCategory(e.target.value); setSelectedResumeIdx(-1); setResumeText(""); }}>
                  <option value="">选择岗位（{categories.length} 个类别）</option>
                  {categories.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              {resumes.length > 0 && (
                <div>
                  <label style={s.label}>选择简历（{resumes.length} 份）</label>
                  <select style={s.select} value={selectedResumeIdx} onChange={e => setSelectedResumeIdx(Number(e.target.value))}>
                    <option value={-1}>选择一份简历</option>
                    {resumes.map(r => <option key={r.index} value={r.index}>#{String(r.index+1).padStart(3,"0")} — {r.preview.slice(0,60)}...</option>)}
                  </select>
                </div>
              )}
              {loading && <p style={{ fontSize: "0.82rem", color: "var(--text-muted)", textAlign: "center" }}>正在加载简历...</p>}
              {resumeText && !loading && <div style={s.preview}>{resumeText.slice(0,600)}{resumeText.length > 600 ? "..." : ""}</div>}
            </div>
          )}

          {tab === "upload" && (
            <div>
              <label style={s.label}>上传简历文件</label>
              <input type="file" accept=".txt,.md" onChange={async e => { const f = e.target.files?.[0]; if (f) setUploadedText(await f.text()); }} style={{ ...s.input, padding: "8px" }} />
              {uploadedText && <p style={{ marginTop: "8px", fontSize: "0.82rem", color: "var(--accent)" }}>已读取 {uploadedText.length} 字符</p>}
            </div>
          )}

          {tab === "paste" && (
            <div>
              <label style={s.label}>粘贴简历内容</label>
              <textarea value={pastedText} onChange={e => setPastedText(e.target.value)} placeholder="在这里粘贴你的简历..." rows={8} style={s.textarea} />
            </div>
          )}

          <div style={{ marginTop: "24px" }}>
            <label style={s.label}>目标面试岗位</label>
            <input type="text" value={targetJob} onChange={e => setTargetJob(e.target.value)} placeholder="如：后端开发工程师" style={s.input} />
          </div>

          {error && <div style={{ marginTop: "16px", padding: "10px 14px", background: "rgba(239,68,68,0.06)", border: "1px solid rgba(239,68,68,0.15)", borderRadius: "var(--radius-sm)", fontSize: "0.82rem", color: "#ef4444" }}>{error}</div>}

          <button
            onClick={handleStart}
            disabled={!canStart || loading}
            style={{ ...s.btn(!canStart || loading), marginTop: "28px" }}
            onMouseEnter={e => { if (canStart && !loading) e.currentTarget.style.background = "var(--accent-hover)"; }}
            onMouseLeave={e => { if (canStart && !loading) e.currentTarget.style.background = "var(--accent)"; }}
          >
            {loading ? "正在分析简历..." : "开始面试"}
          </button>
        </div>

        <p style={{ textAlign: "center", marginTop: "24px", fontSize: "0.78rem", color: "var(--text-muted)" }}>
          系统将调用 AI 多智能体协同工作：简历分析 → 动态提问 → 实时评估
        </p>
      </div>

      {showPayment && <PaymentModal onClose={() => setShowPayment(false)} />}
    </div>
  );
}
