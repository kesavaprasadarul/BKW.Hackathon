'use client';

import { createContext, useContext, useState, ReactNode } from 'react';

export type AnalysisStep = 'home' | 'processing' | 'step1' | 'step2-processing' | 'step2' | 'report';

interface AnalysisState {
  currentStep: AnalysisStep;
  uploadedFile: File | null;
  step1Completed: boolean;
  step2Completed: boolean;
  reportCompleted: boolean;
}

interface AnalysisContextType {
  state: AnalysisState;
  setCurrentStep: (step: AnalysisStep) => void;
  setUploadedFile: (file: File) => void;
  markStep1Complete: () => void;
  markStep2Complete: () => void;
  markReportComplete: () => void;
  resetAnalysis: () => void;
}

const AnalysisContext = createContext<AnalysisContextType | undefined>(undefined);

const initialState: AnalysisState = {
  currentStep: 'home',
  uploadedFile: null,
  step1Completed: false,
  step2Completed: false,
  reportCompleted: false,
};

export function AnalysisProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AnalysisState>(initialState);

  const setCurrentStep = (step: AnalysisStep) => {
    setState(prev => ({ ...prev, currentStep: step }));
  };

  const setUploadedFile = (file: File) => {
    setState(prev => ({ ...prev, uploadedFile: file }));
  };

  const markStep1Complete = () => {
    setState(prev => ({ ...prev, step1Completed: true }));
  };

  const markStep2Complete = () => {
    setState(prev => ({ ...prev, step2Completed: true }));
  };

  const markReportComplete = () => {
    setState(prev => ({ ...prev, reportCompleted: true }));
  };

  const resetAnalysis = () => {
    setState(initialState);
  };

  return (
    <AnalysisContext.Provider
      value={{
        state,
        setCurrentStep,
        setUploadedFile,
        markStep1Complete,
        markStep2Complete,
        markReportComplete,
        resetAnalysis,
      }}
    >
      {children}
    </AnalysisContext.Provider>
  );
}

export function useAnalysis() {
  const context = useContext(AnalysisContext);
  if (context === undefined) {
    throw new Error('useAnalysis must be used within an AnalysisProvider');
  }
  return context;
}
