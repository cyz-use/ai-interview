// ========== API 客户端 ==========

// 开发模式通过 Vite proxy 转发，生产模式使用相对路径（由 Nginx 反向代理处理）
const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

let _token: string | null = localStorage.getItem("auth_token");

export function getToken(): string | null {
  return _token;
}

export function setToken(token: string | null) {
  _token = token;
  if (token) {
    localStorage.setItem("auth_token", token);
  } else {
    localStorage.removeItem("auth_token");
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) || {}),
  };

  if (_token) {
    headers["Authorization"] = `Bearer ${_token}`;
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `请求失败: ${res.status}`);
  }

  return res.json();
}

// ========== 认证 ==========

export async function register(username: string, email: string, password: string) {
  return request<{ access_token: string; token_type: string; expires_in: number }>(
    "/auth/register",
    { method: "POST", body: JSON.stringify({ username, email, password }) }
  );
}

export async function login(username: string, password: string) {
  return request<{ access_token: string; token_type: string; expires_in: number }>(
    "/auth/login",
    { method: "POST", body: JSON.stringify({ username, password }) }
  );
}

export async function getMe() {
  return request<import("../types").UserInfo>("/auth/me");
}

// ========== 面试 ==========

export async function startInterview(resumeText: string, targetJob: string) {
  return request<import("../types").StartInterviewResponse>("/interview/start", {
    method: "POST",
    body: JSON.stringify({ resume_text: resumeText, target_job: targetJob }),
  });
}

export function getSSEUrl(sessionId: string, type: "answer" | "end"): string {
  return `${API_BASE}/interview/${sessionId}/${type}`;
}

export async function submitAnswerSSE(
  sessionId: string,
  answer: string,
  onEvent: (event: import("../types").SSEEvent) => void,
  onDone: () => void,
  onError: (error: string) => void
): Promise<AbortController> {
  const controller = new AbortController();

  try {
    const res = await fetch(getSSEUrl(sessionId, "answer"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${_token}`,
      },
      body: JSON.stringify({ answer }),
      signal: controller.signal,
    });

    const reader = res.body?.getReader();
    if (!reader) throw new Error("无法读取响应流");

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const data = JSON.parse(line.slice(6));
            onEvent(data);
          } catch {
            // 跳过非 JSON 行
          }
        }
      }
    }

    onDone();
  } catch (err: any) {
    if (err.name !== "AbortError") {
      onError(err.message || "连接失败");
    }
  }

  return controller;
}

export async function endInterviewSSE(
  sessionId: string,
  onEvent: (event: import("../types").SSEEvent) => void,
  onDone: () => void,
  onError: (error: string) => void
): Promise<AbortController> {
  const controller = new AbortController();

  try {
    const res = await fetch(getSSEUrl(sessionId, "end"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${_token}`,
      },
      signal: controller.signal,
    });

    const reader = res.body?.getReader();
    if (!reader) throw new Error("无法读取响应流");

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const data = JSON.parse(line.slice(6));
            onEvent(data);
          } catch {
            // 跳过
          }
        }
      }
    }

    onDone();
  } catch (err: any) {
    if (err.name !== "AbortError") {
      onError(err.message || "连接失败");
    }
  }

  return controller;
}

export async function getReport(sessionId: string) {
  return request<import("../types").FinalReport>(`/interview/${sessionId}/report`);
}

export async function getInterviewHistory(page = 1, size = 20) {
  return request<{
    items: import("../types").InterviewSession[];
    total: number;
  }>(`/interview/history?page=${page}&size=${size}`);
}

// ========== 简历 ==========

export async function getDemoCategories() {
  return request<{ categories: string[] }>("/resume/demo/categories");
}

export async function getDemoResumeList(category: string) {
  return request<{ items: import("../types").DemoResumeItem[]; total: number }>(
    `/resume/demo/list?category=${encodeURIComponent(category)}`
  );
}

export async function getDemoResumeDetail(category: string, index: number) {
  return request<{ text: string }>(
    `/resume/demo/${encodeURIComponent(category)}/${index}`
  );
}

// ========== 订阅 ==========

export async function getSubscriptionStatus() {
  return request<import("../types").SubscriptionStatus>("/subscription/status");
}

export async function getPaymentInfo() {
  return request<import("../types").PaymentInfo>("/subscription/payment-info");
}

// ========== RAG ==========

export async function uploadRagDocument(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/rag/documents`, {
    method: "POST",
    headers: { Authorization: `Bearer ${_token}` },
    body: formData,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || "上传失败");
  }

  return res.json();
}

export async function getRagDocuments() {
  return request<{ items: { document_id: string; filename: string; chunk_count: number }[] }>(
    "/rag/documents"
  );
}
