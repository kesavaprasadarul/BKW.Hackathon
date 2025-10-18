'use client';

import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  icon: LucideIcon;
  title: string;
  value: string;
  delta?: string;
  deltaType?: 'positive' | 'negative' | 'neutral';
  className?: string;
}

export function MetricCard({
  icon: Icon,
  title,
  value,
  delta,
  deltaType = 'neutral',
  className = '',
}: MetricCardProps) {
  const deltaColor =
    deltaType === 'positive'
      ? 'text-success-green'
      : deltaType === 'negative'
      ? 'text-error-red'
      : 'text-text-secondary';

  return (
    <div
      className={`bg-white rounded-lg p-4 border border-gray-100 hover:shadow-lg transition-shadow ${className}`}
    >
      <div className="flex items-start gap-2.5">
        <div className="p-1.5 bg-blue-100 rounded-lg">
          <Icon className="w-4 h-4 text-primary-blue" />
        </div>
        <div className="flex-1">
          <p className="text-xs font-medium text-text-secondary mb-0.5">{title}</p>
          <p className="text-2xl font-bold text-text-primary">{value}</p>
          {delta && <p className={`text-xs mt-1 ${deltaColor}`}>{delta}</p>}
        </div>
      </div>
    </div>
  );
}
