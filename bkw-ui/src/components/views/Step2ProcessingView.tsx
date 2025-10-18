'use client';

import { ProgressStepper, defaultSteps } from '@/components/ProgressStepper';
import { LoadingState } from '@/components/LoadingState';
import { Zap } from 'lucide-react';
import { useAnalysis } from '@/contexts/AnalysisContext';
import { useEffect, useState } from 'react';

export function Step2ProcessingView() {
  const { state, setCurrentStep, markStep2Complete } = useAnalysis();
  const [progress, setProgress] = useState(33);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 66) {
          clearInterval(interval);
          return 66;
        }
        return prev + 5;
      });
    }, 100);

    const timer = setTimeout(() => {
      setCurrentStep('step2');
      markStep2Complete();
    }, 2000);

    return () => {
      clearInterval(interval);
      clearTimeout(timer);
    };
  }, [setCurrentStep, markStep2Complete]);

  const steps = defaultSteps.map((step, index) => ({
    ...step,
    active: index === 1,
    completed: index === 0,
    path: state.step1Completed && index === 0 ? 'step1' : undefined,
  }));

  return (
    <main className="min-h-screen pt-[56px] bg-background flex flex-col">
      <ProgressStepper steps={steps} />

      <div className="flex-1 flex items-center justify-center">
        <div className="max-w-2xl mx-auto px-6">
          <LoadingState
            icon={Zap}
            title="Energieverbrauch wird berechnet..."
            message="Analysiere Heizleistung und prognostiziere Verbrauch..."
            progress={progress}
          />
        </div>
      </div>
    </main>
  );
}
