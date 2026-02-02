import type { NewsItem } from './news'

export interface ApiResponse<T> {
  success: boolean
  data: T
}

export interface NewsListResponse {
  success: boolean
  total: number
  data: NewsItem[]
}

export interface NewsItemResponse {
  success: boolean
  data: NewsItem
}

export interface NewsletterResponse {
  success: boolean
  selected_count: number
  newsletter_date: string
  data: NewsItem[]
}

export interface SelectionRequest {
  news_ids: string[]
}

export interface SelectionResponse {
  success: boolean
  selected_count: number
  message: string
}

export interface ValidationResult {
  is_valid: boolean
  selected_count: number
  warnings: string[]
  recommendations: string[]
}

export interface NewsletterPreviewArticle {
  id: string
  title: string
  source: string
  impact_score: number
  strategic_tag: string
  primary_sector: string
}

export interface NewsletterPreview {
  date: string
  article_count: number
  articles: NewsletterPreviewArticle[]
  sectors_covered: string[]
  avg_impact_score: number
}

export interface NewsletterPreviewResponse {
  preview: NewsletterPreview
  validation: ValidationResult
}

export interface SyncResponse {
  success: boolean
  message: string
  details: {
    articles_synced: number
    articles_transformed: number
    articles_scored: number
    errors: string[]
  }
}

export interface SyncStatus {
  last_sync: string | null
  articles_synced: number
  articles_transformed: number
  articles_scored: number
  errors: string[]
}

export interface HealthCheckResponse {
  status: string
  version: string
  database_connected: boolean
  news_scanner_connected: boolean
  last_sync: string | null
}

export interface SectorAnalytics {
  total_articles: number
  sector_distribution: Record<string, number>
}

export interface ScoreAnalytics {
  total_articles: number
  score_distribution: Record<string, number>
}

export interface TagAnalytics {
  total_articles: number
  tag_distribution: Record<string, number>
}

export interface DatasetResponse {
  success: boolean
  last_updated: string
  total_records: number
  data: NewsItem[]
}
