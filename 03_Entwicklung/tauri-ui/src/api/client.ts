import axios, { AxiosError } from 'axios';
import type { 
  Project, 
  CreateProjectRequest, 
  Agent, 
  Task, 
  CreateTaskRequest,
  HealthResponse,
  Document,
  SearchRequest,
  SearchResult,
  KnowledgeStats
} from '../types';

// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Create axios instance
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Error handler
export const handleApiError = (error: AxiosError) => {
  if (error.response) {
    // Server responded with error status
    console.error('API Error:', error.response.data);
    throw error.response.data;
  } else if (error.request) {
    // Request was made but no response
    console.error('Network Error:', error.request);
    throw { error: 'Network error. Is the backend running?' };
  } else {
    // Something else happened
    console.error('Error:', error.message);
    throw { error: error.message };
  }
};

// Health Check
export const checkHealth = async (): Promise<HealthResponse> => {
  try {
    const response = await apiClient.get<HealthResponse>('/health');
    return response.data;
  } catch (error) {
    handleApiError(error as AxiosError);
    throw error;
  }
};

// Projects API
export const projectsApi = {
  // List all projects
  list: async (): Promise<Project[]> => {
    try {
      const response = await apiClient.get<Project[]>('/projects');
      return response.data;
    } catch (error) {
      handleApiError(error as AxiosError);
      throw error;
    }
  },

  // Get single project
  get: async (projectId: string): Promise<Project> => {
    try {
      const response = await apiClient.get<Project>(`/projects/${projectId}`);
      return response.data;
    } catch (error) {
      handleApiError(error as AxiosError);
      throw error;
    }
  },

  // Create project
  create: async (data: CreateProjectRequest): Promise<Project> => {
    try {
      const response = await apiClient.post<Project>('/projects', data);
      return response.data;
    } catch (error) {
      handleApiError(error as AxiosError);
      throw error;
    }
  },

  // Delete project
  delete: async (projectId: string): Promise<void> => {
    try {
      await apiClient.delete(`/projects/${projectId}`);
    } catch (error) {
      handleApiError(error as AxiosError);
      throw error;
    }
  },
};

// Agents API
export const agentsApi = {
  // List all agents
  list: async (): Promise<Agent[]> => {
    try {
      const response = await apiClient.get<Agent[]>('/agents');
      return response.data;
    } catch (error) {
      handleApiError(error as AxiosError);
      throw error;
    }
  },

  // Get agent status
  get: async (agentName: string): Promise<Agent> => {
    try {
      // Note: This endpoint might need to be added to backend
      const response = await apiClient.get<Agent>(`/agents/${agentName}`);
      return response.data;
    } catch (error) {
      handleApiError(error as AxiosError);
      throw error;
    }
  },
};

// Tasks API
export const tasksApi = {
  // Create task
  create: async (data: CreateTaskRequest): Promise<Task> => {
    try {
      const response = await apiClient.post<Task>('/tasks', data);
      return response.data;
    } catch (error) {
      handleApiError(error as AxiosError);
      throw error;
    }
  },

  // Get task status
  get: async (taskId: string): Promise<Task> => {
    try {
      const response = await apiClient.get<Task>(`/tasks/${taskId}`);
      return response.data;
    } catch (error) {
      handleApiError(error as AxiosError);
      throw error;
    }
  },
};

// Knowledge API
export const knowledgeApi = {
  // Add document
  addDocument: async (document: Document): Promise<{ id: string; status: string }> => {
    try {
      const response = await apiClient.post('/knowledge/documents', document);
      return response.data;
    } catch (error) {
      handleApiError(error as AxiosError);
      throw error;
    }
  },

  // Search documents
  search: async (request: SearchRequest): Promise<SearchResult[]> => {
    try {
      const response = await apiClient.post<SearchResult[]>('/knowledge/search', request);
      return response.data;
    } catch (error) {
      handleApiError(error as AxiosError);
      throw error;
    }
  },

  // Delete document
  deleteDocument: async (docId: string): Promise<void> => {
    try {
      await apiClient.delete(`/knowledge/documents/${docId}`);
    } catch (error) {
      handleApiError(error as AxiosError);
      throw error;
    }
  },

  // Get stats
  getStats: async (): Promise<KnowledgeStats> => {
    try {
      const response = await apiClient.get<KnowledgeStats>('/knowledge/stats');
      return response.data;
    } catch (error) {
      handleApiError(error as AxiosError);
      throw error;
    }
  },
};
