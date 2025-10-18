'use client';

import { ProgressStepper, defaultSteps } from '@/components/ProgressStepper';
import { LoadingState } from '@/components/LoadingState';
import { Brain } from 'lucide-react';
import { useAnalysis } from '@/contexts/AnalysisContext';
import { fetchStep1Analysis } from '@/services/api';
import { useEffect } from 'react';

export function ProcessingView() {
  const { state, setCurrentStep, markStep1Complete, setProcessing, setStep1Data } = useAnalysis();

  useEffect(() => {
    let isMounted = true;

    // API call for step 1
    const apiCall = async () => {
      setProcessing(true);

      try {
        // Call API with both uploaded files
        const data = await fetchStep1Analysis(state.uploadedFiles.file1!, state.uploadedFiles.file2!);

        if (isMounted) {
          // Store the data globally
          setStep1Data(data);

          // Mark step 1 as complete
          markStep1Complete();

          // Navigate to step 1 results
          setCurrentStep('step1');
        }
      } catch (error) {
        console.error('Step 1 API error:', error);
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
