'use client';

import { ProgressStepper, defaultSteps } from '@/components/ProgressStepper';
import { LoadingState } from '@/components/LoadingState';
import { FileText } from 'lucide-react';
import { useAnalysis } from '@/contexts/AnalysisContext';
import { fetchStep3Analysis } from '@/services/api';
import { useEffect } from 'react';

export function Step3ProcessingView() {
  const { state, setCurrentStep, markStep3Complete, setProcessing, setStep3Data } = useAnalysis();

  useEffect(() => {
    let isMounted = true;

    // API call for step 3
    const apiCall = async () => {
      setProcessing(true);

      try {
        // Call API
        const data = await fetchStep3Analysis();

        if (isMounted) {
          // Store the data globally
          setStep3Data(data);

          // Mark step 3 as complete
          markStep3Complete();

          // Navigate to step 3 results
          setCurrentStep('step3');
        }
      } catch (error) {
        console.error('Step 3 API error:', error);
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
    active: index === 2,
    completed: index < 2,
    path: state.step1Completed && index === 0 ? ('step1' as const) : 
          state.step2Completed && index === 1 ? ('step2' as const) : undefined,
  }));

  return (
    <main className="min-h-screen pt-[56px] bg-background flex flex-col">
      <ProgressStepper steps={steps} />

      <div className="flex-1 flex items-center justify-center">
        <div className="max-w-2xl mx-auto px-6">
          <LoadingState
            icon={FileText}
            title="Neue Analyse wird durchgeführt..."
            message="Verarbeite neue Daten und führe Vergleichsanalyse durch..."
          />
        </div>
      </div>
    </main>
  );
}
