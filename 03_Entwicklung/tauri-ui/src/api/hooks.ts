import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectsApi, agentsApi, tasksApi, knowledgeApi } from './client';
import type { CreateProjectRequest, CreateTaskRequest, Document, SearchRequest } from '../types';

// Projects Hooks
export const useProjects = () => {
  return useQuery({
    queryKey: ['projects'],
    queryFn: () => projectsApi.list(),
  });
};

export const useProject = (projectId: string) => {
  return useQuery({
    queryKey: ['projects', projectId],
    queryFn: () => projectsApi.get(projectId),
    enabled: !!projectId,
  });
};

export const useCreateProject = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: CreateProjectRequest) => projectsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
};

export const useDeleteProject = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (projectId: string) => projectsApi.delete(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
};

// Agents Hooks
export const useAgents = () => {
  return useQuery({
    queryKey: ['agents'],
    queryFn: () => agentsApi.list(),
    refetchInterval: 5000, // Refetch every 5 seconds for live status
  });
};

// Tasks Hooks
export const useCreateTask = () => {
  return useMutation({
    mutationFn: (data: CreateTaskRequest) => tasksApi.create(data),
  });
};

export const useTask = (taskId: string | null) => {
  return useQuery({
    queryKey: ['tasks', taskId],
    queryFn: () => tasksApi.get(taskId!),
    enabled: !!taskId,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (data?.status === 'running') return 1000; // Poll every second if running
      return false; // Stop polling if not running
    },
  });
};

// Knowledge Hooks
export const useKnowledgeStats = () => {
  return useQuery({
    queryKey: ['knowledge', 'stats'],
    queryFn: () => knowledgeApi.getStats(),
  });
};

export const useSearchDocuments = () => {
  return useMutation({
    mutationFn: (request: SearchRequest) => knowledgeApi.search(request),
  });
};

export const useAddDocument = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (document: Document) => knowledgeApi.addDocument(document),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['knowledge', 'stats'] });
    },
  });
};

export const useDeleteDocument = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (docId: string) => knowledgeApi.deleteDocument(docId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['knowledge', 'stats'] });
    },
  });
};
