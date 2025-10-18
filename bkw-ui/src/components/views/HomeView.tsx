'use client';

import { DraftingCompass } from 'lucide-react';
import { UploadArea } from '@/components/UploadArea';
import { useAnalysis } from '@/contexts/AnalysisContext';

export function HomeView() {
  const { setUploadedFiles, setCurrentStep } = useAnalysis();

  const handleFileSelect = (file1: File, file2: File) => {
    setUploadedFiles(file1, file2);
    // Start automatic analysis flow
    setTimeout(() => {
      setCurrentStep('processing');
    }, 500);
  };

  return (
    <main className="min-h-screen pt-[56px] flex items-center justify-center bg-gradient-to-b from-primary-blue-light/10 to-background">
      <div className="max-w-5xl mx-auto px-6 py-6 text-center">
        {/* Hero Icon */}
        <div className="mb-4 flex justify-center">
          <div className="p-2.5 bg-primary-blue-light/20 rounded-xl">
            <DraftingCompass className="w-10 h-10 text-primary-blue" />
          </div>
        </div>

        {/* Headline */}
        <h1 className="text-3xl md:text-4xl font-bold text-text-primary mb-3">
          Transformieren Sie Ihre Ingenieurdaten in{' '}
          <span className="text-primary-blue">prädiktive Erkenntnisse</span>
        </h1>

        {/* Subtitle */}
        <p className="text-base text-text-secondary mb-6 max-w-2xl mx-auto">
          Laden Sie Ihre Dateien hoch für KI-gestützte Prognosen zu
          Heizleistung, Energieverbrauch und Kostenoptimierung
        </p>

        {/* Upload Area */}
        <UploadArea onFileSelect={handleFileSelect} />

        {/* How it works */}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <h2 className="text-lg font-semibold text-text-primary mb-4">
            Wie es funktioniert
          </h2>
          <div className="grid md:grid-cols-3 gap-6 text-left">
            <div>
              <div className="w-9 h-9 bg-primary-blue text-white rounded-lg flex items-center justify-center font-bold text-base mb-2.5">
                1
              </div>
              <h3 className="font-semibold text-sm text-text-primary mb-1">
                Datei hochladen
              </h3>
              <p className="text-xs text-text-secondary">
                Laden Sie Ihre Excel-Leistungsermittlung hoch
              </p>
            </div>
            <div>
              <div className="w-9 h-9 bg-primary-blue text-white rounded-lg flex items-center justify-center font-bold text-base mb-2.5">
                2
              </div>
              <h3 className="font-semibold text-sm text-text-primary mb-1">
                KI-Analyse
              </h3>
              <p className="text-xs text-text-secondary">
                Unsere KI optimiert Raumtypen und prognostiziert den Energieverbrauch
              </p>
            </div>
            <div>
              <div className="w-9 h-9 bg-primary-blue text-white rounded-lg flex items-center justify-center font-bold text-base mb-2.5">
                3
              </div>
              <h3 className="font-semibold text-sm text-text-primary mb-1">
                Bericht erhalten
              </h3>
              <p className="text-xs text-text-secondary">
                Erhalten Sie detaillierte Einblicke und Einsparungsempfehlungen
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
