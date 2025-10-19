'use client';

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

interface SavingsBreakdownChartProps {
  totalSavings: number;
}

export function SavingsBreakdownChart({ totalSavings }: SavingsBreakdownChartProps) {
  // Breakdown of savings by optimization category
  const data = [
    { name: 'Raumtyp-Optimierung', value: 35, amount: totalSavings * 0.35 },
    { name: 'Heizkreis-Effizienz', value: 25, amount: totalSavings * 0.25 },
    { name: 'Bedarfssteuerung', value: 20, amount: totalSavings * 0.20 },
    { name: 'Nachtabsenkung', value: 15, amount: totalSavings * 0.15 },
    { name: 'Spitzenlast-Reduktion', value: 5, amount: totalSavings * 0.05 },
  ];

  // Blue shades palette - from light to dark
  const COLORS = ['#A8C5E3', '#7BA3CC', '#5B8DBE', '#4A73A3', '#3D5A80'];

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 rounded-lg border border-gray-200 shadow-lg">
          <p className="text-xs font-semibold text-text-primary mb-1">
            {payload[0].name}
          </p>
          <p className="text-xs text-text-secondary">
            €{Math.round(payload[0].payload.amount).toLocaleString('de-DE')}
          </p>
          <p className="text-xs text-primary-blue font-medium">
            {payload[0].value}%
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-lg border border-gray-100 h-full overflow-hidden">
      <div className="bg-primary-blue/30 px-4 py-2.5 border-b border-primary-blue/50">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 flex items-center justify-center">
            <div className="w-3 h-3 rounded-full border-2 border-primary-blue" />
          </div>
          <h3 className="text-sm font-semibold text-text-primary">Einsparungen nach Kategorie</h3>
        </div>
      </div>
      <div className="p-4 flex items-center gap-4">
        {/* Custom Legend - Left Side */}
        <div className="flex-shrink-0 space-y-2">
          {data.map((entry, index) => (
            <div key={entry.name} className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-sm flex-shrink-0"
                style={{ backgroundColor: COLORS[index] }}
              />
              <div className="flex flex-col">
                <span className="text-xs text-text-secondary whitespace-nowrap">{entry.name}</span>
                <span className="text-xs font-semibold text-text-primary">{entry.value}%</span>
              </div>
            </div>
          ))}
        </div>

        {/* Pie Chart - Right Side */}
        <div className="flex-1">
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={65}
                outerRadius={90}
                paddingAngle={3}
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
