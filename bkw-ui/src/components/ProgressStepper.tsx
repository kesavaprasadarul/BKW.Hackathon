'use client';

import { CheckCircle2, Building, Zap, FileText, LucideIcon } from 'lucide-react';
import { useAnalysis } from '@/contexts/AnalysisContext';
import type { AnalysisStep } from '@/contexts/AnalysisContext';

export interface Step {
  id: number;
  name: string;
  icon: LucideIcon;
  completed: boolean;
  active: boolean;
  path?: AnalysisStep; // Navigation path as state value
}

interface ProgressStepperProps {
  steps: Step[];
}

export function ProgressStepper({ steps }: ProgressStepperProps) {
  const { state, setCurrentStep } = useAnalysis();

  const handleStepClick = (step: Step) => {
    // Block navigation if currently processing
    if (state.isProcessing) {
      return;
    }

    // Allow navigation if step has a path (completed, active, or accessible)
    if (step.path) {
      setCurrentStep(step.path);
    }
  };

  return (
    <div className="w-full bg-white border-b border-gray-200 sticky top-[56px] z-40">
      <div className="max-w-2xl mx-auto py-4 px-6">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => {
            const Icon = step.icon;
            const isClickable = !!step.path; // Clickable if it has a path

            return (
              <div key={step.id} className={`flex items-center ${step.id === 3 ? '' : 'flex-1'}`}>
                {/* Step Circle */}
                <div className="flex flex-col items-center">
                  <button
                    onClick={() => handleStepClick(step)}
                    disabled={!isClickable || state.isProcessing}
                    className={`
                      w-9 h-9 rounded-full flex items-center justify-center transition-all duration-200
                      ${
                        step.completed
                          ? 'bg-success-green'
                          : step.active
                          ? 'bg-primary-blue'
                          : isClickable
                          ? 'border-2 border-primary-blue bg-white'
                          : 'border-2 border-gray-300 bg-white'
                      }
                      ${isClickable && !state.isProcessing ? 'cursor-pointer hover:scale-110' : 'cursor-not-allowed opacity-60'}
                    `}
                    aria-label={`Go to ${step.name}`}
                  >
                    {step.completed ? (
                      <CheckCircle2 className="w-5 h-5 text-white" />
                    ) : (
                      <Icon
                        className={`w-4 h-4 ${
                          step.active ? 'text-white' : isClickable ? 'text-primary-blue' : 'text-gray-400'
                        }`}
                      />
                    )}
                  </button>
                  <p
                    className={`text-xs font-medium mt-1.5 text-center max-w-[100px] ${
                      step.active || step.completed || isClickable
                        ? 'text-text-primary'
                        : 'text-text-secondary'
                    }`}
                  >
                    {step.name}
                  </p>
                </div>

                {/* Connector Line */}
                {index < steps.length - 1 && (
                  <div
                    className={`flex-1 border-t-2 mx-3 transition-colors duration-200 ${
                      step.completed ? 'border-success-green' : 'border-gray-300'
                    }`}
                  />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// Default steps configuration
export const defaultSteps: Step[] = [
  {
    id: 1,
    name: 'Raumtyp Optimierung',
    icon: Building,
    completed: false,
    active: false,
  },
  {
    id: 2,
    name: 'Energieverbrauch Prognose',
    icon: Zap,
    completed: false,
    active: false,
  },
  {
    id: 3,
    name: 'Finaler Bericht',
    icon: FileText,
    completed: false,
    active: false,
  },
];
