import { RefreshCw, CheckCircle2, XCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useHealth, useSyncStatus, useTriggerSync } from '@/hooks'
import { format } from 'date-fns'
import { ko } from 'date-fns/locale'

export function Header() {
  const { data: health } = useHealth()
  const { data: syncStatus } = useSyncStatus()
  const triggerSync = useTriggerSync()

  const isHealthy = health?.status === 'healthy'
  const lastSync = syncStatus?.last_sync
    ? format(new Date(syncStatus.last_sync), 'MM/dd HH:mm', { locale: ko })
    : '없음'

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-14 items-center justify-between px-6">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
            <span className="text-white font-bold text-sm">P</span>
          </div>
          <h1 className="text-lg font-semibold">Purple Letter Admin</h1>
        </div>

        <div className="flex items-center gap-4">
          {/* Health Status */}
          <div className="flex items-center gap-2 text-sm">
            {isHealthy ? (
              <CheckCircle2 className="h-4 w-4 text-green-500" />
            ) : (
              <XCircle className="h-4 w-4 text-red-500" />
            )}
            <span className="text-muted-foreground">
              {isHealthy ? '연결됨' : '연결 끊김'}
            </span>
          </div>

          {/* Last Sync */}
          <div className="text-sm text-muted-foreground">
            마지막 동기화: {lastSync}
          </div>

          {/* Sync Button */}
          <Button
            variant="outline"
            size="sm"
            onClick={() => triggerSync.mutate()}
            disabled={triggerSync.isPending}
          >
            <RefreshCw
              className={`h-4 w-4 mr-2 ${triggerSync.isPending ? 'animate-spin' : ''}`}
            />
            동기화
          </Button>
        </div>
      </div>
    </header>
  )
}
