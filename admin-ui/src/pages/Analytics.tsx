import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { SectorChart, ScoreDistribution, TagBreakdown } from '@/components/analytics'
import { LoadingSpinner, ErrorMessage } from '@/components/shared'
import { useSectorAnalytics, useScoreAnalytics, useTagAnalytics } from '@/hooks'

export function Analytics() {
  const {
    data: sectorData,
    isLoading: isLoadingSectors,
    error: sectorError,
  } = useSectorAnalytics()
  const {
    data: scoreData,
    isLoading: isLoadingScores,
    error: scoreError,
  } = useScoreAnalytics()
  const {
    data: tagData,
    isLoading: isLoadingTags,
    error: tagError,
  } = useTagAnalytics()

  const isLoading = isLoadingSectors || isLoadingScores || isLoadingTags
  const hasError = sectorError || scoreError || tagError

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold">Analytics</h1>
        <p className="text-muted-foreground">
          뉴스 데이터의 분포와 트렌드를 분석합니다.
        </p>
      </div>

      {isLoading && <LoadingSpinner className="py-12" />}

      {hasError && (
        <ErrorMessage message="분석 데이터를 불러오는 중 오류가 발생했습니다." />
      )}

      {!isLoading && !hasError && (
        <>
          {/* Stats Overview */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  전체 기사
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {sectorData?.total_articles ?? 0}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  활성 섹터
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {sectorData
                    ? Object.keys(sectorData.sector_distribution).length
                    : 0}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  활성 태그
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {tagData ? Object.keys(tagData.tag_distribution).length : 0}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Charts Row 1 */}
          <div className="grid gap-6 md:grid-cols-2">
            {sectorData && (
              <SectorChart data={sectorData.sector_distribution} />
            )}
            {scoreData && (
              <ScoreDistribution data={scoreData.score_distribution} />
            )}
          </div>

          {/* Charts Row 2 */}
          <div className="grid gap-6 md:grid-cols-2">
            {tagData && <TagBreakdown data={tagData.tag_distribution} />}

            {/* Sector Table */}
            {sectorData && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">섹터별 기사 수</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(sectorData.sector_distribution)
                      .sort(([, a], [, b]) => b - a)
                      .map(([sector, count]) => {
                        const percentage = (
                          (count / sectorData.total_articles) *
                          100
                        ).toFixed(1)
                        return (
                          <div key={sector} className="flex items-center gap-3">
                            <div className="flex-1">
                              <div className="flex items-center justify-between text-sm">
                                <span className="capitalize">{sector.replace('_', ' ')}</span>
                                <span className="text-muted-foreground">
                                  {count}개 ({percentage}%)
                                </span>
                              </div>
                              <div className="mt-1 h-2 w-full rounded-full bg-muted">
                                <div
                                  className="h-2 rounded-full bg-primary"
                                  style={{ width: `${percentage}%` }}
                                />
                              </div>
                            </div>
                          </div>
                        )
                      })}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </>
      )}
    </div>
  )
}
