/**
 * API client for communicating with the EveWatch Python FastAPI backend.
 */

import type {
  SimulationRequest,
  SimulationResponse,
  EncryptRequest,
  EncryptResponse,
  DecryptRequest,
  DecryptResponse,
  ExperimentDataset,
  SystemHealth,
} from '../types/quantum';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const fullUrl = `${API_BASE}${url}`;
  const response = await fetch(fullUrl, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    let errorDetail = response.statusText;
    try {
      const errorJson = await response.json();
      if (errorJson.detail) {
        errorDetail = typeof errorJson.detail === 'string' 
          ? errorJson.detail 
          : JSON.stringify(errorJson.detail);
      }
    } catch {
      // ignore
    }
    throw new Error(`API Error (${response.status}): ${errorDetail}`);
  }

  return response.json();
}

export const api = {
  getHealth: (): Promise<SystemHealth> => {
    return fetchJson<SystemHealth>('/api/health');
  },

  simulate: (payload: SimulationRequest): Promise<SimulationResponse> => {
    return fetchJson<SimulationResponse>('/api/simulate', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  getExperiments: (): Promise<ExperimentDataset[]> => {
    return fetchJson<ExperimentDataset[]>('/api/experiments');
  },

  getExperimentById: (id: string): Promise<ExperimentDataset> => {
    return fetchJson<ExperimentDataset>(`/api/experiments/${id}`);
  },

  encryptMessage: (payload: EncryptRequest): Promise<EncryptResponse> => {
    return fetchJson<EncryptResponse>('/api/messaging/encrypt', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  decryptMessage: (payload: DecryptRequest): Promise<DecryptResponse> => {
    return fetchJson<DecryptResponse>('/api/messaging/decrypt', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
};
