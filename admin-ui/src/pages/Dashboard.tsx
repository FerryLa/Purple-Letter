import { Newspaper, CheckSquare, TrendingUp, RefreshCw } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { NewsCard } from '@/components/news'
import { LoadingSpinner, EmptyState, ErrorMessage } from '@/components/shared'
import {
  useRecommendedNews,
  useNews,
  useNewsletter,
  useSyncStatus,
  useTriggerSync,
} from '@/hooks'
import { format } from 'date-fns'
import { ko } from 'date-fns/locale'

export function Dashboard() {
  const { data: recommended, isLoading: isLoadingRecommended, error: recommendedError } = useRecommendedNews(4)
  const { data: allNews } = useNews({ limit: 1 })
  const { data: newsletter } = useNewsletter()
  const { data: syncStatus } = useSyncStatus()
  const triggerSync = useTriggerSync()

  const totalArticles = allNews?.total ?? 0
  const selectedCount = newsletter?.selected_count ?? 0
  const avgScore =
    recommended?.data && recommended.data.length > 0
      ? (
          recommended.data.reduce((sum, n) => sum + n.impact_score, 0) /
          recommended.data.length
        ).toFixed(1)
      : '-'

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            오늘의 뉴스 인텔리전스 현황
          </p>
        </div>
        <Button
          variant="outline"
          onClick={() => triggerSync.mutate()}
          disabled={triggerSync.isPending}
        >
          <RefreshCw
            className={`h-4 w-4 mr-2 ${triggerSync.isPending ? 'animate-spin' : ''}`}
          />
          데이터 동기화
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">전체 뉴스</CardTitle>
            <Newspaper className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalArticles}</div>
            <p className="text-xs text-muted-foreground">
              분석된 기사 수
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">선택된 뉴스</CardTitle>
            <CheckSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{selectedCount}</div>
            <p className="text-xs text-muted-foreground">
              뉴스레터용 선택
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">평균 점수</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{avgScore}</div>
            <p className="text-xs text-muted-foreground">
              추천 뉴스 ImpactScore
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">마지막 동기화</CardTitle>
            <RefreshCw className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {syncStatus?.last_sync
                ? format(new Date(syncStatus.last_sync), 'HH:mm', { locale: ko })
                : '-'}
            </div>
            <p className="text-xs text-muted-foreground">
              {syncStatus?.articles_synced ?? 0}개 동기화됨
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recommended News */}
      <div>
        <h2 className="text-lg font-semibold mb-4">추천 뉴스 Top 4</h2>

        {isLoadingRecommended && (
          <LoadingSpinner className="py-12" />
        )}

        {recommendedError && (
          <ErrorMessage message="추천 뉴스를 불러오는 중 오류가 발생했습니다." />
        )}

        {!isLoadingRecommended && !recommendedError && (
          <>
            {recommended?.data && recommended.data.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2">
                {recommended.data.map((news) => (
                  <NewsCard key={news.id} news={news} />
                ))}
              </div>
            ) : (
              <EmptyState
                title="추천 뉴스가 없습니다"
                description="선택되지 않은 높은 점수의 뉴스가 없습니다."
              />
            )}
          </>
        )}
      </div>
    </div>
  )
}
