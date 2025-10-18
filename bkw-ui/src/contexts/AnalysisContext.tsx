'use client';

import { createContext, useContext, useState, ReactNode } from 'react';

export type AnalysisStep = 'home' | 'processing' | 'step1' | 'step2-processing' | 'step2' | 'report';

export interface Step1Data {
  optimizedRooms: number;
  totalRooms: number;
  improvementRate: number;
  confidence: number;
}

export interface Step2Data {
  energyConsumption: number;
  reductionPercentage: number;
  annualSavings: number;
}

interface AnalysisState {
  currentStep: AnalysisStep;
  uploadedFiles: {
    file1: File | null;
    file2: File | null;
  };
  step1Completed: boolean;
  step2Completed: boolean;
  reportCompleted: boolean;
  step1Visited: boolean;
  step2Visited: boolean;
  isProcessing: boolean;
  step1Data: Step1Data | null;
  step2Data: Step2Data | null;
}

interface AnalysisContextType {
  state: AnalysisState;
  setCurrentStep: (step: AnalysisStep) => void;
  setUploadedFiles: (file1: File, file2: File) => void;
  markStep1Complete: () => void;
  markStep2Complete: () => void;
  markReportComplete: () => void;
  markStep1Visited: () => void;
  markStep2Visited: () => void;
  setProcessing: (isProcessing: boolean) => void;
  setStep1Data: (data: Step1Data) => void;
  setStep2Data: (data: Step2Data) => void;
  resetAnalysis: () => void;
}

const AnalysisContext = createContext<AnalysisContextType | undefined>(undefined);

const initialState: AnalysisState = {
  currentStep: 'home',
  uploadedFiles: {
    file1: null,
    file2: null,
  },
  step1Completed: false,
  step2Completed: false,
  reportCompleted: false,
  step1Visited: false,
  step2Visited: false,
  isProcessing: false,
  step1Data: null,
  step2Data: null,
};

export function AnalysisProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AnalysisState>(initialState);

  const setCurrentStep = (step: AnalysisStep) => {
    setState(prev => ({ ...prev, currentStep: step }));
  };

  const setUploadedFiles = (file1: File, file2: File) => {
    setState(prev => ({ ...prev, uploadedFiles: { file1, file2 } }));
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

  const markStep1Visited = () => {
    setState(prev => ({ ...prev, step1Visited: true }));
  };

  const markStep2Visited = () => {
    setState(prev => ({ ...prev, step2Visited: true }));
  };

  const setProcessing = (isProcessing: boolean) => {
    setState(prev => ({ ...prev, isProcessing }));
  };

  const setStep1Data = (data: Step1Data) => {
    setState(prev => ({ ...prev, step1Data: data }));
  };

  const setStep2Data = (data: Step2Data) => {
    setState(prev => ({ ...prev, step2Data: data }));
  };

  const resetAnalysis = () => {
    setState(initialState);
  };

  return (
    <AnalysisContext.Provider
      value={{
        state,
        setCurrentStep,
        setUploadedFiles,
        markStep1Complete,
        markStep2Complete,
        markReportComplete,
        markStep1Visited,
        markStep2Visited,
        setProcessing,
        setStep1Data,
        setStep2Data,
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
