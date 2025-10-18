'use client';

import { ProgressStepper, defaultSteps } from '@/components/ProgressStepper';
import { LoadingState } from '@/components/LoadingState';
import { Brain } from 'lucide-react';
import { useAnalysis } from '@/contexts/AnalysisContext';
import { useEffect, useState } from 'react';

export function ProcessingView() {
  const { setCurrentStep, markStep1Complete } = useAnalysis();
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Simulate processing with progress
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 10;
      });
    }, 150);

    // Auto-advance to step 1 after processing
    const timer = setTimeout(() => {
      setCurrentStep('step1');
      markStep1Complete();
    }, 2000);

    return () => {
      clearInterval(interval);
      clearTimeout(timer);
    };
  }, [setCurrentStep, markStep1Complete]);

  // Steps for processing view
  const steps = defaultSteps.map((step, index) => ({
    ...step,
    active: index === 0,
    completed: false,
    path: undefined, // No navigation during processing
  }));

  return (
    <main className="min-h-screen pt-[56px] bg-background flex flex-col">
      <ProgressStepper steps={steps} />

      <div className="flex-1 flex items-center justify-center">
        <div className="max-w-2xl mx-auto px-6">
          <LoadingState
            icon={Brain}
            title="Analyse läuft..."
            message="Optimiere Raumtypen..."
            progress={progress}
          />
        </div>
      </div>
    </main>
  );
}
