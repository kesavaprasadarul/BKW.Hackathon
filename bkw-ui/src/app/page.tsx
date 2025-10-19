'use client';

import { useAnalysis } from '@/contexts/AnalysisContext';
import { Navigation } from '@/components/Navigation';
import { HomeView } from '@/components/views/HomeView';
import { ProcessingView } from '@/components/views/ProcessingView';
import { Step1View } from '@/components/views/Step1View';
import { Step2ProcessingView } from '@/components/views/Step2ProcessingView';
import { Step2View } from '@/components/views/Step2View';
import { ReportView } from '@/components/views/ReportView';

export default function Home() {
  const { state } = useAnalysis();

  const renderView = () => {
    switch (state.currentStep) {
      case 'home':
        return <HomeView />;
      case 'processing':
        return <ProcessingView />;
      case 'step1':
        return <Step1View />;
      case 'step2-processing':
        return <Step2ProcessingView />;
      case 'step2':
        return <Step2View />;
      case 'report':
        return <ReportView />;
      default:
        return <HomeView />;
    }
  };

  return (
    <>
      <Navigation />
      {renderView()}
    </>
  );
}
