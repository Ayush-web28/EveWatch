/**
 * TypeScript definitions for EveWatch Quantum Platform
 * Synchronized with backend/schemas.py
 */

export interface SimulationRequest {
  num_qubits: number;
  eve_present: boolean;
  eve_fraction: number;
  channel_noise_prob: number;
  depolarizing_error_prob: number;
  readout_error_prob: number;
  abort_threshold: number;
  sample_size: number;
  seed?: number;
  use_fake_backend: boolean;
  include_circuit: boolean;
}

export interface QubitEvent {
  index: number;
  alice_bit: number;
  alice_basis: number; // 0: Z, 1: X
  alice_basis_label: string;
  alice_state: string; // "|0⟩", "|1⟩", "|+⟩", "|-⟩"
  eve_intercepted: boolean;
  eve_basis?: number | null;
  eve_basis_label?: string | null;
  eve_measured_bit?: number | null;
  bob_basis: number;
  bob_basis_label: string;
  bob_measured_bit: number;
  bases_match: boolean;
  role: 'discarded' | 'sampled' | 'retained';
  is_error?: boolean | null;
}

export interface SimulationResponse {
  num_qubits: number;
  sifted_count: number;
  sifted_ratio: number;
  sample_count: number;
  sample_qber: floatNumber;
  overall_qber: floatNumber;
  abort_threshold: number;
  aborted: boolean;
  verdict: string;
  verdict_detail: string;
  secret_key_rate: number;
  retained_key_length: number;
  alice_key_preview: string;
  bob_key_preview: string;
  key_agreement_rate: number;
  qubit_events: QubitEvent[];
  circuit_ascii?: string | null;
  metadata: {
    eve_present: boolean;
    eve_fraction: number;
    channel_noise_prob: number;
    theoretical_qber: number;
    noise_model: string;
    seed?: number | null;
  };
}

export type floatNumber = number;

export interface EncryptRequest {
  message: string;
  key_bits?: number[];
  estimated_qber?: number;
}

export interface EncryptResponse {
  original_message: string;
  key_length_used: number;
  parity_corrections: number;
  final_secret_bits: number;
  hex_ciphertext: string;
  binary_ciphertext_preview: string;
  decrypted_bob: string;
  decrypted_eve_sample: string;
  roundtrip_verified: boolean;
  explanation: string;
}

export interface DecryptRequest {
  hex_ciphertext: string;
  key_bits: number[];
}

export interface DecryptResponse {
  decrypted_message: string;
  success: boolean;
}

export interface ExperimentDataset {
  id: string;
  title: string;
  description: string;
  source_file: string;
  columns: string[];
  rows: Record<string, any>[];
  summary: Record<string, any>;
}

export interface SystemHealth {
  status: string;
  service: string;
  version: string;
  qiskit_version: string;
  aer_simulator: string;
  ibm_token_configured: boolean;
}
