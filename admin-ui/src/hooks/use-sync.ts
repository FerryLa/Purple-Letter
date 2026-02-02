import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import type { SyncStatus, SyncResponse, HealthCheckResponse } from '@/types'
import { newsKeys } from './use-news'

export const syncKeys = {
  status: ['sync', 'status'] as const,
  health: ['health'] as const,
}

export function useSyncStatus() {
  return useQuery({
    queryKey: syncKeys.status,
    queryFn: () => apiClient.get<SyncStatus>('/sync/status'),
    refetchInterval: 60000,
  })
}

export function useHealth() {
  return useQuery({
    queryKey: syncKeys.health,
    queryFn: () => apiClient.get<HealthCheckResponse>('/health'),
    refetchInterval: 30000,
  })
}

export function useTriggerSync() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => apiClient.post<SyncResponse>('/sync'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: syncKeys.status })
      queryClient.invalidateQueries({ queryKey: newsKeys.all })
    },
  })
}
