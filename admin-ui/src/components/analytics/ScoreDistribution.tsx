import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface ScoreDistributionProps {
  data: Record<string, number>
}

export function ScoreDistribution({ data }: ScoreDistributionProps) {
  // Ensure all scores from 4-10 are represented
  const chartData = Array.from({ length: 7 }, (_, i) => {
    const score = i + 4
    return {
      score: score.toString(),
      count: data[score.toString()] || 0,
    }
  })

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">ImpactScore 분포</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis
                dataKey="score"
                tickLine={false}
                axisLine={false}
                fontSize={12}
              />
              <YAxis tickLine={false} axisLine={false} fontSize={12} />
              <Tooltip
                formatter={(value) => [`${value}개`, '기사 수']}
                labelFormatter={(label) => `점수: ${label}`}
              />
              <Bar
                dataKey="count"
                radius={[4, 4, 0, 0]}
                fill="#7C3AED"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
