'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface ChartDataPoint {
  month: string;
  standard: number;
  optimized: number;
}

interface CostChartProps {
  data: ChartDataPoint[];
  title?: string;
}

export function CostChart({ data, title = 'Kosteneinsparungen im Jahresverlauf' }: CostChartProps) {
  return (
    <div className="bg-white rounded-lg p-4 border border-gray-100">
      <h3 className="text-sm font-semibold text-text-primary mb-3">{title}</h3>
      <ResponsiveContainer width="100%" height={180}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis
            dataKey="month"
            stroke="#6B7280"
            style={{ fontSize: '12px' }}
          />
          <YAxis
            stroke="#6B7280"
            style={{ fontSize: '12px' }}
            tickFormatter={(value) => `€${value}`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#FFFFFF',
              border: '1px solid #E5E7EB',
              borderRadius: '8px',
            }}
            formatter={(value: number) => [`€${value.toLocaleString('de-DE')}`, '']}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="standard"
            stroke="#F0C987"
            strokeWidth={2}
            name="Standard"
            dot={{ fill: '#F0C987', r: 4 }}
          />
          <Line
            type="monotone"
            dataKey="optimized"
            stroke="#86BCAC"
            strokeWidth={2}
            name="AI-Optimiert"
            dot={{ fill: '#86BCAC', r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
