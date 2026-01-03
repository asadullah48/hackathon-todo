/**
 * TypeScript type definitions from data-model.md
 */

export interface User {
  id: string;
  email: string;
  createdAt: string;
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  isCompleted: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface TaskCreateInput {
  title: string;
  description?: string;
}

export interface TaskUpdateInput {
  title?: string;
  description?: string;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
  page: number;
  pageSize: number;
}

export interface AuthResponse {
  user: User;
  token: string;
  expiresAt: string;
}

export interface UserCreate {
  email: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, string>;
}

export type ApiResult<T> =
  | { success: true; data: T }
  | { success: false; error: ApiError };

// Chat types for Phase 3
export interface ToolCallInfo {
  tool_name: string;
  arguments: Record<string, unknown>;
  result: string;
}

export interface ChatRequest {
  conversation_id?: string;
  message: string;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls: ToolCallInfo[];
}

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
}

export interface Conversation {
  id: string;
  user_id: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
}

export interface ConversationListResponse {
  conversations: Conversation[];
  total: number;
}
