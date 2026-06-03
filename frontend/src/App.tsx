// ========== 应用入口 ==========

import { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import * as api from "./api/client";
import Home from "./pages/Home";
import Interview from "./pages/Interview";
import Report from "./pages/Report";

// ===================== 登录页 =====================

function LoginPage() {
  const [mode, setMode] = useState<"login" | "register">("register");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!username || !password || (mode === "register" && !email)) return;
    setLoading(true); setError("");
    try {
      const r = mode === "register"
        ? await api.register(username, email, password)
        : await api.login(username, password);
      api.setToken(r.access_token);
      window.location.reload();
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  const inputStyle = {
    width: "100%", padding: "12px 14px", border: "1px solid var(--border-light)", borderRadius: "var(--radius-sm)",
    background: "var(--bg-base)", color: "var(--text-primary)", fontSize: "0.9rem", outline: "none",
    transition: "border-color 0.2s",
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--bg-base)", padding: "20px" }}>
      <div style={{ width: "100%", maxWidth: "380px" }}>
        {/* Logo */}
        <div style={{ textAlign: "center", marginBottom: "36px" }}>
          <div style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: 44, height: 44, background: "var(--accent-glow)", borderRadius: "var(--radius)", marginBottom: 16 }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
          </div>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 600, color: "var(--text-primary)", letterSpacing: "-0.02em" }}>{mode === "login" ? "欢迎登录" : "注册新账号"}</h1>
          <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginTop: 4 }}>{mode === "login" ? "登录后继续面试" : "免费试用 3 次，无需付费"}</p>
        </div>

        {/* 卡片 */}
        <div style={{ background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: "var(--radius-lg)", padding: "28px 24px" }}>
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <input style={inputStyle} type="text" placeholder="用户名" value={username} onChange={e => setUsername(e.target.value)} />
            {mode === "register" && <input style={inputStyle} type="email" placeholder="邮箱" value={email} onChange={e => setEmail(e.target.value)} />}
            <input style={inputStyle} type="password" placeholder="密码" value={password} onChange={e => setPassword(e.target.value)} onKeyDown={e => e.key === "Enter" && handleSubmit()} />

            {error && <div style={{ padding: "10px 12px", background: "rgba(248,113,113,0.08)", border: "1px solid rgba(248,113,113,0.2)", borderRadius: "var(--radius-sm)", fontSize: "0.8rem", color: "var(--red)" }}>{error}</div>}

            <button onClick={handleSubmit} disabled={loading}
              style={{ width: "100%", padding: "12px", background: loading ? "var(--text-muted)" : "var(--accent)", color: "white", border: "none", borderRadius: "var(--radius)", fontWeight: 500, fontSize: "0.9rem", cursor: loading ? "not-allowed" : "pointer", transition: "background 0.15s" }}>
              {loading ? "处理中..." : mode === "login" ? "登录" : "注册"}
            </button>
          </div>

          <p style={{ marginTop: 20, textAlign: "center", fontSize: "0.82rem", color: "var(--text-muted)" }}>
            {mode === "login" ? "还没有账号？" : "已有账号？"}
            <span onClick={() => setMode(mode === "login" ? "register" : "login")} style={{ marginLeft: 4, color: "var(--accent)", fontWeight: 600, cursor: "pointer", fontSize: "0.85rem" }}>{mode === "login" ? "立即注册 →" : "去登录 →"}</span>
          </p>
        </div>
      </div>
    </div>
  );
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  if (!api.getToken()) return <LoginPage />;
  return <>{children}</>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
        <Route path="/interview/:sessionId" element={<ProtectedRoute><Interview /></ProtectedRoute>} />
        <Route path="/report/:sessionId" element={<ProtectedRoute><Report /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
