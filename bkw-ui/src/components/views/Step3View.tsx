'use client';

import { ProgressStepper, defaultSteps } from '@/components/ProgressStepper';
import { MetricCard } from '@/components/MetricCard';
import { FadeIn } from '@/components/FadeIn';
import { UploadArea } from '@/components/UploadArea';
import { FileText, TrendingUp, CheckCircle2 } from 'lucide-react';
import { useAnalysis } from '@/contexts/AnalysisContext';
import { useEffect } from 'react';

export function Step3View() {
  const { state, setUploadedFiles, setCurrentStep, markStep3Visited, markReportComplete } = useAnalysis();

  // Auto-advance to report only on first visit
  useEffect(() => {
    if (!state.step3Visited) {
      // Mark as visited immediately
      markStep3Visited();

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
    active: index === 2,
    completed: index < 2,
    path:
      index === 0 && state.step1Completed
        ? ('step1' as const)
        : index === 1 && state.step2Completed
        ? ('step2' as const)
        : index === 2 && state.step3Completed
        ? ('step3' as const)
        : index === 3 && state.reportCompleted
        ? ('report' as const)
        : undefined,
  }));

  const handleFileSelect = (file1: File, file2: File) => {
    setUploadedFiles(file1, file2);
    // Start automatic analysis flow
    setTimeout(() => {
      setCurrentStep('processing');
    }, 500);
  };

  return (
    <main className="min-h-screen pt-[56px] bg-background">
      <ProgressStepper steps={steps} />

      <div className="max-w-6xl mx-auto px-6 py-4">
        {/* Header */}
        <FadeIn delay={0} duration={400}>
          <div className="text-center mb-4">
            <div className="inline-flex items-center justify-center w-12 h-12 bg-success-green/20 rounded-full mb-2">
              <FileText className="w-6 h-6 text-success-green" />
            </div>
            <h1 className="text-2xl font-bold text-text-primary mb-1.5">
              Vergleichsanalyse Abgeschlossen
            </h1>
            <p className="text-sm text-text-secondary">
              Ihre Daten wurden erfolgreich verglichen und zusätzliche Optimierungen identifiziert
            </p>
          </div>
        </FadeIn>

        {/* Metrics Grid */}
        <div className="grid md:grid-cols-3 gap-4 mb-5">
          <FadeIn delay={200} duration={400}>
            <MetricCard
              icon={FileText}
              title="Vergleichsergebnisse"
              value="15"
              delta="neue Erkenntnisse"
              deltaType="positive"
            />
          </FadeIn>
          <FadeIn delay={350} duration={400}>
            <MetricCard
              icon={TrendingUp}
              title="Zusätzliche Optimierungen"
              value="8"
              delta="+12% Verbesserung"
              deltaType="positive"
            />
          </FadeIn>
          <FadeIn delay={500} duration={400}>
            <MetricCard
              icon={CheckCircle2}
              title="Zusätzliche Einsparungen"
              value="3,200 €"
              delta="pro Jahr"
              deltaType="positive"
            />
          </FadeIn>
        </div>

        {/* Upload Section for Additional Analysis */}
        <FadeIn delay={700} duration={500}>
          <div className="bg-white rounded-lg p-6 border border-gray-100 mb-5">
            <h2 className="text-lg font-semibold text-text-primary mb-4 text-center">
              Starten Sie eine weitere Analyse
            </h2>
            <p className="text-sm text-text-secondary mb-6 text-center">
              Laden Sie weitere Dateien hoch für eine neue KI-gestützte Prognose
            </p>
            
            {/* Upload Area */}
            <div className="max-w-2xl mx-auto">
              <UploadArea onFileSelect={handleFileSelect} />
            </div>
          </div>
        </FadeIn>

        {/* Summary of Previous Steps */}
        <FadeIn delay={900} duration={500}>
          <div className="bg-primary-blue-light/10 rounded-lg p-5 border border-primary-blue-light">
            <h3 className="text-base font-semibold text-text-primary mb-3">
              Bereits abgeschlossene Analysen
            </h3>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-success-green mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-xs font-semibold text-text-primary">Raumtyp-Optimierung</p>
                  <p className="text-xs text-text-secondary">47 von 52 Räumen optimiert</p>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-success-green mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-xs font-semibold text-text-primary">Energieverbrauch-Prognose</p>
                  <p className="text-xs text-text-secondary">18% Reduktion erreicht</p>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-success-green mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-xs font-semibold text-text-primary">Vergleichsanalyse</p>
                  <p className="text-xs text-text-secondary">8 zusätzliche Optimierungen</p>
                </div>
              </div>
            </div>
          </div>
        </FadeIn>
      </div>
    </main>
  );
}
