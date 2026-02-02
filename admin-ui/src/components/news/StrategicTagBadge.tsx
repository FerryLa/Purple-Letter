import { cn } from '@/lib/utils'
import { STRATEGIC_TAG_COLORS, STRATEGIC_TAG_LABELS } from '@/lib/constants'
import type { StrategicTag } from '@/types'

interface StrategicTagBadgeProps {
  tag: StrategicTag
}

export function StrategicTagBadge({ tag }: StrategicTagBadgeProps) {
  const colorClass = STRATEGIC_TAG_COLORS[tag] || STRATEGIC_TAG_COLORS.neutral
  const label = STRATEGIC_TAG_LABELS[tag] || tag

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium',
        colorClass
      )}
    >
      {label}
    </span>
  )
}
