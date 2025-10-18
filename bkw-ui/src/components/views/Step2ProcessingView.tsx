'use client';

import { ProgressStepper, defaultSteps } from '@/components/ProgressStepper';
import { LoadingState } from '@/components/LoadingState';
import { Zap } from 'lucide-react';
import { useAnalysis } from '@/contexts/AnalysisContext';
import { fetchStep2Analysis } from '@/services/api';
import { useEffect } from 'react';

export function Step2ProcessingView() {
  const { state, setCurrentStep, markStep2Complete, setProcessing, setStep2Data } = useAnalysis();

  useEffect(() => {
    let isMounted = true;

    // API call for step 2
    const apiCall = async () => {
      setProcessing(true);

      try {
        // Call API
        const data = await fetchStep2Analysis();

        if (isMounted) {
          // Store the data globally
          setStep2Data(data);

          // Mark step 2 as complete
          markStep2Complete();

          // Navigate to step 2 results
          setCurrentStep('step2');
        }
      } catch (error) {
        console.error('Step 2 API error:', error);
      } finally {
        if (isMounted) {
          setProcessing(false);
        }
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
    path: state.step1Completed && index === 0 ? ('step1' as const) : undefined,
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
