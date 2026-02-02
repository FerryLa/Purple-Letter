import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import type { NewsFilters, NewsListResponse, NewsItemResponse } from '@/types'

export const newsKeys = {
  all: ['news'] as const,
  lists: () => [...newsKeys.all, 'list'] as const,
  list: (filters: NewsFilters) => [...newsKeys.lists(), filters] as const,
  recommended: (topN: number) => [...newsKeys.all, 'recommended', topN] as const,
  detail: (id: string) => [...newsKeys.all, 'detail', id] as const,
}

export function useNews(filters: NewsFilters = {}) {
  return useQuery({
    queryKey: newsKeys.list(filters),
    queryFn: () =>
      apiClient.get<NewsListResponse>('/news', {
        min_score: filters.min_score,
        sector: filters.sector,
        category: filters.category,
        limit: filters.limit ?? 50,
        offset: filters.offset ?? 0,
      }),
    staleTime: 30000,
  })
}

export function useRecommendedNews(topN = 4) {
  return useQuery({
    queryKey: newsKeys.recommended(topN),
    queryFn: () =>
      apiClient.get<NewsListResponse>('/news/recommended', { top_n: topN }),
    staleTime: 30000,
  })
}

export function useNewsDetail(id: string) {
  return useQuery({
    queryKey: newsKeys.detail(id),
    queryFn: () => apiClient.get<NewsItemResponse>(`/news/${id}`),
    enabled: !!id,
  })
}
