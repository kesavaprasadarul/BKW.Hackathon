'use client';

import { X, Flame, Wind } from 'lucide-react';
import { useState, useRef, DragEvent, ChangeEvent } from 'react';

interface UploadAreaProps {
  onFileSelect: (file1: File, file2: File) => void;
  acceptedFormats?: string[];
  maxSizeMB?: number;
}

export function UploadArea({
  onFileSelect,
  acceptedFormats = ['.xlsx', '.xls'],
  maxSizeMB = 10,
}: UploadAreaProps) {
  const [isDragging1, setIsDragging1] = useState(false);
  const [isDragging2, setIsDragging2] = useState(false);
  const [selectedFile1, setSelectedFile1] = useState<File | null>(null);
  const [selectedFile2, setSelectedFile2] = useState<File | null>(null);
  const [error1, setError1] = useState<string>('');
  const [error2, setError2] = useState<string>('');
  const fileInputRef1 = useRef<HTMLInputElement>(null);
  const fileInputRef2 = useRef<HTMLInputElement>(null);

  const validateFile = (file: File, fileNumber: 1 | 2): boolean => {
    const setError = fileNumber === 1 ? setError1 : setError2;

    // Check file size
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      setError(`Datei ist zu groß. Maximum: ${maxSizeMB}MB`);
      return false;
    }

    // Check file extension
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!acceptedFormats.includes(fileExtension)) {
      setError(`Ungültiges Dateiformat. Erlaubt: ${acceptedFormats.join(', ')}`);
      return false;
    }

    setError('');
    return true;
  };

  const handleFile1 = (file: File) => {
    if (validateFile(file, 1)) {
      setSelectedFile1(file);
      // Trigger callback if both files are selected
      if (selectedFile2) {
        onFileSelect(file, selectedFile2);
      }
    }
  };

  const handleFile2 = (file: File) => {
    if (validateFile(file, 2)) {
      setSelectedFile2(file);
      // Trigger callback if both files are selected
      if (selectedFile1) {
        onFileSelect(selectedFile1, file);
      }
    }
  };

  // Handlers for File 1
  const handleDragEnter1 = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging1(true);
  };

  const handleDragLeave1 = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging1(false);
  };

  const handleDragOver1 = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop1 = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging1(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFile1(files[0]);
    }
  };

  const handleFileInput1 = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile1(files[0]);
    }
  };

  const handleClick1 = () => {
    fileInputRef1.current?.click();
  };

  const handleRemove1 = () => {
    setSelectedFile1(null);
    setError1('');
    if (fileInputRef1.current) {
      fileInputRef1.current.value = '';
    }
  };

  // Handlers for File 2
  const handleDragEnter2 = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging2(true);
  };

  const handleDragLeave2 = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging2(false);
  };

  const handleDragOver2 = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop2 = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging2(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFile2(files[0]);
    }
  };

  const handleFileInput2 = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile2(files[0]);
    }
  };

  const handleClick2 = () => {
    fileInputRef2.current?.click();
  };

  const handleRemove2 = () => {
    setSelectedFile2(null);
    setError2('');
    if (fileInputRef2.current) {
      fileInputRef2.current.value = '';
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      <h2 className="text-lg font-semibold text-text-primary mb-4 text-center">
        Excel hochladen von Leistungsermittlung
      </h2>

      <input
        ref={fileInputRef1}
        type="file"
        accept={acceptedFormats.join(',')}
        onChange={handleFileInput1}
        className="hidden"
      />
      <input
        ref={fileInputRef2}
        type="file"
        accept={acceptedFormats.join(',')}
        onChange={handleFileInput2}
        className="hidden"
      />

      <div className="grid md:grid-cols-2 gap-4">
        {/* File 1 Upload Area - Heating/Cooling */}
        <div>
          <h3 className="text-sm font-semibold text-text-primary mb-2 flex items-center gap-2">
            Kälte und Heizung (KLT/HZG)
          </h3>
          {!selectedFile1 ? (
            <div
              onDragEnter={handleDragEnter1}
              onDragLeave={handleDragLeave1}
              onDragOver={handleDragOver1}
              onDrop={handleDrop1}
              onClick={handleClick1}
              className={`
                border-2 border-dashed rounded-xl p-6 text-center
                transition-all duration-200 cursor-pointer
                ${
                  isDragging1
                    ? 'border-primary-blue bg-primary-blue-light/20'
                    : 'border-primary-blue hover:bg-blue-50/30'
                }
              `}
            >
              <Flame className="w-8 h-8 mx-auto text-primary-blue mb-2" />
              <p className="text-sm font-medium text-text-primary mb-1">
                KLT/HZG hochladen
              </p>
              <p className="text-xs text-text-secondary">
                Ziehen Sie Ihre Datei hierher
              </p>
              <p className="text-xs text-text-secondary mt-1">
                {acceptedFormats.join(', ')} · Max. {maxSizeMB}MB
              </p>
            </div>
          ) : (
            <div className="border-2 border-primary-blue rounded-xl p-4 bg-primary-blue-light/10">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 bg-primary-blue rounded-lg">
                    <Flame className="w-4 h-4 text-white" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-medium text-text-primary truncate">{selectedFile1.name}</p>
                    <p className="text-xs text-text-secondary">
                      {(selectedFile1.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleRemove1}
                  className="p-1 hover:bg-gray-200 rounded-lg transition-colors flex-shrink-0"
                  aria-label="Datei entfernen"
                >
                  <X className="w-4 h-4 text-text-secondary" />
                </button>
              </div>
            </div>
          )}
          {error1 && (
            <div className="mt-2 p-2 bg-error-red/10 border border-error-red/30 rounded-lg">
              <p className="text-xs text-red-900">{error1}</p>
            </div>
          )}
        </div>

        {/* File 2 Upload Area - Ventilation */}
        <div>
          <h3 className="text-sm font-semibold text-text-primary mb-2 flex items-center gap-2">
            Raumlüftung (RLT)
          </h3>
          {!selectedFile2 ? (
            <div
              onDragEnter={handleDragEnter2}
              onDragLeave={handleDragLeave2}
              onDragOver={handleDragOver2}
              onDrop={handleDrop2}
              onClick={handleClick2}
              className={`
                border-2 border-dashed rounded-xl p-6 text-center
                transition-all duration-200 cursor-pointer
                ${
                  isDragging2
                    ? 'border-primary-blue bg-primary-blue-light/20'
                    : 'border-primary-blue hover:bg-blue-50/30'
                }
              `}
            >
              <Wind className="w-8 h-8 mx-auto text-primary-blue mb-2" />
              <p className="text-sm font-medium text-text-primary mb-1">
                RLT hochladen
              </p>
              <p className="text-xs text-text-secondary">
                Ziehen Sie Ihre Datei hierher
              </p>
              <p className="text-xs text-text-secondary mt-1">
                {acceptedFormats.join(', ')} · Max. {maxSizeMB}MB
              </p>
            </div>
          ) : (
            <div className="border-2 border-primary-blue rounded-xl p-4 bg-primary-blue-light/10">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 bg-primary-blue rounded-lg">
                    <Wind className="w-4 h-4 text-white" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-medium text-text-primary truncate">{selectedFile2.name}</p>
                    <p className="text-xs text-text-secondary">
                      {(selectedFile2.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleRemove2}
                  className="p-1 hover:bg-gray-200 rounded-lg transition-colors flex-shrink-0"
                  aria-label="Datei entfernen"
                >
                  <X className="w-4 h-4 text-text-secondary" />
                </button>
              </div>
            </div>
          )}
          {error2 && (
            <div className="mt-2 p-2 bg-error-red/10 border border-error-red/30 rounded-lg">
              <p className="text-xs text-red-900">{error2}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
