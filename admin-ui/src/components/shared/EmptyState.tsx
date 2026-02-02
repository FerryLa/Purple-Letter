import { FileQuestion } from 'lucide-react'
import { cn } from '@/lib/utils'

interface EmptyStateProps {
  title?: string
  description?: string
  className?: string
}

export function EmptyState({
  title = '데이터가 없습니다',
  description = '표시할 항목이 없습니다.',
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center py-12 text-center',
        className
      )}
    >
      <FileQuestion className="h-12 w-12 text-muted-foreground mb-4" />
      <h3 className="text-lg font-medium">{title}</h3>
      <p className="text-sm text-muted-foreground mt-1">{description}</p>
    </div>
  )
}
