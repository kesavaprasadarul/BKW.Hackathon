// Simulated API calls - replace with actual Vercel API endpoints

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
