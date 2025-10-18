'use client';

import { ProgressStepper, defaultSteps } from '@/components/ProgressStepper';
import { MetricCard } from '@/components/MetricCard';
import { FadeIn } from '@/components/FadeIn';
import { Zap, Flame, TrendingDown } from 'lucide-react';
import { useAnalysis } from '@/contexts/AnalysisContext';
import { useEffect, useRef } from 'react';

export function Step2View() {
  const { state, setCurrentStep, markReportComplete, markStep2Visited } = useAnalysis();

  // Auto-advance to report only on first visit
  useEffect(() => {
    if (!state.step2Visited) {
      // Mark as visited immediately
      markStep2Visited();

      // Auto-advance after 2 seconds
      const timer = setTimeout(() => {
        markReportComplete();
        setCurrentStep('report');
      }, 2000);

      return () => clearTimeout(timer);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const steps = defaultSteps.map((step, index) => ({
    ...step,
    active: index === 1,
    completed: index === 0,
    path:
      index === 0 && state.step1Completed
        ? ('step1' as const)
        : index === 1 && state.step2Completed
        ? ('step2' as const)
        : index === 2 && state.reportCompleted
        ? ('report' as const)
        : undefined,
  }));

  return (
    <main className="min-h-screen pt-[56px] bg-background">
        <ProgressStepper steps={steps} />

        <div className="max-w-6xl mx-auto px-6 py-4">
          {/* Header */}
          <FadeIn delay={0} duration={400}>
            <div className="text-center mb-4">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-success-green/20 rounded-full mb-2">
                <Zap className="w-6 h-6 text-success-green" />
              </div>
              <h1 className="text-2xl font-bold text-text-primary mb-1.5">
                Energieverbrauch-Prognose Abgeschlossen
              </h1>
              <p className="text-sm text-text-secondary">
                Ihre Energieverbrauchswerte wurden erfolgreich berechnet und optimiert
              </p>
            </div>
          </FadeIn>

          {/* Metrics Grid */}
          <div className="grid md:grid-cols-3 gap-4 mb-5">
            <FadeIn delay={200} duration={400}>
              <MetricCard
                icon={Zap}
                title="Optimierter Energieverbrauch"
                value="45 W/m²"
                delta="↓ 18% gegenüber Standard"
                deltaType="positive"
              />
            </FadeIn>
            <FadeIn delay={350} duration={400}>
              <MetricCard
                icon={Flame}
                title="Heizleistung"
                value="57 kW"
                delta="↓ 12% optimiert"
                deltaType="positive"
              />
            </FadeIn>
            <FadeIn delay={500} duration={400}>
              <MetricCard
                icon={TrendingDown}
                title="Jahresverbrauch"
                value="143,820 kWh"
                delta="↓ 25,680 kWh eingespart"
                deltaType="positive"
              />
            </FadeIn>
          </div>

          {/* Energy Breakdown and Optimization Highlights - Side by Side */}
          <FadeIn delay={700} duration={500}>
            <div className="grid md:grid-cols-2 gap-4 mb-5">
            {/* Energy Breakdown */}
            <div className="bg-white rounded-lg p-5 border border-gray-100">
              <h2 className="text-base font-semibold text-text-primary mb-3">
                Energieverteilung nach Raumtyp
              </h2>
              <div className="space-y-2.5">
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-text-secondary">Büros</span>
                    <span className="font-semibold text-text-primary">42 W/m²</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <div className="bg-primary-blue h-1.5 rounded-full" style={{ width: '70%' }} />
                  </div>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-text-secondary">Konferenzräume</span>
                    <span className="font-semibold text-text-primary">55 W/m²</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <div className="bg-accent-blue h-1.5 rounded-full" style={{ width: '85%' }} />
                  </div>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-text-secondary">Gemeinschaftsbereiche</span>
                    <span className="font-semibold text-text-primary">38 W/m²</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <div className="bg-primary-blue-light h-1.5 rounded-full" style={{ width: '60%' }} />
                  </div>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-text-secondary">Flure & Technik</span>
                    <span className="font-semibold text-text-primary">28 W/m²</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <div className="bg-success-green h-1.5 rounded-full" style={{ width: '45%' }} />
                  </div>
                </div>
              </div>
            </div>

            {/* Optimization Highlights */}
            <div className="bg-success-green/10 rounded-lg p-5 border border-success-green/30">
              <h3 className="text-base font-semibold text-text-primary mb-3">
                Optimierungshighlights
              </h3>
              <div className="space-y-2.5">
                <div className="flex items-start gap-2">
                  <div className="w-7 h-7 bg-success-green rounded-lg flex items-center justify-center flex-shrink-0">
                    <TrendingDown className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-text-primary">Reduzierte Spitzenlast</p>
                    <p className="text-xs text-text-secondary">15% niedrigere Spitzenlast</p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="w-7 h-7 bg-success-green rounded-lg flex items-center justify-center flex-shrink-0">
                    <Flame className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-text-primary">Effiziente Heizkreise</p>
                    <p className="text-xs text-text-secondary">12% weniger Wärmeverluste</p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="w-7 h-7 bg-success-green rounded-lg flex items-center justify-center flex-shrink-0">
                    <Zap className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-text-primary">Bedarfsgerechte Steuerung</p>
                    <p className="text-xs text-text-secondary">Nutzungsbasierte Anpassung</p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="w-7 h-7 bg-success-green rounded-lg flex items-center justify-center flex-shrink-0">
                    <TrendingDown className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-text-primary">Nachtabsenkung optimiert</p>
                    <p className="text-xs text-text-secondary">Zusätzlich 8% Einsparung</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
            </FadeIn>

        </div>
      </main>
  );
}
