// API Types for Noode

export interface Project {
  project_id: string;
  name: string;
  description?: string;
  template: string;
  path: string;
  status: 'active' | 'development' | 'review' | 'completed';
  created_at: string;
  updated_at: string;
}

export interface CreateProjectRequest {
  name: string;
  description?: string;
  template: string;
}

export interface Agent {
  name: string;
  role: string;
  status: 'idle' | 'busy' | 'error';
  capabilities: string[];
  last_active?: string;
}

export interface Task {
  task_id: string;
  task_type: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  project_id?: string;
  result?: Record<string, unknown>;
  error?: string;
  duration_ms?: number;
}

export interface CreateTaskRequest {
  task_type: string;
  description: string;
  project_id?: string;
  parameters?: Record<string, unknown>;
}

export interface ApiError {
  error: string;
  detail?: string;
  code: string;
}

export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  version: string;
  timestamp: string;
}

// Knowledge Types
export interface Document {
  id?: string;
  content: string;
  doc_type: 'text' | 'code' | 'markdown' | 'json';
  metadata?: Record<string, unknown>;
  created_at?: string;
}

export interface SearchRequest {
  query: string;
  top_k?: number;
}

export interface SearchResult {
  id: string;
  content: string;
  doc_type: string;
  score: number;
  metadata: Record<string, unknown>;
}

export interface KnowledgeStats {
  total_documents: number;
  document_types: Record<string, number>;
  storage_size_mb?: number;
}
