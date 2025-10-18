'use client';

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface CumulativeSavingsChartProps {
  data: { month: string; savings: number }[];
  title: string;
}

export function CumulativeSavingsChart({ data, title }: CumulativeSavingsChartProps) {
  return (
    <div className="bg-white rounded-lg p-4 border border-gray-100">
      <h3 className="text-sm font-semibold text-text-primary mb-3">{title}</h3>
      <ResponsiveContainer width="100%" height={180}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="savingsGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#86BCAC" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#86BCAC" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis
            dataKey="month"
            tick={{ fontSize: 11, fill: '#6B7280' }}
            axisLine={{ stroke: '#E5E7EB' }}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#6B7280' }}
            axisLine={{ stroke: '#E5E7EB' }}
            tickFormatter={(value) => `€${(value / 1000).toFixed(0)}k`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #E5E7EB',
              borderRadius: '8px',
              fontSize: '12px',
            }}
            formatter={(value: number) => [`€${value.toLocaleString('de-DE')}`, 'Kumulierte Einsparung']}
          />
          <Area
            type="monotone"
            dataKey="savings"
            stroke="#86BCAC"
            strokeWidth={2}
            fill="url(#savingsGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
