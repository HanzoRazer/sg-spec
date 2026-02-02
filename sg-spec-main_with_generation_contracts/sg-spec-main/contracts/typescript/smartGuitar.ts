/**
 * Smart Guitar TypeScript Interfaces
 * ===================================
 *
 * Contract definitions for Smart Guitar instruments.
 *
 * @version 1.0.0
 */

// =============================================================================
// CORE TYPES
// =============================================================================

export interface SmartGuitarSpec {
  model_id: 'smart_guitar';
  display_name: string;
  category: 'electric_guitar';
  status: 'COMPLETE' | 'STUB' | 'ASSETS_ONLY';
  scale_length_mm: number;
  fret_count: number;
  string_count: number;
  description: string;
}

export interface SmartGuitarInfo {
  ok: boolean;
  model_id: 'smart';
  display_name: string;
  category: string;
  architecture: SmartGuitarArchitecture;
  related_endpoints: SmartGuitarEndpoints;
}

// =============================================================================
// SUBSYSTEMS
// =============================================================================

export interface SmartGuitarIoT {
  processor: string;
  memory_gb: number;
  storage_gb: number;
  os: string;
}

export interface SmartGuitarConnectivity {
  wired: boolean;
  wireless: boolean;
  midi: boolean;
}

export interface SmartGuitarAudio {
  quality: string;
  latency: string;
  outputs: string[];
}

export interface SmartGuitarSensors {
  pickups: boolean;
  motion: boolean;
  touch: boolean;
}

export interface SmartGuitarPower {
  battery: boolean;
  runtime: string;
}

// =============================================================================
// ARCHITECTURE
// =============================================================================

export interface SmartGuitarArchitecture {
  hardware: {
    compute: string;
    connectivity: string[];
    audio: string;
  };
  software: {
    os: string;
  };
}

export interface SmartGuitarEndpoints {
  spec: string;
  cam: string;
}

// =============================================================================
// CAM FEATURES
// =============================================================================

export interface SmartGuitarCamFeatures {
  electronics_cavity: string;
  control_panel: string;
  pcb_mounting: string;
}

export interface SmartGuitarToolpath {
  name: string;
  type: 'pocket' | 'drill' | 'contour';
  description: string;
  component: SmartGuitarComponent;
}

export type SmartGuitarComponent =
  | 'electronics_cavity'
  | 'battery'
  | 'led_channel'
  | 'usb_port'
  | 'antenna';

// =============================================================================
// REGISTRY ENTRY
// =============================================================================

export interface SmartGuitarRegistryEntry {
  id: 'smart_guitar';
  display_name: string;
  status: 'COMPLETE';
  category: 'electric_guitar';
  scale_length_mm: number;
  fret_count: number;
  string_count: number;
  description: string;
  iot: SmartGuitarIoT;
  connectivity: SmartGuitarConnectivity;
  audio: SmartGuitarAudio;
  sensors: SmartGuitarSensors;
  power: SmartGuitarPower;
  features: string[];
  cam_features: SmartGuitarCamFeatures;
}

// =============================================================================
// API RESPONSE TYPES
// =============================================================================

export interface SmartGuitarHealthResponse {
  ok: boolean;
  subsystem: 'smart_guitar_cam';
  model_id: 'smart';
  capabilities: string[];
}

export interface SmartGuitarToolpathsResponse {
  ok: boolean;
  toolpaths: SmartGuitarToolpath[];
}

export interface SmartGuitarResource {
  name: string;
  type: 'documentation' | 'instructions';
  path?: string;
  description?: string;
}

export interface SmartGuitarBundleResponse {
  ok: boolean;
  bundle_version: string;
  resources: SmartGuitarResource[];
}

// =============================================================================
// FEATURE FLAGS
// =============================================================================

export const SMART_GUITAR_FEATURES = [
  'temperament_support',
  'led_markers',
  'effects_processing',
  'wireless_audio',
  'midi_output',
] as const;

export type SmartGuitarFeature = (typeof SMART_GUITAR_FEATURES)[number];

// =============================================================================
// DEFAULT VALUES
// =============================================================================

export const SMART_GUITAR_DEFAULTS: Partial<SmartGuitarSpec> = {
  model_id: 'smart_guitar',
  display_name: 'Smart Guitar',
  category: 'electric_guitar',
  scale_length_mm: 648.0,
  fret_count: 24,
  string_count: 6,
};
