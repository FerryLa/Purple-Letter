import { useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { NewsTable, NewsFilters } from '@/components/news'
import { LoadingSpinner, EmptyState, ErrorMessage } from '@/components/shared'
import { useNews } from '@/hooks'
import type { NewsFilters as FiltersType } from '@/types'

const PAGE_SIZE = 20

export function NewsList() {
  const [filters, setFilters] = useState<FiltersType>({
    limit: PAGE_SIZE,
    offset: 0,
  })

  const { data, isLoading, error } = useNews(filters)

  const currentPage = Math.floor((filters.offset ?? 0) / PAGE_SIZE) + 1
  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 0

  const handlePrevPage = () => {
    setFilters((prev) => ({
      ...prev,
      offset: Math.max(0, (prev.offset ?? 0) - PAGE_SIZE),
    }))
  }

  const handleNextPage = () => {
    setFilters((prev) => ({
      ...prev,
      offset: (prev.offset ?? 0) + PAGE_SIZE,
    }))
  }

  const handleFiltersChange = (newFilters: FiltersType) => {
    setFilters({
      ...newFilters,
      limit: PAGE_SIZE,
      offset: 0, // Reset to first page when filters change
    })
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold">News</h1>
        <p className="text-muted-foreground">
          전체 뉴스 목록을 확인하고 뉴스레터에 포함할 기사를 선택하세요.
        </p>
      </div>

      {/* Filters */}
      <NewsFilters filters={filters} onFiltersChange={handleFiltersChange} />

      {/* Content */}
      {isLoading && <LoadingSpinner className="py-12" />}

      {error && (
        <ErrorMessage message="뉴스 목록을 불러오는 중 오류가 발생했습니다." />
      )}

      {!isLoading && !error && (
        <>
          {data?.data && data.data.length > 0 ? (
            <>
              {/* Results Info */}
              <div className="text-sm text-muted-foreground">
                총 {data.total}개 중 {(filters.offset ?? 0) + 1}-
                {Math.min((filters.offset ?? 0) + PAGE_SIZE, data.total)}개 표시
              </div>

              {/* Table */}
              <NewsTable news={data.data} />

              {/* Pagination */}
              <div className="flex items-center justify-between">
                <div className="text-sm text-muted-foreground">
                  {currentPage} / {totalPages} 페이지
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handlePrevPage}
                    disabled={currentPage <= 1}
                  >
                    <ChevronLeft className="h-4 w-4 mr-1" />
                    이전
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleNextPage}
                    disabled={currentPage >= totalPages}
                  >
                    다음
                    <ChevronRight className="h-4 w-4 ml-1" />
                  </Button>
                </div>
              </div>
            </>
          ) : (
            <EmptyState
              title="뉴스가 없습니다"
              description="조건에 맞는 뉴스가 없습니다. 필터를 조정해 보세요."
            />
          )}
        </>
      )}
    </div>
  )
}
