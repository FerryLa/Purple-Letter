import { Trash2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { NewsCard } from '@/components/news'
import { ValidationStatus, SectorCoverage } from '@/components/newsletter'
import { LoadingSpinner, EmptyState, ErrorMessage } from '@/components/shared'
import { useNewsletter, useNewsletterPreview, useClearSelections } from '@/hooks'

export function Newsletter() {
  const { data: newsletter, isLoading, error } = useNewsletter()
  const { data: preview } = useNewsletterPreview()
  const clearSelections = useClearSelections()

  const handleClearAll = () => {
    if (window.confirm('모든 선택을 해제하시겠습니까?')) {
      clearSelections.mutate()
    }
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Newsletter</h1>
          <p className="text-muted-foreground">
            선택된 뉴스를 확인하고 뉴스레터를 준비하세요.
          </p>
        </div>
        {newsletter?.data && newsletter.data.length > 0 && (
          <Button
            variant="outline"
            onClick={handleClearAll}
            disabled={clearSelections.isPending}
          >
            <Trash2 className="h-4 w-4 mr-2" />
            전체 해제
          </Button>
        )}
      </div>

      {/* Content */}
      {isLoading && <LoadingSpinner className="py-12" />}

      {error && (
        <ErrorMessage message="뉴스레터 데이터를 불러오는 중 오류가 발생했습니다." />
      )}

      {!isLoading && !error && (
        <>
          {newsletter?.data && newsletter.data.length > 0 ? (
            <div className="grid gap-6 lg:grid-cols-3">
              {/* Main Content */}
              <div className="lg:col-span-2 space-y-4">
                <h2 className="text-lg font-semibold">
                  선택된 뉴스 ({newsletter.selected_count}개)
                </h2>
                <div className="space-y-4">
                  {newsletter.data.map((news) => (
                    <NewsCard key={news.id} news={news} />
                  ))}
                </div>
              </div>

              {/* Sidebar */}
              <div className="space-y-4">
                {/* Stats Card */}
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base">뉴스레터 요약</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-2xl font-bold">
                          {newsletter.selected_count}
                        </p>
                        <p className="text-xs text-muted-foreground">선택된 기사</p>
                      </div>
                      <div>
                        <p className="text-2xl font-bold">
                          {preview?.preview.avg_impact_score.toFixed(1) ?? '-'}
                        </p>
                        <p className="text-xs text-muted-foreground">평균 점수</p>
                      </div>
                    </div>

                    {/* Sector Coverage */}
                    {preview?.preview.sectors_covered && (
                      <SectorCoverage sectors={preview.preview.sectors_covered} />
                    )}
                  </CardContent>
                </Card>

                {/* Validation */}
                {preview?.validation && (
                  <ValidationStatus validation={preview.validation} />
                )}
              </div>
            </div>
          ) : (
            <EmptyState
              title="선택된 뉴스가 없습니다"
              description="News 페이지에서 뉴스레터에 포함할 기사를 선택해 주세요."
            />
          )}
        </>
      )}
    </div>
  )
}
