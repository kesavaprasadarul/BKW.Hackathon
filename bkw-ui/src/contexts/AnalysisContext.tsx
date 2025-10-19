'use client';

import { createContext, useContext, useState, ReactNode } from 'react';

export type AnalysisStep = 'home' | 'processing' | 'intermediate' | 'step1' | 'step2-processing' | 'step2' | 'report';

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

export interface RoomTypeClassificationData {
  processed_file: string;
  report_csv: string;
  output_xlsx: string;
  rows: number;
  message: string;
}

export interface PowerEstimates {
  room_nr: string;
  room_type: number;
  heating_W_per_m2: number;
  cooling_W_per_m2: number;
  ventilation_m3_per_h: number;
  area_m2?: number;
  volume_m3?: number;
}

export interface PowerRequirementsData {
  heating_file: string;
  ventilation_file: string;
  merged_rows: number;
  merged_columns: number;
  power_estimates: Record<string, PowerEstimates>;
  performance_table: string;
  message: string;
}

export interface CostBOQItem {
  description: string;
  subgroup_kg?: string;
  subgroup_title?: string;
  quantity: number;
  unit?: string;
  material_unit_price: number;
  total_material_price: number;
  total_final_price: number;
  bki_component_title: string;
  type?: string;
}

export interface CostEstimationSummary {
  project_metrics: Record<string, number>;
  grand_total_cost: number;
  cost_factors_applied: Record<string, number>;
}

export interface CostEstimationData {
  summary: CostEstimationSummary;
  detailed_boq: CostBOQItem[];
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
  roomTypeData: RoomTypeClassificationData | null;
  powerRequirementsData: PowerRequirementsData | null;
  costEstimationData: CostEstimationData | null;
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
  setRoomTypeData: (data: RoomTypeClassificationData) => void;
  setPowerRequirementsData: (data: PowerRequirementsData) => void;
  setCostEstimationData: (data: CostEstimationData) => void;
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
  roomTypeData: null,
  powerRequirementsData: null,
  costEstimationData: null,
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

  const setRoomTypeData = (data: RoomTypeClassificationData) => {
    setState(prev => ({ ...prev, roomTypeData: data }));
  };

  const setPowerRequirementsData = (data: PowerRequirementsData) => {
    setState(prev => ({ ...prev, powerRequirementsData: data }));
  };

  const setCostEstimationData = (data: CostEstimationData) => {
    setState(prev => ({ ...prev, costEstimationData: data }));
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
        setRoomTypeData,
        setPowerRequirementsData,
        setCostEstimationData,
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
