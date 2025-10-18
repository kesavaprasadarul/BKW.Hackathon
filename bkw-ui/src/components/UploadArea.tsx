'use client';

import { Upload, FileUp, X } from 'lucide-react';
import { useState, useRef, DragEvent, ChangeEvent } from 'react';

interface UploadAreaProps {
  onFileSelect: (file: File) => void;
  acceptedFormats?: string[];
  maxSizeMB?: number;
}

export function UploadArea({
  onFileSelect,
  acceptedFormats = ['.xlsx', '.xls'],
  maxSizeMB = 10,
}: UploadAreaProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): boolean => {
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

  const handleFile = (file: File) => {
    if (validateFile(file)) {
      setSelectedFile(file);
      onFileSelect(file);
    }
  };

  const handleDragEnter = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFileInput = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleRemove = () => {
    setSelectedFile(null);
    setError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <input
        ref={fileInputRef}
        type="file"
        accept={acceptedFormats.join(',')}
        onChange={handleFileInput}
        className="hidden"
      />

      {!selectedFile ? (
        <div
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={handleClick}
          className={`
            border-2 border-dashed rounded-xl p-8 text-center
            transition-all duration-200 cursor-pointer
            ${
              isDragging
                ? 'border-primary-blue bg-primary-blue-light/20'
                : 'border-primary-blue hover:bg-blue-50/30'
            }
          `}
        >
          <Upload className="w-10 h-10 mx-auto text-primary-blue mb-2.5" />
          <p className="text-base font-medium text-text-primary mb-1.5">
            Leistungsermittlung hochladen
          </p>
          <p className="text-xs text-text-secondary">
            Ziehen Sie Ihre Excel-Datei hierher oder klicken Sie zum Auswählen
          </p>
          <p className="text-xs text-text-secondary mt-1">
            {acceptedFormats.join(', ')} · Max. {maxSizeMB}MB
          </p>
        </div>
      ) : (
        <div className="border-2 border-primary-blue rounded-xl p-5 bg-primary-blue-light/10">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="p-2 bg-primary-blue rounded-lg">
                <FileUp className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-sm font-medium text-text-primary">{selectedFile.name}</p>
                <p className="text-xs text-text-secondary">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            <button
              onClick={handleRemove}
              className="p-1.5 hover:bg-gray-200 rounded-lg transition-colors"
              aria-label="Datei entfernen"
            >
              <X className="w-4 h-4 text-text-secondary" />
            </button>
          </div>
        </div>
      )}

      {error && (
        <div className="mt-3 p-3 bg-error-red/10 border border-error-red/30 rounded-lg">
          <p className="text-xs text-red-900">{error}</p>
        </div>
      )}
    </div>
  );
}
