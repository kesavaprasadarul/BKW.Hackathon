'use client';

import { ProgressStepper, defaultSteps } from '@/components/ProgressStepper';
import { LoadingState } from '@/components/LoadingState';
import { Zap } from 'lucide-react';
import { useAnalysis } from '@/contexts/AnalysisContext';
import { useEffect } from 'react';

export function Step2ProcessingView() {
  const { state, setCurrentStep, markStep2Complete, setProcessing } = useAnalysis();

  useEffect(() => {
    let isMounted = true;

    // Simulated API call for step 2
    const apiCall = async () => {
      setProcessing(true);

      // Simulate POST API call (1 second)
      await new Promise(resolve => setTimeout(resolve, 1000));

      if (isMounted) {
        // Mark step 2 as complete
        markStep2Complete();

        // Navigate to step 2 results
        setCurrentStep('step2');
        setProcessing(false);
      }
    };

    apiCall();

    return () => {
      isMounted = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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
          />
        </div>
      </div>
    </main>
  );
}
