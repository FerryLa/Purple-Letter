import { Select } from '@/components/ui/select'
import { SECTOR_LABELS } from '@/lib/constants'
import type { SectorType, NewsFilters as FiltersType } from '@/types'

interface NewsFiltersProps {
  filters: FiltersType
  onFiltersChange: (filters: FiltersType) => void
}

export function NewsFilters({ filters, onFiltersChange }: NewsFiltersProps) {
  const handleMinScoreChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value
    onFiltersChange({
      ...filters,
      min_score: value ? Number(value) : undefined,
    })
  }

  const handleSectorChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value as SectorType | ''
    onFiltersChange({
      ...filters,
      sector: value || undefined,
    })
  }

  return (
    <div className="flex flex-wrap gap-3">
      {/* Min Score Filter */}
      <div className="w-40">
        <Select value={filters.min_score?.toString() ?? ''} onChange={handleMinScoreChange}>
          <option value="">모든 점수</option>
          <option value="10">10점</option>
          <option value="9">9점 이상</option>
          <option value="8">8점 이상</option>
          <option value="7">7점 이상</option>
          <option value="6">6점 이상</option>
          <option value="5">5점 이상</option>
        </Select>
      </div>

      {/* Sector Filter */}
      <div className="w-40">
        <Select value={filters.sector ?? ''} onChange={handleSectorChange}>
          <option value="">모든 섹터</option>
          {Object.entries(SECTOR_LABELS).map(([key, label]) => (
            <option key={key} value={key}>
              {label}
            </option>
          ))}
        </Select>
      </div>
    </div>
  )
}
