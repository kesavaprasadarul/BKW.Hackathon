'use client';

import { DraftingCompass, Download, Building, Target, FileText, Table, ArrowRight } from 'lucide-react';
import { HomeUploadArea } from '@/components/HomeUploadArea';
import { MetricCard } from '@/components/MetricCard';
import { FadeIn } from '@/components/FadeIn';
import { useAnalysis } from '@/contexts/AnalysisContext';
import { classifyRoomTypes } from '@/services/api';

export function HomeView() {
  const { setUploadedFiles, setCurrentStep, setRoomTypeData, setProcessing, state } = useAnalysis();
  const { roomTypeData } = state;

  const handleFileSelect = async (file1: File, file2: File) => {
    setUploadedFiles(file1, file2);
    setProcessing(true);
    setCurrentStep('processing');

    try {
      // Call the room type classification API with both files
      // file1: Excel file with room data
      // file2: Mapping CSV file
      const roomTypeResult = await classifyRoomTypes(file1, file2);
      setRoomTypeData(roomTypeResult);
      
      // Proceed to the next step after successful classification
      setCurrentStep('intermediate');
    } catch (error) {
      console.error('Error classifying room types:', error);
      setCurrentStep('home');
    } finally {
      setProcessing(false);
    }
  };

  const downloadFile = async (filePath: string, filename: string) => {
    try {
      const response = await fetch(`http://localhost:8000/download?file=${encodeURIComponent(filePath)}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      } else {
        console.error('Failed to download file:', response.statusText);
      }
    } catch (error) {
      console.error('Error downloading file:', error);
    }
  };

  const handleDownloadReport = () => {
    if (roomTypeData?.report_csv) {
      downloadFile(roomTypeData.report_csv, 'room-type-report.csv');
    }
  };

  const handleDownloadOutput = () => {
    if (roomTypeData?.output_xlsx) {
      downloadFile(roomTypeData.output_xlsx, 'classified-rooms.xlsx');
    }
  };

  // Show results if room type classification is completed
  if (roomTypeData) {
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
                Raumtyp-Optimierung Abgeschlossen
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
                title="Räume verarbeitet"
                value={roomTypeData.rows.toString()}
                delta="Klassifizierte Räume"
                deltaType="positive"
              />
            </FadeIn>
            <FadeIn delay={350} duration={400}>
              <MetricCard
                icon={Target}
                title="Verarbeitung abgeschlossen"
                value="100%"
                delta={roomTypeData.message}
                deltaType="positive"
              />
            </FadeIn>
          </div>

          {/* Download Buttons */}
          <FadeIn delay={500} duration={400}>
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-6">
              <button
                onClick={handleDownloadReport}
                className="inline-flex items-center gap-2 px-4 py-2 bg-primary-blue text-white rounded-lg hover:bg-primary-blue/90 transition-colors"
              >
                <FileText className="w-4 h-4" />
                Report CSV herunterladen
              </button>
              <button
                onClick={handleDownloadOutput}
                className="inline-flex items-center gap-2 px-4 py-2 bg-success-green text-white rounded-lg hover:bg-success-green/90 transition-colors"
              >
                <Table className="w-4 h-4" />
                Klassifizierte Excel-Datei herunterladen
              </button>
            </div>
          </FadeIn>

          {/* Continue Button */}
          <FadeIn delay={700} duration={400}>
            <div className="flex justify-center mb-6">
              <button
                onClick={() => setCurrentStep('intermediate')}
                className="inline-flex items-center gap-2 px-6 py-3 bg-primary-blue text-white rounded-lg hover:bg-primary-blue/90 transition-colors"
              >
                Weiter zur Leistungsanalyse
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </FadeIn>
        </div>
      </main>
    );
  }

  // Show upload interface if no results yet
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
        <HomeUploadArea onFileSelect={handleFileSelect} />

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
                Laden Sie Ihre Excel-Planungstabellen hoch
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
                Unsere KI bestimmt automatisch die Raumtypen und prognostiziert den Energieverbrauch
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
