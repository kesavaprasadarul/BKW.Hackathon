'use client';

import { DraftingCompass, Download, Building, Target, Upload } from 'lucide-react';
import { IntermediateUploadArea } from '@/components/IntermediateUploadArea';
import { MetricCard } from '@/components/MetricCard';
import { FadeIn } from '@/components/FadeIn';
import { useAnalysis } from '@/contexts/AnalysisContext';

export function IntermediateStepView() {
  const { setUploadedFiles, setCurrentStep } = useAnalysis();

  const handleFileSelect = (file1: File, file2: File) => {
    setUploadedFiles(file1, file2);
    // Navigate directly to step1 since we already have the first analysis results
    setTimeout(() => {
      setCurrentStep('step1');
    }, 500);
  };

  const handleExport = () => {
    // Create a mock intermediate file for download
    const data = {
      roomsMatched: 89,
      averageCertainty: 94.2,
      timestamp: new Date().toISOString(),
      analysisResults: {
        totalRooms: 52,
        matchedRooms: 46,
        confidence: 94.2
      }
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `intermediate-analysis-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleImport = () => {
    // Open file picker for Excel files only
    const fileInput = document.createElement('input') as HTMLInputElement;
    fileInput.type = 'file';
    fileInput.accept = '.xlsx,.xls';
    fileInput.onchange = (e) => {
      const file = fileInput.files?.[0];
      if (file) {
        console.log('Excel file selected:', file.name);
      }
    };
    fileInput.click();
  };

  return (
    <main className="min-h-screen pt-[56px] bg-background">
      <div className="max-w-6xl mx-auto px-6 py-6">
        {/* Header */}
        <FadeIn delay={0} duration={400}>
          <div className="text-center mb-6">
            <div className="inline-flex items-center justify-center w-12 h-12 bg-primary-blue-light/20 rounded-full mb-3">
              <DraftingCompass className="w-6 h-6 text-primary-blue" />
            </div>
            <h1 className="text-2xl font-bold text-text-primary mb-2">
              Erste Analyse Abgeschlossen
            </h1>
            <p className="text-sm text-text-secondary">
              Ihre Raumtypen wurden erfolgreich zugeordnet. Zur Überprüfung können Sie die Tabelle herunterladen.
            </p>
          </div>
        </FadeIn>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-2 gap-4 mb-6">
          <FadeIn delay={200} duration={400}>
            <MetricCard
              icon={Building}
              title="Räume zugeordnet"
              value="89%"
              delta="46 von 52 Räumen"
              deltaType="positive"
            />
          </FadeIn>
          <FadeIn delay={350} duration={400}>
            <MetricCard
              icon={Target}
              title="Durchschnittliche Genauigkeit"
              value="94.2%"
              delta="KI-Konfidenz"
              deltaType="positive"
            />
          </FadeIn>
        </div>

        {/* Export Button */}
        <FadeIn delay={500} duration={400}>
          <div className="flex justify-center mb-6">
            <button
              onClick={handleExport}
              className="inline-flex items-center gap-2 px-4 py-2 bg-primary-blue text-white rounded-lg hover:bg-primary-blue/90 transition-colors"
            >
              <Download className="w-4 h-4" />
              Zwischenergebnisse exportieren
            </button>
          </div>
        </FadeIn>

        {/* Import Button */}
        <FadeIn delay={500} duration={400}>
          <div className="flex justify-center mb-6">
            <button
              onClick={handleImport}
              className="inline-flex items-center gap-2 px-4 py-2 bg-primary-blue text-white rounded-lg hover:bg-primary-blue/90 transition-colors"
            >
              <Upload className="w-4 h-4" />
              Neues Zwischenergebnis importieren
            </button>
          </div>
        </FadeIn>

        {/* Upload Section */}
        <FadeIn delay={700} duration={500}>
          <div className="bg-white rounded-lg p-6 border border-gray-100 mb-6">
            <h2 className="text-lg font-semibold text-text-primary mb-4 text-center">
              Laden Sie zusätzliche Dateien hoch
            </h2>
            <p className="text-sm text-text-secondary mb-6 text-center">
              Für eine umfassende Analyse benötigen wir weitere Daten. Laden Sie Ihre
              zusätzlichen Excel-Dateien hoch für eine vollständige KI-gestützte Prognose.
            </p>
            
            {/* Upload Area */}
            <IntermediateUploadArea onFileSelect={handleFileSelect} />
          </div>
        </FadeIn>

        {/* Progress Steps */}
        <FadeIn delay={900} duration={500}>
          <div className="bg-primary-blue-light/10 rounded-lg p-5 border border-primary-blue-light">
            <h3 className="text-base font-semibold text-text-primary mb-3 text-center">
              Analysefortschritt
            </h3>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="flex items-start gap-2">
                <div className="w-6 h-6 bg-success-green rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-xs text-white font-bold">✓</span>
                </div>
                <div>
                  <p className="text-xs font-semibold text-text-primary">Erste Analyse</p>
                  <p className="text-xs text-text-secondary">89% Räume zugeordnet</p>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <div className="w-6 h-6 bg-primary-blue rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-xs text-white font-bold">2</span>
                </div>
                <div>
                  <p className="text-xs font-semibold text-text-primary">Zusätzliche Dateien</p>
                  <p className="text-xs text-text-secondary">Für vollständige Analyse</p>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <div className="w-6 h-6 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-xs text-gray-600 font-bold">3</span>
                </div>
                <div>
                  <p className="text-xs font-semibold text-text-primary">Detaillierte Analyse</p>
                  <p className="text-xs text-text-secondary">Umfassende Einblicke</p>
                </div>
              </div>
            </div>
          </div>
        </FadeIn>
      </div>
    </main>
  );
}
