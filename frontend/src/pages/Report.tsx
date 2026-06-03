// ========== 评估报告页 ==========

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from "recharts";
import type { FinalReport } from "../types";

export default function Report() {
  const nav = useNavigate();
  const [r, setR] = useState<FinalReport | null>(null);

  useEffect(() => {
    const saved = sessionStorage.getItem("final_report");
    if (saved) try { setR(JSON.parse(saved)); } catch {}
  }, []);

  if (!r) return <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--bg-base)", color: "var(--text-muted)" }}>暂无报告数据</div>;

  const { total_score, dimensions, strengths, weak_points, improvement_suggestions } = r;
  const radarData = Object.entries(dimensions || {}).map(([k, v]) => ({ subject: k, score: v }));
  const barData = Object.entries(dimensions || {}).map(([k, v]) => ({ name: k, score: v }));
  const sc = total_score >= 80 ? "var(--green)" : total_score >= 60 ? "var(--orange)" : "var(--red)";

  const S = {
    page: { minHeight: "100vh", background: "var(--bg-base)", padding: "50px 16px" } as React.CSSProperties,
    wrap: { maxWidth: "780px", margin: "0 auto" } as React.CSSProperties,
    card: { background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: "var(--radius-lg)", padding: "26px 24px" } as React.CSSProperties,
    st: { fontSize: "0.95rem", fontWeight: 600, color: "var(--text-primary)", marginBottom: 14 } as React.CSSProperties,
    li: { display: "flex", gap: 8, padding: "9px 0", borderBottom: "1px solid var(--border)", fontSize: "0.84rem", color: "var(--text-secondary)" } as React.CSSProperties,
  };

  return (
    <div style={S.page}>
      <div style={S.wrap}>
        {/* 标题 */}
        <div style={{ textAlign: "center", marginBottom: 36 }}>
          <div style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: 44, height: 44, background: "var(--accent-glow)", borderRadius: "var(--radius)", marginBottom: 14 }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          </div>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 600, color: "var(--text-primary)", margin: "0 0 6px" }}>面试评估报告</h1>
          <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", margin: 0 }}>AI 多智能体协同评估</p>
        </div>

        {/* 总分 */}
        <div style={{ ...S.card, textAlign: "center", marginBottom: 24, padding: "36px 24px" }}>
          <p style={{ fontSize: "0.78rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 12 }}>综合总分</p>
          <div style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: 130, height: 130, borderRadius: "50%", border: `4px solid ${sc}`, background: sc === "var(--green)" ? "rgba(52,211,153,0.06)" : sc === "var(--orange)" ? "rgba(245,158,11,0.06)" : "rgba(248,113,113,0.06)" }}>
            <span style={{ fontSize: "2.8rem", fontWeight: 700, color: sc, lineHeight: 1 }}>{total_score}</span>
            <span style={{ fontSize: "0.9rem", color: "var(--text-muted)", marginLeft: 2 }}>/100</span>
          </div>
        </div>

        {/* 图表 */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 24 }}>
          <div style={S.card}><h3 style={S.st}>能力维度</h3>
            <ResponsiveContainer width="100%" height={250}><RadarChart data={radarData}><PolarGrid stroke="var(--border)" /><PolarAngleAxis dataKey="subject" tick={{ fill: "var(--text-secondary)", fontSize: 11 }} /><PolarRadiusAxis domain={[0,100]} tick={{ fill: "var(--text-muted)", fontSize: 9 }} /><Radar dataKey="score" stroke="var(--accent)" fill="var(--accent)" fillOpacity={0.12} strokeWidth={2} /></RadarChart></ResponsiveContainer>
          </div>
          <div style={S.card}><h3 style={S.st}>得分对比</h3>
            <ResponsiveContainer width="100%" height={250}><BarChart data={barData} layout="vertical"><CartesianGrid strokeDasharray="3 3" stroke="var(--border)" /><XAxis type="number" domain={[0,100]} tick={{ fill: "var(--text-muted)", fontSize: 10 }} /><YAxis dataKey="name" type="category" tick={{ fill: "var(--text-secondary)", fontSize: 11 }} width={65} /><Bar dataKey="score" fill="var(--accent)" radius={[0,5,5,0]} barSize={18} /></BarChart></ResponsiveContainer>
          </div>
        </div>

        {/* 文本 */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
          <div style={S.card}><h3 style={{ ...S.st, color: "var(--green)" }}>+ 优势</h3>{(strengths || []).map((x,i) => <div key={i} style={S.li}><span style={{ color:"var(--green)", fontWeight:600, flexShrink:0 }}>+</span>{x}</div>)}</div>
          <div style={S.card}><h3 style={{ ...S.st, color: "var(--orange)" }}>! 薄弱点</h3>{(weak_points || []).map((x,i) => <div key={i} style={S.li}><span style={{ color:"var(--orange)", fontWeight:600, flexShrink:0 }}>!</span>{x}</div>)}</div>
        </div>

        {/* 建议 */}
        <div style={{ marginTop: 24 }}><div style={S.card}><h3 style={{ ...S.st, color: "var(--accent-hover)" }}>改进建议</h3>{(improvement_suggestions || []).map((x,i) => <div key={i} style={S.li}><span style={{ color:"var(--accent)", fontWeight:600, flexShrink:0 }}>{i+1}.</span>{x}</div>)}</div></div>

        {/* 分享 */}
        <div style={{ marginTop: 24, ...S.card, textAlign: "center", padding: "24px" }}>
          <div id="share-card" style={{ display: "inline-block", background: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)", borderRadius: "var(--radius-lg)", padding: "28px 36px", color: "white", textAlign: "center", minWidth: 260 }}>
            <div style={{ fontSize: "0.7rem", opacity: 0.8, letterSpacing: "0.1em", marginBottom: 6 }}>AI 模拟面试评估</div>
            <div style={{ fontSize: "3rem", fontWeight: 800, lineHeight: 1 }}>{total_score}<span style={{ fontSize: "0.9rem", fontWeight: 400, opacity: 0.7 }}>/100</span></div>
            <div style={{ fontSize: "0.78rem", opacity: 0.85, marginTop: 6 }}>{Object.entries(dimensions||{}).map(([k,v],i) => <span key={k}>{k} {v}{i<2?" · ":""}</span>)}</div>
          </div>
          <div style={{ marginTop: 16, display: "flex", gap: 10, justifyContent: "center" }}>
            <button onClick={() => { navigator.clipboard.writeText(`我刚完成AI模拟面试，得分${total_score}/100！来测测你的面试水平`).then(() => alert("已复制，去微信群/朋友圈粘贴！")).catch(()=>{}); }}
              style={{ padding: "10px 18px", background: "var(--accent)", color: "white", border: "none", borderRadius: "var(--radius-sm)", fontWeight: 500, cursor: "pointer", fontSize: "0.83rem" }}>复制邀请文案</button>
            <button onClick={() => { let t=`AI模拟面试 ${total_score}/100\n`; Object.entries(dimensions||{}).forEach(([k,v])=>{t+=`${k}:${v} `;}); navigator.clipboard.writeText(t).then(()=>alert("成绩单已复制！")).catch(()=>{}); }}
              style={{ padding: "10px 18px", background: "var(--bg-base)", color: "var(--text-secondary)", border: "1px solid var(--border)", borderRadius: "var(--radius-sm)", fontWeight: 500, cursor: "pointer", fontSize: "0.83rem" }}>复制成绩单</button>
          </div>
        </div>

        <button onClick={() => { sessionStorage.clear(); nav("/"); }}
          style={{ display: "block", width: 200, margin: "36px auto 0", padding: "13px", background: "var(--accent)", color: "white", border: "none", borderRadius: "var(--radius)", fontWeight: 500, fontSize: "0.9rem", cursor: "pointer", textAlign: "center" }}
          onMouseEnter={e => e.currentTarget.style.background = "var(--accent-hover)"} onMouseLeave={e => e.currentTarget.style.background = "var(--accent)"}>重新开始面试</button>
      </div>
    </div>
  );
}
