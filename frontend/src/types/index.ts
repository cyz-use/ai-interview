// ========== TypeScript 类型定义 ==========

export interface CandidateProfile {
  skills: string[];
  years_of_experience: number;
  education: string;
  project_keywords: string[];
  match_score: number;
  summary: string;
}

export interface StartInterviewResponse {
  session_id: string;
  first_question: string;
  candidate_profile: CandidateProfile;
}

export interface RoundScore {
  tech_score: number;
  communication_score: number;
  logic_score: number;
  brief_comment: string;
}

export interface FinalReport {
  total_score: number;
  dimensions: Record<string, number>;
  strengths: string[];
  weak_points: string[];
  improvement_suggestions: string[];
}

export interface SSEEvent {
  node: string;
  status: string;
  question?: string;
  candidate_profile?: CandidateProfile;
  round_scores?: RoundScore[];
  next_question_type?: string;
  main_question_index?: number;
  followup_count?: number;
  current_round?: number;
  interview_completed: boolean;
  final_report?: FinalReport;
  message?: string;
}

export interface InterviewSession {
  session_id: string;
  target_job: string;
  status: string;
  total_score: number | null;
  started_at: string;
  completed_at: string | null;
}

export interface DemoResumeItem {
  index: number;
  preview: string;
  length: number;
}

export interface UserInfo {
  id: string;
  username: string;
  email: string;
  trial_interviews_used: number;
  max_trial_interviews: number;
  subscription_tier: string;
  created_at: string;
}

export interface SubscriptionStatus {
  trial_interviews_used: number;
  max_trial_interviews: number;
  trial_remaining: number;
  subscription_tier: string;
  can_interview: boolean;
}

export interface PaymentInfo {
  price_monthly: number;
  price_yearly: number;
  qr_code_url: string;
  contact: string;
}
