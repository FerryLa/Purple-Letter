import { useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import type { SelectionResponse } from '@/types'
import { newsKeys } from './use-news'
import { newsletterKeys } from './use-newsletter'

export function useSelectArticle() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (articleId: string) =>
      apiClient.post<SelectionResponse>(`/news/select/${articleId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: newsKeys.all })
      queryClient.invalidateQueries({ queryKey: newsletterKeys.all })
    },
  })
}

export function useDeselectArticle() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (articleId: string) =>
      apiClient.delete<SelectionResponse>(`/news/select/${articleId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: newsKeys.all })
      queryClient.invalidateQueries({ queryKey: newsletterKeys.all })
    },
  })
}

export function useBulkSelect() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (newsIds: string[]) =>
      apiClient.post<SelectionResponse>('/news/select', { news_ids: newsIds }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: newsKeys.all })
      queryClient.invalidateQueries({ queryKey: newsletterKeys.all })
    },
  })
}

export function useClearSelections() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => apiClient.delete<SelectionResponse>('/news/select'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: newsKeys.all })
      queryClient.invalidateQueries({ queryKey: newsletterKeys.all })
    },
  })
}
