'use client';

import { DraftingCompass, Download, Building, Target, Upload, FileText, Table, Zap, Wind } from 'lucide-react';
import { IntermediateUploadArea } from '@/components/IntermediateUploadArea';
import { MetricCard } from '@/components/MetricCard';
import { FadeIn } from '@/components/FadeIn';
import { useAnalysis } from '@/contexts/AnalysisContext';
import { generatePowerRequirements } from '@/services/api';

export function IntermediateStepView() {
  const { setUploadedFiles, setCurrentStep, setPowerRequirementsData, setProcessing, state } = useAnalysis();
  const { roomTypeData, powerRequirementsData } = state;

  const handleFileSelect = async (file1: File, file2: File) => {
    console.log('Files selected for power analysis:', file1.name, file2.name);
    setUploadedFiles(file1, file2);
    setProcessing(true);

    try {
      console.log('Starting power requirements analysis...');
      // Call the power requirements API with both files
      // file1: Heating file
      // file2: Ventilation file
      const powerResult = await generatePowerRequirements(file1, file2);
      console.log('Power requirements analysis completed:', powerResult);
      setPowerRequirementsData(powerResult);
      
      // Navigate to step1 after successful power analysis
      console.log('Navigating to step1...');
      setCurrentStep('step1');
    } catch (error) {
      console.error('Error generating power requirements:', error);
      // Handle error - you might want to show an error message to the user
      setCurrentStep('intermediate');
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
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <FadeIn delay={200} duration={400}>
            <MetricCard
              icon={Building}
              title="Räume verarbeitet"
              value={roomTypeData?.rows?.toString() || "0"}
              delta="Klassifizierte Räume"
              deltaType="positive"
            />
          </FadeIn>
          <FadeIn delay={350} duration={400}>
            <MetricCard
              icon={Target}
              title="Verarbeitung abgeschlossen"
              value="100%"
              delta={roomTypeData?.message || "Erfolgreich"}
              deltaType="positive"
            />
          </FadeIn>
          {powerRequirementsData && (
            <>
              <FadeIn delay={500} duration={400}>
                <MetricCard
                  icon={Zap}
                  title="Leistungsanalyse"
                  value={Object.keys(powerRequirementsData.power_estimates).length.toString()}
                  delta="Räume analysiert"
                  deltaType="positive"
                />
              </FadeIn>
              <FadeIn delay={650} duration={400}>
                <MetricCard
                  icon={Wind}
                  title="Daten zusammengeführt"
                  value={powerRequirementsData.merged_rows.toString()}
                  delta={`${powerRequirementsData.merged_columns} Spalten`}
                  deltaType="positive"
                />
              </FadeIn>
            </>
          )}
        </div>

        {/* Download Buttons */}
        <FadeIn delay={500} duration={400}>
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-6">
            <button
              onClick={handleDownloadReport}
              disabled={!roomTypeData?.report_csv}
              className="inline-flex items-center gap-2 px-4 py-2 bg-primary-blue text-white rounded-lg hover:bg-primary-blue/90 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              <FileText className="w-4 h-4" />
              Report CSV herunterladen
            </button>
            <button
              onClick={handleDownloadOutput}
              disabled={!roomTypeData?.output_xlsx}
              className="inline-flex items-center gap-2 px-4 py-2 bg-success-green text-white rounded-lg hover:bg-success-green/90 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              <Table className="w-4 h-4" />
              Klassifizierte Excel-Datei herunterladen
            </button>
          </div>
        </FadeIn>

        {/* Power Requirements Summary */}
        {powerRequirementsData && (
          <FadeIn delay={700} duration={500}>
            <div className="bg-white rounded-lg p-6 border border-gray-100 mb-6">
              <h2 className="text-lg font-semibold text-text-primary mb-4 text-center">
                Leistungsanalyse Ergebnisse
              </h2>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <h3 className="font-medium text-text-primary">Durchschnittliche Heizleistung</h3>
                  <div className="text-2xl font-bold text-primary-blue">
                    {Math.round(
                      Object.values(powerRequirementsData.power_estimates)
                        .reduce((sum, room) => sum + room.heating_W_per_m2, 0) / 
                      Object.keys(powerRequirementsData.power_estimates).length
                    )} W/m²
                  </div>
                </div>
                <div className="space-y-2">
                  <h3 className="font-medium text-text-primary">Durchschnittliche Lüftung</h3>
                  <div className="text-2xl font-bold text-success-green">
                    {Math.round(
                      Object.values(powerRequirementsData.power_estimates)
                        .reduce((sum, room) => sum + room.ventilation_m3_per_h, 0) / 
                      Object.keys(powerRequirementsData.power_estimates).length
                    )} m³/h
                  </div>
                </div>
              </div>
              <div className="mt-4 text-sm text-text-secondary text-center">
                {powerRequirementsData.message}
              </div>
            </div>
          </FadeIn>
        )}

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
              <button 
                onClick={() => setCurrentStep('home')}
                className="flex items-start gap-2 p-2 rounded-lg hover:bg-white/50 transition-colors text-left"
                disabled={!roomTypeData}
              >
                <div className="w-6 h-6 bg-success-green rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-xs text-white font-bold">✓</span>
                </div>
                <div>
                  <p className="text-xs font-semibold text-text-primary">Raumtyp-Optimierung</p>
                  <p className="text-xs text-text-secondary">
                    {roomTypeData ? `${roomTypeData.rows} Räume zugeordnet` : "Abgeschlossen"}
                  </p>
                </div>
              </button>
              <button 
                onClick={() => setCurrentStep('intermediate')}
                className="flex items-start gap-2 p-2 rounded-lg hover:bg-white/50 transition-colors text-left"
                disabled={!powerRequirementsData}
              >
                <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
                  powerRequirementsData 
                    ? 'bg-success-green' 
                    : 'bg-primary-blue'
                }`}>
                  <span className={`text-xs font-bold ${
                    powerRequirementsData ? 'text-white' : 'text-white'
                  }`}>
                    {powerRequirementsData ? '✓' : '2'}
                  </span>
                </div>
                <div>
                  <p className="text-xs font-semibold text-text-primary">Leistungsanalyse</p>
                  <p className="text-xs text-text-secondary">
                    {powerRequirementsData 
                      ? `${Object.keys(powerRequirementsData.power_estimates).length} Räume analysiert`
                      : "Zusätzliche Dateien hochladen"
                    }
                  </p>
                </div>
              </button>
              <div className="flex items-start gap-2 p-2 rounded-lg opacity-50">
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
