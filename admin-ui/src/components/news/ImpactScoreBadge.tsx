import { cn } from '@/lib/utils'
import { getImpactScoreColor } from '@/lib/constants'

interface ImpactScoreBadgeProps {
  score: number
  showBreakdown?: boolean
  breakdown?: {
    market_relevance: number
    business_relevance: number
    tech_shift: number
    urgency: number
  }
}

export function ImpactScoreBadge({
  score,
  showBreakdown = false,
  breakdown,
}: ImpactScoreBadgeProps) {
  return (
    <div className="relative group">
      <span
        className={cn(
          'inline-flex items-center justify-center rounded-full px-2.5 py-0.5 text-xs font-bold',
          getImpactScoreColor(score)
        )}
      >
        {score}
      </span>

      {showBreakdown && breakdown && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-10">
          <div className="bg-popover text-popover-foreground rounded-lg shadow-lg border p-3 text-xs whitespace-nowrap">
            <div className="grid grid-cols-2 gap-x-4 gap-y-1">
              <span className="text-muted-foreground">시장 관련성:</span>
              <span className="font-medium">{breakdown.market_relevance}/3</span>
              <span className="text-muted-foreground">비즈니스:</span>
              <span className="font-medium">{breakdown.business_relevance}/3</span>
              <span className="text-muted-foreground">기술 영향:</span>
              <span className="font-medium">{breakdown.tech_shift}/2</span>
              <span className="text-muted-foreground">긴급도:</span>
              <span className="font-medium">{breakdown.urgency}/2</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
