'use client';

import { ProgressStepper, defaultSteps } from '@/components/ProgressStepper';
import { MetricCard } from '@/components/MetricCard';
import { ComparisonCards } from '@/components/ComparisonCards';
import { CostChart } from '@/components/CostChart';
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

        {/* Key Metrics Grid */}
        <div className="grid md:grid-cols-4 gap-3 mb-4">
          <FadeIn delay={200} duration={400}>
            <MetricCard
              icon={Zap}
              title="Energieeinsparung"
              value="18%"
              delta="25,680 kWh/Jahr"
              deltaType="positive"
            />
          </FadeIn>
          <FadeIn delay={300} duration={400}>
            <MetricCard
              icon={Euro}
              title="Kosteneinsparung"
              value={`€${totalSavings.toLocaleString('de-DE')}`}
              delta={`${savingsPercentage}% pro Jahr`}
              deltaType="positive"
            />
          </FadeIn>
          <FadeIn delay={400} duration={400}>
            <MetricCard
              icon={TrendingDown}
              title="Heizleistung"
              value="57 kW"
              delta="↓ 12% optimiert"
              deltaType="positive"
            />
          </FadeIn>
          <FadeIn delay={500} duration={400}>
            <MetricCard
              icon={Leaf}
              title="CO₂-Reduktion"
              value="4.8 t"
              delta="pro Jahr"
              deltaType="positive"
            />
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

        {/* Cost Projection Chart - Full Width */}
        <FadeIn delay={900} duration={500}>
          <div className="mb-4">
            <CostChart data={costData} title="Monatliche Kosteneinsparungen im Jahresverlauf" />
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

        {/* Tabs for Additional Information */}
        <FadeIn delay={1500} duration={500}>
          <div className="bg-white rounded-lg border border-gray-100 overflow-hidden">
          {/* Tab Headers */}
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveTab('overview')}
              className={`flex-1 py-2 px-4 text-xs font-semibold transition-colors ${
                activeTab === 'overview'
                  ? 'bg-primary-blue text-white'
                  : 'text-text-secondary hover:bg-gray-50'
              }`}
            >
              Übersicht
            </button>
            <button
              onClick={() => setActiveTab('details')}
              className={`flex-1 py-2 px-4 text-xs font-semibold transition-colors ${
                activeTab === 'details'
                  ? 'bg-primary-blue text-white'
                  : 'text-text-secondary hover:bg-gray-50'
              }`}
            >
              Details
            </button>
            <button
              onClick={() => setActiveTab('recommendations')}
              className={`flex-1 py-2 px-4 text-xs font-semibold transition-colors ${
                activeTab === 'recommendations'
                  ? 'bg-primary-blue text-white'
                  : 'text-text-secondary hover:bg-gray-50'
              }`}
            >
              Empfehlungen
            </button>
          </div>

          {/* Tab Content */}
          <div className="p-4">
            {activeTab === 'overview' && (
              <div className="space-y-2">
                <p className="text-xs text-text-secondary">
                  Die KI-gestützte Analyse hat erhebliches Optimierungspotenzial identifiziert.
                  Jährlich bis zu €7,800 Einsparung durch intelligente Raumtyp-Anpassungen und
                  Energieverbrauchsprognosen. 47 Raumtypen (von 52) mit Ø 45 W/m² (-18%).
                </p>
              </div>
            )}

            {activeTab === 'details' && (
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <h4 className="text-xs font-semibold text-text-primary mb-1.5">Gebäudedaten</h4>
                  <ul className="space-y-1 text-xs text-text-secondary">
                    <li>• Fläche: 1,274 m²</li>
                    <li>• Räume: 47</li>
                    <li>• Ø Größe: 24.5 m²</li>
                    <li>• Baujahr: 2010</li>
                  </ul>
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-text-primary mb-1.5">Heizsystem</h4>
                  <ul className="space-y-1 text-xs text-text-secondary">
                    <li>• Typ: Niedertemperatur</li>
                    <li>• Vorlauf: 55°C</li>
                    <li>• Heizkreise: 6</li>
                    <li>• Regelung: Zeit + Nutzung</li>
                  </ul>
                </div>
              </div>
            )}

            {activeTab === 'recommendations' && (
              <div className="space-y-2.5">
                <div className="flex gap-2.5">
                  <div className="w-6 h-6 bg-primary-blue rounded-lg flex items-center justify-center flex-shrink-0">
                    <span className="text-white font-bold text-xs">1</span>
                  </div>
                  <div>
                    <h4 className="text-xs font-semibold text-text-primary">Raumtypen aktualisieren</h4>
                    <p className="text-xs text-text-secondary">Implementieren Sie die Raumtyp-Änderungen</p>
                  </div>
                </div>
                <div className="flex gap-2.5">
                  <div className="w-6 h-6 bg-primary-blue rounded-lg flex items-center justify-center flex-shrink-0">
                    <span className="text-white font-bold text-xs">2</span>
                  </div>
                  <div>
                    <h4 className="text-xs font-semibold text-text-primary">Heizkreise neu gruppieren</h4>
                    <p className="text-xs text-text-secondary">Optimierte Konfiguration reduziert Wärmeverluste</p>
                  </div>
                </div>
                <div className="flex gap-2.5">
                  <div className="w-6 h-6 bg-primary-blue rounded-lg flex items-center justify-center flex-shrink-0">
                    <span className="text-white font-bold text-xs">3</span>
                  </div>
                  <div>
                    <h4 className="text-xs font-semibold text-text-primary">Intelligente Steuerung</h4>
                    <p className="text-xs text-text-secondary">Nutzungsbasierte Regelungstechnik installieren</p>
                  </div>
                </div>
                <div className="flex gap-2.5">
                  <div className="w-6 h-6 bg-primary-blue rounded-lg flex items-center justify-center flex-shrink-0">
                    <span className="text-white font-bold text-xs">4</span>
                  </div>
                  <div>
                    <h4 className="text-xs font-semibold text-text-primary">Monitoring einrichten</h4>
                    <p className="text-xs text-text-secondary">Kontinuierliches Energiemonitoring etablieren</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
          </FadeIn>
      </div>
    </main>
  );
}
