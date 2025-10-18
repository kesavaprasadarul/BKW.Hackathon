'use client';

import { ProgressStepper, defaultSteps } from '@/components/ProgressStepper';
import { ComparisonCards } from '@/components/ComparisonCards';
import { CombinedCostSavingsChart } from '@/components/CombinedCostSavingsChart';
import { SavingsBreakdownChart } from '@/components/SavingsBreakdownChart';
import { FadeIn } from '@/components/FadeIn';
import {
  Download,
  Zap,
  Euro,
  TrendingDown,
  Leaf,
  Building,
  Brain,
} from 'lucide-react';
import { useAnalysis } from '@/contexts/AnalysisContext';
import { useState } from 'react';

export function ReportView() {
  const { state } = useAnalysis();
  const [activeTab, setActiveTab] = useState<'overview' | 'details' | 'recommendations'>('overview');

  // Update steps - all completed and clickable
  const steps = defaultSteps.map((step, index) => ({
    ...step,
    active: index === 2,
    completed: index < 2,
    path:
      index === 0 && state.step1Completed
        ? ('step1' as const)
        : index === 1 && state.step2Completed
        ? ('step2' as const)
        : index === 2 && state.reportCompleted
        ? ('report' as const)
        : undefined,
  }));

  // Sample data for the cost chart
  const costData = [
    { month: 'Jan', standard: 4200, optimized: 3100 },
    { month: 'Feb', standard: 3800, optimized: 2900 },
    { month: 'Mär', standard: 3200, optimized: 2500 },
    { month: 'Apr', standard: 2400, optimized: 1900 },
    { month: 'Mai', standard: 1800, optimized: 1400 },
    { month: 'Jun', standard: 1200, optimized: 900 },
    { month: 'Jul', standard: 800, optimized: 600 },
    { month: 'Aug', standard: 900, optimized: 700 },
    { month: 'Sep', standard: 1600, optimized: 1200 },
    { month: 'Okt', standard: 2800, optimized: 2100 },
    { month: 'Nov', standard: 3600, optimized: 2700 },
    { month: 'Dez', standard: 4100, optimized: 3000 },
  ];

  // Calculate total savings
  const totalStandard = costData.reduce((sum, item) => sum + item.standard, 0);
  const totalOptimized = costData.reduce((sum, item) => sum + item.optimized, 0);
  const totalSavings = totalStandard - totalOptimized;
  const savingsPercentage = ((totalSavings / totalStandard) * 100).toFixed(1);

  const handleExport = () => {
    alert('Export-Funktion würde hier den Bericht als PDF exportieren');
  };

  return (
    <main className="min-h-screen pt-[56px] bg-background">
      <ProgressStepper steps={steps} />

      <div className="max-w-7xl mx-auto px-6 py-3">
        {/* Header with Export Button */}
        <FadeIn delay={0} duration={400}>
          <div className="flex items-center justify-between mb-3">
          <div>
            <h1 className="text-2xl font-bold text-text-primary mb-1">
              Analyse Abgeschlossen
            </h1>
            <p className="text-xs text-text-secondary">
              {new Date().toLocaleDateString('de-DE')}
            </p>
          </div>
          <button
            onClick={handleExport}
            className="bg-primary-blue hover:bg-primary-blue-dark text-white px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-1.5 transition-colors"
          >
            <Download className="w-4 h-4" />
            Exportieren
          </button>
        </div>
        </FadeIn>

        {/* Key Metrics and Breakdown */}
        <div className="grid md:grid-cols-2 gap-4 mb-4">
          {/* Metrics - Left Container (50%) */}
          <FadeIn delay={200} duration={400}>
            <div className="bg-white rounded-lg border border-gray-100 h-full overflow-hidden">
              <div className="bg-primary-blue/30 px-4 py-2.5 border-b border-primary-blue/50">
                <div className="flex items-center gap-2">
                  <TrendingDown className="w-4 h-4 text-primary-blue" />
                  <h3 className="text-sm font-semibold text-text-primary">Kernergebnisse</h3>
                </div>
              </div>
              <div className="p-4">
                <div className="flex flex-col gap-4  pt-7">
                  {/* Row 1 */}
                  <div className="grid grid-cols-2 gap-x-4 w-full">
                    <div className="flex items-start gap-2.5">
                      <div className="p-2.5 bg-blue-100 rounded-lg flex-shrink-0">
                        <Zap className="w-5 h-5 text-primary-blue" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium text-text-secondary mb-1">Energieeinsparung</p>
                        <p className="text-xl font-bold text-text-primary">18%</p>
                        <p className="text-xs text-success-green mt-0.5">↓ 10.8 kWh/m²</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-2.5">
                      <div className="p-2.5 bg-green-100 rounded-lg flex-shrink-0">
                        <Euro className="w-5 h-5 text-success-green" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium text-text-secondary mb-1">Kosteneinsparung</p>
                        <p className="text-xl font-bold text-text-primary">
                          €{totalSavings.toLocaleString('de-DE')}
                        </p>
                        <p className="text-xs text-success-green mt-0.5">pro Jahr</p>
                      </div>
                    </div>
                  </div>

                  {/* Row 2 */}
                  <div className="grid grid-cols-2 gap-x-4 gap-y-5 pt-7 w-full">
                    <div className="flex items-start gap-2.5">
                      <div className="p-2.5 bg-orange-100 rounded-lg flex-shrink-0">
                        <TrendingDown className="w-5 h-5 text-warning-amber" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium text-text-secondary">Heizleistung</p>
                        <p className="text-xl font-bold text-text-primary">57 kW</p>
                        <p className="text-xs text-success-green mt-0.5">↓ 12 kW optimiert</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-2.5">
                      <div className="p-2.5 bg-green-100 rounded-lg flex-shrink-0">
                        <Leaf className="w-5 h-5 text-success-green" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium text-text-secondary">CO₂-Reduktion</p>
                        <p className="text-xl font-bold text-text-primary">4.8 t</p>
                        <p className="text-xs text-success-green mt-0.5">pro Jahr</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </FadeIn>

          {/* Pie Chart - Right Container (50%) */}
          <FadeIn delay={400} duration={400}>
            <SavingsBreakdownChart totalSavings={totalSavings} />
          </FadeIn>
        </div>

        {/* Comparison Section */}
        <FadeIn delay={650} duration={500}>
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-text-primary mb-3">
              Effizienzvergleich
            </h2>
            <ComparisonCards
            standardScenario={{
              icon: Building,
              title: 'Standard-Szenario',
              metrics: [
                { label: 'Raumtypen', value: '52' },
                { label: 'Energieverbrauch', value: '55', unit: 'W/m²' },
                { label: 'Heizleistung', value: '65', unit: 'kW' },
                { label: 'Jahreskosten', value: '€30,300' },
              ],
            }}
            optimizedScenario={{
              icon: Brain,
              title: 'KI-Optimiertes Szenario',
              metrics: [
                { label: 'Raumtypen', value: '47' },
                { label: 'Energieverbrauch', value: '45', unit: 'W/m²' },
                { label: 'Heizleistung', value: '57', unit: 'kW' },
                { label: 'Jahreskosten', value: '€22,500' },
              ],
            }}
            deltas={[
              { label: 'Raumtypen', value: '5', isImprovement: true },
              { label: 'Energieverbrauch', value: '18%', isImprovement: true },
              { label: 'Heizleistung', value: '12%', isImprovement: true },
              { label: 'Jahreskosten', value: '26%', isImprovement: true },
            ]}
          />
        </div>
          </FadeIn>

        {/* Combined Cost and Cumulative Savings Chart */}
        <FadeIn delay={900} duration={500}>
          <div className="mb-4">
            <CombinedCostSavingsChart data={costData} title="Monatliche Kosten und Kumulierte Einsparungen" />
          </div>
        </FadeIn>

        {/* Savings Summary - Below Chart */}
        <FadeIn delay={1100} duration={500}>
          <div className="grid md:grid-cols-2 gap-4 mb-4">
          <div className="bg-success-green/10 rounded-lg p-4 border border-success-green/30">
            <p className="text-xs font-medium text-text-secondary mb-0.5">
              Geschätzte Gesamteinsparung
            </p>
            <p className="text-2xl font-bold text-success-green">
              €{totalSavings.toLocaleString('de-DE')}
            </p>
            <p className="text-xs text-text-secondary">
              {savingsPercentage}% Reduktion gegenüber Standard-Szenario
            </p>
          </div>
          <div className="bg-primary-blue-light/10 rounded-lg p-4 border border-primary-blue-light">
            <p className="text-xs font-medium text-text-secondary mb-0.5">
              ROI-Zeitraum
            </p>
            <p className="text-2xl font-bold text-text-primary">2.4 Jahre</p>
            <p className="text-xs text-text-secondary">
              Bei durchschnittlichen Investitionskosten
            </p>
          </div>
        </div>
          </FadeIn>

        {/* Parameter Difference Table */}
        <FadeIn delay={1300} duration={500}>
          <div className="bg-white rounded-lg p-4 border border-gray-100 mb-4">
          <h2 className="text-sm font-semibold text-text-primary mb-3">
            Detaillierte Parameteränderungen
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-1.5 px-2 text-xs font-medium text-text-secondary">
                    Parameter
                  </th>
                  <th className="text-right py-1.5 px-2 text-xs font-medium text-text-secondary">
                    Standard
                  </th>
                  <th className="text-right py-1.5 px-2 text-xs font-medium text-text-secondary">
                    Optimiert
                  </th>
                  <th className="text-right py-1.5 px-2 text-xs font-medium text-text-secondary">
                    Änderung
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-1.5 px-2 text-xs font-medium text-text-primary">Raumtypen</td>
                  <td className="py-1.5 px-2 text-right text-xs text-text-primary">52</td>
                  <td className="py-1.5 px-2 text-right text-xs text-text-primary">47</td>
                  <td className="py-1.5 px-2 text-right text-xs text-success-green font-semibold">↓ 5 (9.6%)</td>
                </tr>
                <tr className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-1.5 px-2 text-xs font-medium text-text-primary">W/m²</td>
                  <td className="py-1.5 px-2 text-right text-xs text-text-primary">55</td>
                  <td className="py-1.5 px-2 text-right text-xs text-text-primary">45</td>
                  <td className="py-1.5 px-2 text-right text-xs text-success-green font-semibold">↓ 10 (18%)</td>
                </tr>
                <tr className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-1.5 px-2 text-xs font-medium text-text-primary">Heizleistung kW</td>
                  <td className="py-1.5 px-2 text-right text-xs text-text-primary">65</td>
                  <td className="py-1.5 px-2 text-right text-xs text-text-primary">57</td>
                  <td className="py-1.5 px-2 text-right text-xs text-success-green font-semibold">↓ 8 (12%)</td>
                </tr>
                <tr className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-1.5 px-2 text-xs font-medium text-text-primary">kWh/Jahr</td>
                  <td className="py-1.5 px-2 text-right text-xs text-text-primary">169,500</td>
                  <td className="py-1.5 px-2 text-right text-xs text-text-primary">143,820</td>
                  <td className="py-1.5 px-2 text-right text-xs text-success-green font-semibold">↓ 25,680</td>
                </tr>
                <tr className="hover:bg-gray-50">
                  <td className="py-1.5 px-2 text-xs font-medium text-text-primary">€/Jahr</td>
                  <td className="py-1.5 px-2 text-right text-xs text-text-primary">30,300</td>
                  <td className="py-1.5 px-2 text-right text-xs text-text-primary">22,500</td>
                  <td className="py-1.5 px-2 text-right text-xs text-success-green font-semibold">↓ 7,800</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </FadeIn>
      </div>
    </main>
  );
}
