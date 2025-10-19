// API calls to backend endpoints

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface RoomTypeClassificationResponse {
  processed_file: string;
  report_csv: string;
  output_xlsx: string;
  rows: number;
  message: string;
}

interface Step1Response {
  optimizedRooms: number;
  totalRooms: number;
  improvementRate: number;
  confidence: number;
}

interface Step2Response {
  energyConsumption: number;
  reductionPercentage: number;
  annualSavings: number;
}

interface Step3Response {
  comparisonResults: number;
  newOptimizations: number;
  additionalSavings: number;
}

export async function classifyRoomTypes(excelFile: File, mappingFile: File): Promise<RoomTypeClassificationResponse> {
  const formData = new FormData();
  formData.append('excel_file', excelFile);
  formData.append('mapping_csv', mappingFile);

  const response = await fetch(`${API_BASE_URL}/roomtypes/classify`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}

export async function fetchStep1Analysis(file1: File, file2: File): Promise<Step1Response> {
  // Simulate API call with 1 second delay
  await new Promise(resolve => setTimeout(resolve, 1000));

  // TODO: Replace with actual POST to your Vercel API endpoint
  // const formData = new FormData();
  // formData.append('file1', file1); // Leistungsermittlung_KLT_HZG
  // formData.append('file2', file2); // Leistungsermittlung_RLT
  // const response = await fetch('/api/analyze/step1', {
  //   method: 'POST',
  //   body: formData,
  // });
  // return response.json();

  // Simulated response data
  return {
    optimizedRooms: 47,
    totalRooms: 52,
    improvementRate: 90,
    confidence: 98,
  };
}

export async function fetchStep2Analysis(): Promise<Step2Response> {
  // Simulate API call with 1 second delay
  await new Promise(resolve => setTimeout(resolve, 1000));

  // TODO: Replace with actual POST to your Vercel API endpoint
  // const response = await fetch('/api/analyze/step2', {
  //   method: 'POST',
  // });
  // return response.json();

  // Simulated response data
  return {
    energyConsumption: 45,
    reductionPercentage: 18,
    annualSavings: 7800,
  };
}

export async function fetchStep3Analysis(): Promise<Step3Response> {
  // Simulate API call with 1 second delay
  await new Promise(resolve => setTimeout(resolve, 1000));

  // TODO: Replace with actual POST to your Vercel API endpoint
  // const response = await fetch('/api/analyze/step3', {
  //   method: 'POST',
  // });
  // return response.json();

  // Simulated response data
  return {
    comparisonResults: 15,
    newOptimizations: 8,
    additionalSavings: 3200,
  };
}
