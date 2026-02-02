import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { STRATEGIC_TAG_LABELS } from '@/lib/constants'

const TAG_CHART_COLORS: Record<string, string> = {
  opportunity: '#22C55E',
  risk: '#EF4444',
  trend: '#3B82F6',
  policy: '#F97316',
  breaking: '#A855F7',
  exclusive: '#EC4899',
  neutral: '#6B7280',
}

interface TagBreakdownProps {
  data: Record<string, number>
}

export function TagBreakdown({ data }: TagBreakdownProps) {
  const chartData = Object.entries(data)
    .map(([key, value]) => ({
      tag: key,
      name: STRATEGIC_TAG_LABELS[key] || key,
      count: value,
      color: TAG_CHART_COLORS[key] || '#6B7280',
    }))
    .sort((a, b) => b.count - a.count)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Strategic Tag 분포</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" tickLine={false} axisLine={false} fontSize={12} />
              <YAxis
                type="category"
                dataKey="name"
                tickLine={false}
                axisLine={false}
                fontSize={12}
                width={60}
              />
              <Tooltip
                formatter={(value) => [`${value}개`, '기사 수']}
              />
              <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
