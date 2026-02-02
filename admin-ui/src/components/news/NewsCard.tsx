import { ExternalLink, Clock, Check, Plus } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ImpactScoreBadge } from './ImpactScoreBadge'
import { StrategicTagBadge } from './StrategicTagBadge'
import { SECTOR_LABELS } from '@/lib/constants'
import { useSelectArticle, useDeselectArticle } from '@/hooks'
import { format } from 'date-fns'
import { ko } from 'date-fns/locale'
import type { NewsItem } from '@/types'

interface NewsCardProps {
  news: NewsItem
  showSelectButton?: boolean
}

export function NewsCard({ news, showSelectButton = true }: NewsCardProps) {
  const selectArticle = useSelectArticle()
  const deselectArticle = useDeselectArticle()

  const handleToggleSelect = () => {
    if (news.selected) {
      deselectArticle.mutate(news.id)
    } else {
      selectArticle.mutate(news.id)
    }
  }

  const isLoading = selectArticle.isPending || deselectArticle.isPending

  return (
    <Card className="overflow-hidden hover:shadow-md transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            {/* Tags */}
            <div className="flex items-center gap-2 mb-2">
              <ImpactScoreBadge
                score={news.impact_score}
                showBreakdown
                breakdown={{
                  market_relevance: news.market_relevance,
                  business_relevance: news.business_relevance,
                  tech_shift: news.tech_shift,
                  urgency: news.urgency,
                }}
              />
              <StrategicTagBadge tag={news.strategic_tag} />
              {news.primary_sector && (
                <span className="text-xs text-muted-foreground">
                  {SECTOR_LABELS[news.primary_sector] || news.primary_sector}
                </span>
              )}
            </div>

            {/* Title */}
            <h3 className="font-medium text-sm line-clamp-2 mb-2">
              {news.title}
            </h3>

            {/* Meta */}
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              <span>{news.source}</span>
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {format(new Date(news.published_at), 'MM/dd HH:mm', {
                  locale: ko,
                })}
              </span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-col items-end gap-2">
            {showSelectButton && (
              <Button
                variant={news.selected ? 'default' : 'outline'}
                size="sm"
                onClick={handleToggleSelect}
                disabled={isLoading}
                className="w-8 h-8 p-0"
              >
                {news.selected ? (
                  <Check className="h-4 w-4" />
                ) : (
                  <Plus className="h-4 w-4" />
                )}
              </Button>
            )}
            <a
              href={news.link}
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground hover:text-foreground"
            >
              <ExternalLink className="h-4 w-4" />
            </a>
          </div>
        </div>

        {/* Summary (optional) */}
        {news.summary && (
          <p className="text-xs text-muted-foreground mt-3 line-clamp-2">
            {news.summary}
          </p>
        )}
      </CardContent>
    </Card>
  )
}
