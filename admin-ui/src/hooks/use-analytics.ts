import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import type { SectorAnalytics, ScoreAnalytics, TagAnalytics } from '@/types'

export const analyticsKeys = {
  all: ['analytics'] as const,
  sectors: () => [...analyticsKeys.all, 'sectors'] as const,
  scores: () => [...analyticsKeys.all, 'scores'] as const,
  tags: () => [...analyticsKeys.all, 'tags'] as const,
}

export function useSectorAnalytics() {
  return useQuery({
    queryKey: analyticsKeys.sectors(),
    queryFn: () => apiClient.get<SectorAnalytics>('/analytics/sectors'),
    staleTime: 60000,
  })
}

export function useScoreAnalytics() {
  return useQuery({
    queryKey: analyticsKeys.scores(),
    queryFn: () => apiClient.get<ScoreAnalytics>('/analytics/scores'),
    staleTime: 60000,
  })
}

export function useTagAnalytics() {
  return useQuery({
    queryKey: analyticsKeys.tags(),
    queryFn: () => apiClient.get<TagAnalytics>('/analytics/tags'),
    staleTime: 60000,
  })
}
