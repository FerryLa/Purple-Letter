import { SECTOR_LABELS, SECTOR_COLORS } from '@/lib/constants'

interface SectorCoverageProps {
  sectors: string[]
}

export function SectorCoverage({ sectors }: SectorCoverageProps) {
  const allSectors = Object.keys(SECTOR_LABELS)
  const coveredSet = new Set(sectors)

  return (
    <div className="space-y-2">
      <h4 className="text-sm font-medium">섹터 커버리지</h4>
      <div className="flex flex-wrap gap-2">
        {allSectors.map((sector) => {
          const isCovered = coveredSet.has(sector)
          const color = SECTOR_COLORS[sector] || '#6B7280'

          return (
            <div
              key={sector}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-opacity ${
                isCovered ? 'opacity-100' : 'opacity-30'
              }`}
              style={{
                backgroundColor: isCovered ? `${color}20` : '#f3f4f6',
                color: isCovered ? color : '#9ca3af',
                border: `1px solid ${isCovered ? color : '#e5e7eb'}`,
              }}
            >
              <span
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: isCovered ? color : '#d1d5db' }}
              />
              {SECTOR_LABELS[sector]}
            </div>
          )
        })}
      </div>
      <p className="text-xs text-muted-foreground">
        {sectors.length}개 섹터 / {allSectors.length}개 전체
      </p>
    </div>
  )
}
