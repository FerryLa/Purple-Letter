import { ExternalLink, Check, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ImpactScoreBadge } from './ImpactScoreBadge'
import { StrategicTagBadge } from './StrategicTagBadge'
import { SECTOR_LABELS } from '@/lib/constants'
import { useSelectArticle, useDeselectArticle } from '@/hooks'
import { format } from 'date-fns'
import { ko } from 'date-fns/locale'
import type { NewsItem } from '@/types'

interface NewsTableProps {
  news: NewsItem[]
}

export function NewsTable({ news }: NewsTableProps) {
  const selectArticle = useSelectArticle()
  const deselectArticle = useDeselectArticle()

  const handleToggleSelect = (item: NewsItem) => {
    if (item.selected) {
      deselectArticle.mutate(item.id)
    } else {
      selectArticle.mutate(item.id)
    }
  }

  return (
    <div className="rounded-md border">
      <table className="w-full">
        <thead>
          <tr className="border-b bg-muted/50">
            <th className="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-12">
              선택
            </th>
            <th className="h-10 px-4 text-left align-middle font-medium text-muted-foreground">
              제목
            </th>
            <th className="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-24">
              점수
            </th>
            <th className="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-24">
              태그
            </th>
            <th className="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-28">
              섹터
            </th>
            <th className="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-24">
              출처
            </th>
            <th className="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-32">
              발행일
            </th>
            <th className="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-12">
              링크
            </th>
          </tr>
        </thead>
        <tbody>
          {news.map((item) => (
            <tr key={item.id} className="border-b hover:bg-muted/50 transition-colors">
              <td className="p-4">
                <Button
                  variant={item.selected ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => handleToggleSelect(item)}
                  disabled={selectArticle.isPending || deselectArticle.isPending}
                  className="w-8 h-8 p-0"
                >
                  {item.selected ? (
                    <Check className="h-4 w-4" />
                  ) : (
                    <Plus className="h-4 w-4" />
                  )}
                </Button>
              </td>
              <td className="p-4">
                <span className="line-clamp-2 text-sm">{item.title}</span>
              </td>
              <td className="p-4">
                <ImpactScoreBadge
                  score={item.impact_score}
                  showBreakdown
                  breakdown={{
                    market_relevance: item.market_relevance,
                    business_relevance: item.business_relevance,
                    tech_shift: item.tech_shift,
                    urgency: item.urgency,
                  }}
                />
              </td>
              <td className="p-4">
                <StrategicTagBadge tag={item.strategic_tag} />
              </td>
              <td className="p-4">
                <span className="text-sm text-muted-foreground">
                  {item.primary_sector
                    ? SECTOR_LABELS[item.primary_sector] || item.primary_sector
                    : '-'}
                </span>
              </td>
              <td className="p-4">
                <span className="text-sm text-muted-foreground truncate block max-w-24">
                  {item.source}
                </span>
              </td>
              <td className="p-4">
                <span className="text-sm text-muted-foreground">
                  {format(new Date(item.published_at), 'MM/dd HH:mm', {
                    locale: ko,
                  })}
                </span>
              </td>
              <td className="p-4">
                <a
                  href={item.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-foreground"
                >
                  <ExternalLink className="h-4 w-4" />
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
