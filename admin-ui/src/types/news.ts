export type StrategicTag =
  | 'opportunity'
  | 'risk'
  | 'trend'
  | 'policy'
  | 'breaking'
  | 'exclusive'
  | 'neutral'

export type SectorType =
  | 'macro_economy'
  | 'social_policy'
  | 'finance'
  | 'industry_tech'
  | 'culture_lifestyle'

export interface NewsItem {
  id: string
  title: string
  link: string
  summary: string
  source: string
  published_at: string
  date: string
  image_url: string | null
  primary_sector: SectorType | null
  secondary_sector: SectorType | null
  subcategories: string[]
  market_relevance: number
  business_relevance: number
  tech_shift: number
  urgency: number
  impact_score: number
  strategic_tag: StrategicTag
  selected: boolean
  selected_at: string | null
  original_score: number | null
  matched_keywords: string[]
  why_it_matters: string | null
  implication: string | null
}

export interface NewsFilters {
  min_score?: number
  sector?: SectorType
  category?: string
  limit?: number
  offset?: number
}
