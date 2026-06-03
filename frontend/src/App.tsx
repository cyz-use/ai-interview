// ========== 应用入口 ==========

import { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import * as api from "./api/client";
import Home from "./pages/Home";
import Interview from "./pages/Interview";
import Report from "./pages/Report";

// ===================== 登录/注册页 =====================

function LoginPage() {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!username || !password || (mode === "register" && !email)) return;
    setLoading(true);
    setError("");
    try {
      const result =
        mode === "register"
          ? await api.register(username, email, password)
          : await api.login(username, password);
      api.setToken(result.access_token);
      window.location.reload();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="flex min-h-screen items-center justify-center px-4"
      style={{ background: "var(--bg-primary)" }}
    >
      <div
        className="w-full max-w-sm"
        style={{
          background: "var(--bg-card)",
          border: "1px solid var(--border)",
          borderRadius: "var(--radius-lg)",
          padding: "40px 32px",
          boxShadow: "var(--shadow-lg)",
        }}
      >
        {/* Logo */}
        <div className="mb-8 text-center">
          <div
            className="mx-auto mb-4 flex h-12 w-12 items-center justify-center"
            style={{
              background: "var(--accent-light)",
              borderRadius: "var(--radius)",
            }}
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round">
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          <h1
            className="text-xl font-semibold tracking-tight"
            style={{ color: "var(--text-primary)" }}
          >
            AI 模拟面试
          </h1>
          <p className="mt-1 text-sm" style={{ color: "var(--text-muted)" }}>
            {mode === "login" ? "欢迎回来" : "创建新账号"}
          </p>
        </div>

        {/* 表单 */}
        <div className="space-y-4">
          <div>
            <label
              className="mb-1.5 block text-xs font-medium"
              style={{ color: "var(--text-secondary)" }}
            >
              用户名
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="输入用户名"
              style={{
                width: "100%",
                padding: "10px 14px",
                border: "1px solid var(--border)",
                borderRadius: "var(--radius-sm)",
                background: "var(--bg-secondary)",
                color: "var(--text-primary)",
                fontSize: "0.9rem",
                transition: "border-color 0.15s",
              }}
            />
          </div>

          {mode === "register" && (
            <div>
              <label
                className="mb-1.5 block text-xs font-medium"
                style={{ color: "var(--text-secondary)" }}
              >
                邮箱
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="输入邮箱"
                style={{
                  width: "100%",
                  padding: "10px 14px",
                  border: "1px solid var(--border)",
                  borderRadius: "var(--radius-sm)",
                  background: "var(--bg-secondary)",
                  color: "var(--text-primary)",
                  fontSize: "0.9rem",
                }}
              />
            </div>
          )}

          <div>
            <label
              className="mb-1.5 block text-xs font-medium"
              style={{ color: "var(--text-secondary)" }}
            >
              密码
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
              placeholder="输入密码"
              style={{
                width: "100%",
                padding: "10px 14px",
                border: "1px solid var(--border)",
                borderRadius: "var(--radius-sm)",
                background: "var(--bg-secondary)",
                color: "var(--text-primary)",
                fontSize: "0.9rem",
              }}
            />
          </div>

          {error && (
            <div
              style={{
                padding: "10px 14px",
                background: "rgba(239,68,68,0.08)",
                border: "1px solid rgba(239,68,68,0.2)",
                borderRadius: "var(--radius-sm)",
                fontSize: "0.82rem",
                color: "#ef4444",
              }}
            >
              {error}
            </div>
          )}

          <button
            onClick={handleSubmit}
            disabled={loading}
            style={{
              width: "100%",
              padding: "12px",
              background: loading
                ? "var(--text-muted)"
                : "var(--accent)",
              color: "white",
              border: "none",
              borderRadius: "var(--radius)",
              fontWeight: 500,
              fontSize: "0.93rem",
              cursor: loading ? "not-allowed" : "pointer",
              transition: "background 0.15s, transform 0.1s",
              transform: loading ? "none" : "scale(1)",
            }}
            onMouseEnter={(e) => {
              if (!loading) e.currentTarget.style.background = "var(--accent-hover)";
            }}
            onMouseLeave={(e) => {
              if (!loading) e.currentTarget.style.background = "var(--accent)";
            }}
          >
            {loading ? "处理中..." : mode === "login" ? "登录" : "注册"}
          </button>
        </div>

        <p className="mt-6 text-center text-xs" style={{ color: "var(--text-muted)" }}>
          {mode === "login" ? "还没有账号？" : "已有账号？"}
          <button
            onClick={() => setMode(mode === "login" ? "register" : "login")}
            style={{
              marginLeft: "4px",
              color: "var(--accent)",
              background: "none",
              border: "none",
              fontWeight: 500,
              cursor: "pointer",
              fontSize: "0.82rem",
            }}
          >
            {mode === "login" ? "立即注册" : "去登录"}
          </button>
        </p>
      </div>
    </div>
  );
}

// ===================== 路由守卫 =====================

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = api.getToken();
  if (!token) return <LoginPage />;
  return <>{children}</>;
}

// ===================== 路由 =====================

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />
        <Route
          path="/interview/:sessionId"
          element={
            <ProtectedRoute>
              <Interview />
            </ProtectedRoute>
          }
        />
        <Route
          path="/report/:sessionId"
          element={
            <ProtectedRoute>
              <Report />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
