'use client';

import { ProgressStepper, defaultSteps } from '@/components/ProgressStepper';
import { LoadingState } from '@/components/LoadingState';
import { Brain } from 'lucide-react';
import { useAnalysis } from '@/contexts/AnalysisContext';
import { useEffect } from 'react';

export function ProcessingView() {
  const { setCurrentStep, markStep1Complete, setProcessing } = useAnalysis();

  useEffect(() => {
    let isMounted = true;

    // Simulated API call for step 1
    const apiCall = async () => {
      setProcessing(true);

      // Simulate POST API call (1 second)
      await new Promise(resolve => setTimeout(resolve, 1000));

      if (isMounted) {
        // Mark step 1 as complete
        markStep1Complete();

        // Navigate to step 1 results
        setCurrentStep('step1');
        setProcessing(false);
      }
    };

    apiCall();

    return () => {
      isMounted = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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
          />
        </div>
      </div>
    </main>
  );
}
