'use client';

import { Building, Brain, LucideIcon, ArrowDown, ArrowUp } from 'lucide-react';

interface MetricItem {
  label: string;
  value: string | number;
  unit?: string;
}

interface ComparisonCardsProps {
  standardScenario: {
    title?: string;
    icon?: LucideIcon;
    metrics: MetricItem[];
  };
  optimizedScenario: {
    title?: string;
    icon?: LucideIcon;
    metrics: MetricItem[];
  };
  deltas?: {
    label: string;
    value: string;
    isImprovement: boolean;
  }[];
}

export function ComparisonCards({
  standardScenario,
  optimizedScenario,
  deltas,
}: ComparisonCardsProps) {
  const StandardIcon = standardScenario.icon || Building;
  const OptimizedIcon = optimizedScenario.icon || Brain;

  return (
    <div className="grid md:grid-cols-2 gap-4">
      {/* Standard Scenario */}
      <div className="bg-white rounded-lg overflow-hidden border border-gray-100">
        <div className="bg-warning-amber/30 px-4 py-2.5 border-b border-warning-amber/50">
          <div className="flex items-center gap-2">
            <StandardIcon className="w-4 h-4 text-text-primary" />
            <h3 className="text-sm font-semibold text-text-primary">
              {standardScenario.title || 'Standard-Szenario'}
            </h3>
          </div>
        </div>
        <div className="p-4 space-y-2">
          {standardScenario.metrics.map((metric, index) => (
            <div key={index} className="flex items-center justify-between">
              <span className="text-xs font-medium text-text-secondary">
                {metric.label}
              </span>
              <span className="text-sm font-semibold text-text-primary">
                {metric.value}
                {metric.unit && (
                  <span className="text-xs font-normal text-text-secondary ml-1">
                    {metric.unit}
                  </span>
                )}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* AI-Optimized Scenario */}
      <div className="bg-white rounded-lg overflow-hidden border border-gray-100">
        <div className="bg-success-green/30 px-4 py-2.5 border-b border-success-green/50">
          <div className="flex items-center gap-2">
            <OptimizedIcon className="w-4 h-4 text-text-primary" />
            <h3 className="text-sm font-semibold text-text-primary">
              {optimizedScenario.title || 'KI-Optimiertes Szenario'}
            </h3>
          </div>
        </div>
        <div className="p-4 space-y-2">
          {optimizedScenario.metrics.map((metric, index) => (
            <div
              key={index}
              className="flex items-center justify-between bg-success-green/5 -mx-1 px-1.5 py-0.5 rounded"
            >
              <span className="text-xs font-medium text-text-secondary">
                {metric.label}
              </span>
              <div className="flex items-center gap-1.5">
                <span className="text-sm font-semibold text-text-primary">
                  {metric.value}
                  {metric.unit && (
                    <span className="text-xs font-normal text-text-secondary ml-1">
                      {metric.unit}
                    </span>
                  )}
                </span>
                {deltas && deltas[index] && (
                  <span
                    className={`text-xs font-medium flex items-center gap-0.5 ${
                      deltas[index].isImprovement
                        ? 'text-success-green'
                        : 'text-error-red'
                    }`}
                  >
                    {deltas[index].isImprovement ? (
                      <ArrowDown className="w-3 h-3" />
                    ) : (
                      <ArrowUp className="w-3 h-3" />
                    )}
                    {deltas[index].value}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
