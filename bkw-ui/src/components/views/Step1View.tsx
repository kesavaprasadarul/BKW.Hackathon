'use client';

import { ProgressStepper, defaultSteps } from '@/components/ProgressStepper';
import { MetricCard } from '@/components/MetricCard';
import { FadeIn } from '@/components/FadeIn';
import { Building, CheckCircle2, TrendingUp } from 'lucide-react';
import { useAnalysis } from '@/contexts/AnalysisContext';
import { useEffect, useRef } from 'react';

export function Step1View() {
  const { state, setCurrentStep, markStep1Visited } = useAnalysis();

  // Auto-advance to step 2 processing only on first visit
  useEffect(() => {
    if (!state.step1Visited) {
      // Mark as visited immediately
      markStep1Visited();

      // Auto-advance after 2 seconds
      const timer = setTimeout(() => {
        setCurrentStep('step2-processing');
      }, 2000);

      return () => clearTimeout(timer);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Steps - all clickable if completed
  const steps = defaultSteps.map((step, index) => ({
    ...step,
    active: index === 0,
    completed: index < 0,
    path:
      index === 0 && state.step1Completed
        ? ('step1' as const)
        : index === 1 && (state.step2Completed || state.reportCompleted)
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
              <CheckCircle2 className="w-6 h-6 text-success-green" />
            </div>
            <h1 className="text-2xl font-bold text-text-primary mb-1.5">
              Raumtyp-Optimierung Abgeschlossen
            </h1>
            <p className="text-sm text-text-secondary">
              Ihre Raumtypen wurden erfolgreich analysiert und optimiert
            </p>
          </div>
        </FadeIn>

        {/* Metrics Grid */}
        <div className="grid md:grid-cols-3 gap-4 mb-5">
          <FadeIn delay={200} duration={400}>
            <MetricCard
              icon={Building}
              title="Optimierte Räume"
              value="47"
              delta="von 52 Räumen"
              deltaType="positive"
            />
          </FadeIn>
          <FadeIn delay={350} duration={400}>
            <MetricCard
              icon={TrendingUp}
              title="Verbesserungsrate"
              value="90%"
              delta="+12% gegenüber Standard"
              deltaType="positive"
            />
          </FadeIn>
          <FadeIn delay={500} duration={400}>
            <MetricCard
              icon={CheckCircle2}
              title="Genauigkeit"
              value="98%"
              delta="KI-Konfidenz"
              deltaType="positive"
            />
          </FadeIn>
        </div>

        {/* Details and Key Changes - Side by Side */}
        <FadeIn delay={700} duration={500}>
          <div className="grid md:grid-cols-2 gap-4">
            {/* Details Section */}
            <div className="bg-white rounded-lg p-5 border border-gray-100">
            <h2 className="text-base font-semibold text-text-primary mb-3">
              Optimierungsdetails
            </h2>
            <div className="space-y-2">
              <div className="flex items-center justify-between py-1.5 border-b border-gray-100">
                <span className="text-xs text-text-secondary">
                  Ursprüngliche Raumtypen
                </span>
                <span className="text-sm font-semibold text-text-primary">52</span>
              </div>
              <div className="flex items-center justify-between py-1.5 border-b border-gray-100">
                <span className="text-xs text-text-secondary">Optimierte Raumtypen</span>
                <span className="text-sm font-semibold text-text-primary">47</span>
              </div>
              <div className="flex items-center justify-between py-1.5 border-b border-gray-100">
                <span className="text-xs text-text-secondary">Ø Raumgröße</span>
                <span className="text-sm font-semibold text-text-primary">24.5 m²</span>
              </div>
              <div className="flex items-center justify-between py-1.5">
                <span className="text-xs text-text-secondary">Gesamtfläche</span>
                <span className="text-sm font-semibold text-text-primary">1,274 m²</span>
              </div>
            </div>
          </div>

          {/* Key Changes */}
          <div className="bg-primary-blue-light/10 rounded-lg p-5 border border-primary-blue-light">
            <h3 className="text-base font-semibold text-text-primary mb-3">
              Wichtigste Änderungen
            </h3>
            <ul className="space-y-2">
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-success-green mt-0.5 flex-shrink-0" />
                <span className="text-xs text-text-secondary">
                  5 Räume von "Büro Standard" auf "Büro Optimiert" umkategorisiert
                </span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-success-green mt-0.5 flex-shrink-0" />
                <span className="text-xs text-text-secondary">
                  Konferenzräume für effizientere Heizungsnutzung angepasst
                </span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-success-green mt-0.5 flex-shrink-0" />
                <span className="text-xs text-text-secondary">
                  Optimale Raumgruppierung für gemeinsame Heizkreise identifiziert
                </span>
              </li>
            </ul>
          </div>
        </div>
          </FadeIn>
      </div>
    </main>
  );
}
