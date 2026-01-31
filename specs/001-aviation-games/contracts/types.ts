/**
 * TypeScript type definitions for Airfeeld Aviation Games API
 * Generated from OpenAPI specification
 * Version: 1.0.0
 */

// ============================================================================
// Core Game Types
// ============================================================================

export interface GameRoundStart {
  round_id: string; // UUID
  round_token: string;
  photo: PhotoDisplay;
  expires_at: string; // ISO 8601 timestamp
}

export interface PhotoDisplay {
  id: string; // UUID
  url: string;
  alt_text: string;
  width: number;
  height: number;
}

export interface GuessRequest {
  round_id: string; // UUID
  round_token: string;
  guessed_airport: string; // ICAO code
}

export interface GuessResponse {
  correct: boolean;
  attempt: 1 | 2 | 3;
  final: boolean;
  score?: 0 | 3 | 5 | 10;
  distance_km?: number;
  distance_mi?: number;
  country_hint?: string;
  revealed_airport?: Airport;
  difficulty_multiplier?: number; // 1.0 to 3.0
  adjusted_score?: number;
  attribution?: Attribution;
}

// ============================================================================
// Aviation Data Types
// ============================================================================

export interface Airport {
  icao: string; // 4 uppercase letters
  iata?: string | null; // 3 uppercase letters
  name: string;
  country_code: string; // ISO 3166-1 alpha-2
  country_name: string;
  region: string;
  municipality: string;
  latitude: number; // -90 to 90
  longitude: number; // -180 to 180
}

export interface Airline {
  id: number;
  name: string;
  iata_code?: string | null;
  icao_code?: string | null;
  callsign?: string | null;
  country: string;
  active: boolean;
}

export interface Aircraft {
  id: number;
  manufacturer: string;
  model: string;
  type: 'narrow_body' | 'wide_body' | 'regional' | 'cargo';
  common_name: string;
}

// ============================================================================
// Attribution & Content Types
// ============================================================================

export type AttributionSource = 'flickr' | 'wikimedia' | 'public_domain' | 'user_upload';
export type LicenseType = 'CC BY 2.0' | 'CC BY-SA 2.0' | 'CC0' | 'Public Domain';

export interface Attribution {
  source: AttributionSource;
  photographer_name?: string | null;
  photographer_url?: string | null;
  license: LicenseType;
  original_url?: string | null;
}

export interface PhotoUploadResponse {
  photo_id: string; // UUID
  status: 'pending_review' | 'approved';
  message: string;
}

// ============================================================================
// Leaderboard & Player Types
// ============================================================================

export type LeaderboardPeriod = 'all_time' | 'monthly' | 'weekly';

export interface LeaderboardResponse {
  entries: LeaderboardEntry[];
  period: LeaderboardPeriod;
  last_updated: string; // ISO 8601 timestamp
}

export interface LeaderboardEntry {
  rank: number; // >= 1
  player_id: string; // UUID
  username: string;
  total_score: number;
  games_played: number;
}

export interface PlayerStats {
  player_id: string; // UUID
  username: string;
  total_score: number;
  games_played: number;
  rank?: number | null;
  average_score: number;
  best_round_score: number;
}

// ============================================================================
// System & Error Types
// ============================================================================

export interface HealthResponse {
  status: 'healthy';
  version: string;
  timestamp: string; // ISO 8601 timestamp
}

export interface APIError {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}

// ============================================================================
// Request/Response Collection Types
// ============================================================================

export interface AirportsListResponse {
  airports: Airport[];
  total: number;
  limit: number;
  offset: number;
}

export interface AirportSearchParams {
  query?: string;
  limit?: number; // max 100
  offset?: number;
}

export interface LeaderboardParams {
  limit?: number; // max 100
  period?: LeaderboardPeriod;
}

// ============================================================================
// Client State Management Types (Frontend-specific)
// ============================================================================

export type GameState = 'idle' | 'playing' | 'completed' | 'expired';
export type AttemptNumber = 1 | 2 | 3;

export interface GameRoundState {
  round_id: string;
  round_token: string;
  photo: PhotoDisplay;
  state: GameState;
  current_attempt: AttemptNumber;
  attempts: {
    attempt_1?: string; // ICAO code
    attempt_2?: string;
    attempt_3?: string;
  };
  feedback?: GuessResponse;
  expires_at: Date;
}

export interface PlayerSession {
  player_id: string;
  username: string;
  total_score: number;
  games_played: number;
}

// ============================================================================
// Form & Validation Types
// ============================================================================

export interface PhotoUploadForm {
  file: File;
  airport_id: string; // ICAO code
  player_id?: string; // Optional UUID
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

// ============================================================================
// API Client Configuration
// ============================================================================

export interface APIConfig {
  baseURL: string;
  timeout?: number; // milliseconds
  headers?: Record<string, string>;
}

export interface APIResponse<T> {
  data?: T;
  error?: APIError;
  status: number;
}

// ============================================================================
// Utility Types
// ============================================================================

export type Nullable<T> = T | null;
export type Optional<T> = T | undefined;

// Type guards
export function isAPIError(response: unknown): response is APIError {
  return (
    typeof response === 'object' &&
    response !== null &&
    'error' in response &&
    'message' in response
  );
}

export function isGuessCorrect(response: GuessResponse): boolean {
  return response.correct && response.final;
}

export function isRoundComplete(response: GuessResponse): boolean {
  return response.final;
}

export function hasDistanceFeedback(response: GuessResponse): response is GuessResponse & {
  distance_km: number;
  distance_mi: number;
} {
  return 'distance_km' in response && 'distance_mi' in response;
}

export function hasCountryHint(response: GuessResponse): response is GuessResponse & {
  country_hint: string;
} {
  return 'country_hint' in response;
}
