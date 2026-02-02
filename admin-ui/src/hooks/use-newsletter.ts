import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import type { NewsletterResponse, NewsletterPreviewResponse } from '@/types'

export const newsletterKeys = {
  all: ['newsletter'] as const,
  selected: () => [...newsletterKeys.all, 'selected'] as const,
  preview: () => [...newsletterKeys.all, 'preview'] as const,
}

export function useNewsletter() {
  return useQuery({
    queryKey: newsletterKeys.selected(),
    queryFn: () => apiClient.get<NewsletterResponse>('/newsletter'),
  })
}

export function useNewsletterPreview() {
  return useQuery({
    queryKey: newsletterKeys.preview(),
    queryFn: () => apiClient.get<NewsletterPreviewResponse>('/newsletter/preview'),
  })
}
