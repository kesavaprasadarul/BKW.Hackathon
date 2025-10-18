'use client';

import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface CostData {
  month: string;
  standard: number;
  optimized: number;
}

interface CombinedCostSavingsChartProps {
  data: CostData[];
  title: string;
}

export function CombinedCostSavingsChart({ data, title }: CombinedCostSavingsChartProps) {
  // Calculate cumulative savings
  const combinedData = data.map((item, index) => {
    const cumulativeSavings = data
      .slice(0, index + 1)
      .reduce((sum, curr) => sum + (curr.standard - curr.optimized), 0);
    return {
      month: item.month,
      standard: item.standard,
      optimized: item.optimized,
      cumulative: cumulativeSavings,
    };
  });

  return (
    <div className="bg-white rounded-lg p-4 border border-gray-100">
      <h3 className="text-sm font-semibold text-text-primary mb-3">{title}</h3>

      {/* Monthly Cost Chart - No Legend */}
      <ResponsiveContainer width="100%" height={180}>
        <LineChart data={combinedData} margin={{ top: 5, right: 20, bottom: 0, left: 0 }}>
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
            formatter={(value: number) => `€${value.toLocaleString('de-DE')}`}
          />
          <Line
            type="monotone"
            dataKey="standard"
            stroke="#F0C987"
            strokeWidth={2}
            dot={false}
            name="Standard"
          />
          <Line
            type="monotone"
            dataKey="optimized"
            stroke="#86BCAC"
            strokeWidth={2}
            dot={false}
            name="AI-Optimiert"
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Cumulative Savings Chart - No Legend */}
      <ResponsiveContainer width="100%" height={180}>
        <AreaChart data={combinedData} margin={{ top: 0, right: 20, bottom: 5, left: 0 }}>
          <defs>
            <linearGradient id="savingsGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#5B8DBE" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#5B8DBE" stopOpacity={0} />
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
            dataKey="cumulative"
            stroke="#5B8DBE"
            strokeWidth={2}
            fill="url(#savingsGradient)"
            name="Kumulierte Einsparung"
          />
        </AreaChart>
      </ResponsiveContainer>

      {/* Custom Legend Below */}
      <div className="flex items-center justify-center gap-6 mt-2 text-xs">
        <div className="flex items-center gap-1.5">
          <div className="w-6 h-0.5 bg-[#F0C987]"></div>
          <span className="text-text-secondary">Standard</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-6 h-0.5 bg-[#86BCAC]"></div>
          <span className="text-text-secondary">AI-Optimiert</span>
        </div>
        <div className="h-4 w-px bg-gray-300"></div>
        <div className="flex items-center gap-1.5">
          <div className="w-6 h-0.5 bg-[#5B8DBE]"></div>
          <span className="text-text-secondary">Kumulierte Einsparung</span>
        </div>
      </div>
    </div>
  );
}
