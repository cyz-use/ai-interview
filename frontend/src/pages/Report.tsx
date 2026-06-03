// ========== 评估报告页 ==========

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";
import type { FinalReport } from "../types";

export default function Report() {
  const navigate = useNavigate();
  const [report, setReport] = useState<FinalReport | null>(null);

  useEffect(() => {
    const saved = sessionStorage.getItem("final_report");
    if (saved) {
      try { setReport(JSON.parse(saved)); } catch {}
    }
  }, []);

  if (!report) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--bg-primary)" }}>
        <p style={{ color: "var(--text-muted)" }}>暂无报告数据</p>
      </div>
    );
  }

  const { total_score, dimensions, strengths, weak_points, improvement_suggestions } = report;

  const radarData = Object.entries(dimensions || {}).map(([name, value]) => ({ subject: name, score: value }));
  const barData = Object.entries(dimensions || {}).map(([name, value]) => ({ name, score: value }));
  const scoreColor = total_score >= 80 ? "#10b981" : total_score >= 60 ? "#f59e0b" : "#ef4444";

  const s = {
    page: { minHeight: "100vh", background: "var(--bg-primary)", padding: "60px 16px" } as React.CSSProperties,
    container: { maxWidth: "800px", margin: "0 auto" } as React.CSSProperties,
    card: {
      background: "var(--bg-card)",
      border: "1px solid var(--border)",
      borderRadius: "var(--radius-lg)",
      padding: "32px",
      boxShadow: "var(--shadow-sm)",
    } as React.CSSProperties,
    sectionTitle: {
      fontSize: "1rem",
      fontWeight: 600,
      color: "var(--text-primary)",
      marginBottom: "16px",
    } as React.CSSProperties,
    chip: (color: string) =>
      ({
        display: "inline-flex",
        alignItems: "center",
        gap: "6px",
        padding: "6px 12px",
        borderRadius: "20px",
        background: `rgba(${color === "green" ? "16,185,129" : color === "orange" ? "245,158,11" : "239,68,68"}, 0.08)`,
        color: color === "green" ? "#10b981" : color === "orange" ? "#f59e0b" : "#ef4444",
        fontSize: "0.78rem",
        fontWeight: 500,
      } as React.CSSProperties),
    listItem: (color: string) =>
      ({
        display: "flex",
        gap: "10px",
        padding: "10px 0",
        borderBottom: "1px solid var(--border)",
        fontSize: "0.86rem",
        color: "var(--text-secondary)",
      } as React.CSSProperties),
    btn: {
      display: "block",
      width: "200px",
      margin: "40px auto 0",
      padding: "14px",
      background: "var(--accent)",
      color: "white",
      border: "none",
      borderRadius: "var(--radius)",
      fontWeight: 500,
      fontSize: "0.93rem",
      cursor: "pointer",
      textAlign: "center" as const,
    } as React.CSSProperties,
  };

  return (
    <div style={s.page}>
      <div style={s.container}>
        {/* 标题 */}
        <div style={{ textAlign: "center", marginBottom: "40px" }}>
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              width: "48px",
              height: "48px",
              background: "var(--accent-light)",
              borderRadius: "var(--radius)",
              marginBottom: "16px",
            }}
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="1.8" strokeLinecap="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
          </div>
          <h1 style={{ fontSize: "1.6rem", fontWeight: 600, color: "var(--text-primary)", margin: "0 0 8px" }}>
            面试评估报告
          </h1>
          <p style={{ fontSize: "0.88rem", color: "var(--text-muted)", margin: 0 }}>
            AI 多智能体协同评估
          </p>
        </div>

        {/* 总分 */}
        <div style={{ ...s.card, textAlign: "center", marginBottom: "28px", padding: "40px 32px" }}>
          <p style={{ fontSize: "0.84rem", color: "var(--text-muted)", margin: "0 0 12px", textTransform: "uppercase", letterSpacing: "0.1em" }}>
            综合总分
          </p>
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              width: "140px",
              height: "140px",
              borderRadius: "50%",
              border: `4px solid ${scoreColor}`,
              background: `rgba(${scoreColor === "#10b981" ? "16,185,129" : scoreColor === "#f59e0b" ? "245,158,11" : "239,68,68"}, 0.06)`,
            }}
          >
            <div>
              <span style={{ fontSize: "3rem", fontWeight: 700, color: scoreColor, lineHeight: 1 }}>{total_score}</span>
              <span style={{ fontSize: "1rem", color: "var(--text-muted)" }}> /100</span>
            </div>
          </div>
        </div>

        {/* 图表双栏 */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "28px", marginBottom: "28px" }}>
          <div style={s.card}>
            <h3 style={s.sectionTitle}>能力维度</h3>
            <ResponsiveContainer width="100%" height={280}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="var(--border)" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: "var(--text-secondary)", fontSize: 12 }} />
                <PolarRadiusAxis domain={[0, 100]} tick={{ fill: "var(--text-muted)", fontSize: 10 }} />
                <Radar dataKey="score" stroke="var(--accent)" fill="var(--accent)" fillOpacity={0.15} strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          <div style={s.card}>
            <h3 style={s.sectionTitle}>得分对比</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={barData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis type="number" domain={[0, 100]} tick={{ fill: "var(--text-muted)", fontSize: 11 }} />
                <YAxis dataKey="name" type="category" tick={{ fill: "var(--text-secondary)", fontSize: 12 }} width={70} />
                <Bar dataKey="score" fill="var(--accent)" radius={[0, 6, 6, 0]} barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 文字分析 */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "28px" }}>
          <div style={s.card}>
            <h3 style={{ ...s.sectionTitle, color: "#10b981", display: "flex", alignItems: "center", gap: "6px" }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2"><polyline points="20 6 9 17 4 12" /></svg>
              优势
            </h3>
            {(strengths || []).map((item, i) => (
              <div key={i} style={s.listItem("green")}>
                <span style={{ color: "#10b981", fontWeight: 600, flexShrink: 0 }}>+</span>
                {item}
              </div>
            ))}
          </div>

          <div style={s.card}>
            <h3 style={{ ...s.sectionTitle, color: "#f59e0b", display: "flex", alignItems: "center", gap: "6px" }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" strokeWidth="2"><circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" /></svg>
              薄弱点
            </h3>
            {(weak_points || []).map((item, i) => (
              <div key={i} style={s.listItem("orange")}>
                <span style={{ color: "#f59e0b", fontWeight: 600, flexShrink: 0 }}>!</span>
                {item}
              </div>
            ))}
          </div>
        </div>

        {/* 改进建议 */}
        <div style={{ marginTop: "28px" }}>
          <div style={s.card}>
            <h3 style={{ ...s.sectionTitle, color: "var(--accent)", display: "flex", alignItems: "center", gap: "6px" }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" /></svg>
              改进建议
            </h3>
            {(improvement_suggestions || []).map((item, i) => (
              <div key={i} style={s.listItem("")}>
                <span style={{ color: "var(--accent)", fontWeight: 600, flexShrink: 0 }}>{i + 1}.</span>
                {item}
              </div>
            ))}
          </div>
        </div>

        {/* ====== 分享卡片 ====== */}
        <div style={{ marginTop: "28px" }}>
          <div style={{ ...s.card, textAlign: "center", padding: "40px 32px" }}>
            <p style={{ fontSize: "0.84rem", color: "var(--text-muted)", marginBottom: "20px", textTransform: "uppercase", letterSpacing: "0.08em" }}>
              分享你的成绩
            </p>
            {/* 分享预览卡片 */}
            <div
              id="share-card"
              style={{
                display: "inline-block",
                background: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
                borderRadius: "var(--radius-lg)",
                padding: "32px 40px",
                color: "white",
                textAlign: "center",
                minWidth: "280px",
                boxShadow: "var(--shadow-lg)",
              }}
            >
              <div style={{ fontSize: "0.72rem", opacity: 0.8, letterSpacing: "0.1em", marginBottom: "8px", textTransform: "uppercase" }}>
                AI 模拟面试评估
              </div>
              <div style={{ fontSize: "3.5rem", fontWeight: 800, lineHeight: 1, marginBottom: "4px" }}>
                {total_score}
                <span style={{ fontSize: "1rem", fontWeight: 400, opacity: 0.7 }}> /100</span>
              </div>
              <div style={{ fontSize: "0.82rem", opacity: 0.85, marginBottom: "16px" }}>
                {Object.entries(dimensions || {}).slice(0, 3).map(([k, v], i) => (
                  <span key={k}>{k} {v}{i < 2 ? " · " : ""}</span>
                ))}
              </div>
              <div style={{ fontSize: "0.7rem", opacity: 0.6 }}>
                ai-interview.vercel.app
              </div>
            </div>

            {/* 分享按钮 */}
            <div style={{ marginTop: "20px", display: "flex", gap: "10px", justifyContent: "center", flexWrap: "wrap" }}>
              <button
                onClick={() => {
                  const text = `我刚完成了一次 AI 模拟面试，得分 ${total_score}/100！快来测测你的面试水平 → ai-interview.vercel.app`;
                  try { navigator.clipboard.writeText(text); alert("已复制！去微信群/朋友圈粘贴吧"); } catch { alert(text); }
                }}
                style={{ padding: "10px 20px", background: "var(--accent)", color: "white", border: "none", borderRadius: "var(--radius-sm)", fontWeight: 500, cursor: "pointer", fontSize: "0.85rem" }}
              >
                复制邀请文案
              </button>
              <button
                onClick={() => {
                  let text = `AI 模拟面试得分 ${total_score}/100\n`;
                  Object.entries(dimensions || {}).forEach(([k, v]) => { text += `${k}: ${v} · `; });
                  text += "\nai-interview.vercel.app";
                  try { navigator.clipboard.writeText(text); alert("已复制！去微信群/朋友圈粘贴吧"); } catch { alert(text); }
                }}
                style={{ padding: "10px 20px", background: "var(--bg-secondary)", color: "var(--text-secondary)", border: "1px solid var(--border)", borderRadius: "var(--radius-sm)", fontWeight: 500, cursor: "pointer", fontSize: "0.85rem" }}
              >
                复制成绩单
              </button>
            </div>
          </div>
        </div>

        {/* 重新开始 */}
        <button
          style={s.btn}
          onClick={() => {
            sessionStorage.clear();
            navigate("/");
          }}
          onMouseEnter={(e) => { e.currentTarget.style.background = "var(--accent-hover)"; }}
          onMouseLeave={(e) => { e.currentTarget.style.background = "var(--accent)"; }}
        >
          重新开始面试
        </button>
      </div>
    </div>
  );
}
