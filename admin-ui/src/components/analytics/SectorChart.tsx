import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { SECTOR_LABELS, SECTOR_COLORS } from '@/lib/constants'

interface SectorChartProps {
  data: Record<string, number>
}

export function SectorChart({ data }: SectorChartProps) {
  const chartData = Object.entries(data).map(([key, value]) => ({
    name: SECTOR_LABELS[key] || key,
    value,
    color: SECTOR_COLORS[key] || '#6B7280',
  }))

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">섹터별 분포</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={2}
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value) => [`${value}개`, '기사 수']}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
