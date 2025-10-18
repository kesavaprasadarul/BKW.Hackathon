'use client';

import { LucideIcon } from 'lucide-react';
import { FadeIn } from './FadeIn';

interface LoadingStateProps {
  icon?: LucideIcon;
  title: string;
  message?: string;
  progress?: number;
}

export function LoadingState({
  icon: Icon,
  title,
  message,
  progress,
}: LoadingStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      {/* Animated Ring with Icon */}
      <FadeIn delay={0} duration={400}>
        <div className="relative mb-4">
          <div className="w-20 h-20 rounded-full border-4 border-gray-200" />
          <div className="absolute inset-0 w-20 h-20 rounded-full border-4 border-primary-blue border-t-transparent animate-spin" />
          {Icon && (
            <div className="absolute inset-0 flex items-center justify-center">
              <Icon className="w-10 h-10 text-primary-blue" />
            </div>
          )}
        </div>
      </FadeIn>

      <FadeIn delay={200} duration={400}>
        <h2 className="text-xl font-semibold text-text-primary mb-1 text-center">
          {title}
        </h2>
      </FadeIn>

      {message && (
        <FadeIn delay={400} duration={400}>
          <p className="text-sm text-text-secondary text-center animate-pulse">{message}</p>
        </FadeIn>
      )}

      {progress !== undefined && (
        <FadeIn delay={600} duration={400}>
          <div className="w-full max-w-2xl mt-4">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-medium text-primary-blue">
                {progress}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-1.5">
              <div
                className="bg-primary-blue h-1.5 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        </FadeIn>
      )}
    </div>
  );
}
