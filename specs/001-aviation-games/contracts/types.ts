/**
 * TypeScript type definitions for Airfeeld Aviation Games API
 * Generated from OpenAPI specification
 * Version: 1.1.0
 */

// ============================================================================
// Security & Registration Types
// ============================================================================

export interface ProofOfWorkChallenge {
  challenge_id: string; // UUID
  challenge_nonce: string; // 32 characters
  difficulty: 4 | 5 | 6;
  algorithm: 'sha256';
  expires_at: string; // ISO 8601 timestamp
  instructions: string;
}

export interface PlayerRegistration {
  username: string; // 3-20 chars, alphanumeric + underscore
  challenge_id: string; // UUID from /players/challenge
  solution_nonce: string; // Client-computed solution
}

export interface PlayerCreated {
  player_id: string; // UUID
  username: string;
  created_at: string; // ISO 8601 timestamp
  message: string;
}

export interface PlayerDataExport {
  player_id: string; // UUID
  username: string;
  exported_at: string; // ISO 8601 timestamp
  data: {
    profile: {
      total_score: number;
      games_played: number;
      created_at: string;
    };
    game_history: Array<{
      round_id: string;
      score: number;
      completed_at: string;
    }>;
    uploaded_photos: Array<{
      photo_id: string;
      status: string;
      uploaded_at: string;
    }>;
  };
}

export type PhotoFlagReason = 
  | 'inappropriate' 
  | 'wrong_airport' 
  | 'copyright' 
  | 'non_aviation' 
  | 'other';

export interface PhotoFlagRequest {
  reason: PhotoFlagReason;
  description?: string; // max 500 chars
  reporter_id?: string | null; // UUID, optional for anonymous reports
}

export interface PhotoFlagResponse {
  flag_id: string; // UUID
  message: string;
}

export interface RateLimitInfo {
  limit: number;
  remaining: number;
  reset: number; // Unix timestamp
}

export interface RateLimitError extends APIError {
  error: 'rate_limit_exceeded';
  details: {
    retry_after_seconds: number;
  };
}

// ============================================================================
// Moderation Types (Internal)
// ============================================================================

export type ModerationStatus = 'pending' | 'approved' | 'rejected' | 'escalated';

export interface AutoCheckResults {
  magic_number_valid: boolean;
  phash_duplicate: boolean;
  phash_similar_ids: string[];
  photodna_flagged: boolean;
  histogram_aviation_score: number; // 0.0 to 1.0
  ai_generated_score: number; // 0.0 to 1.0
  ocr_text_detected: string[];
  file_size_valid: boolean;
  dimensions_valid: boolean;
  exif_stripped: boolean;
}

export interface ModerationQueueEntry {
  id: string; // UUID
  photo_id: string; // UUID
  auto_check_results: AutoCheckResults;
  status: ModerationStatus;
  rejection_reason?: string | null;
  moderator_id?: string | null; // UUID
  reviewed_at?: string | null; // ISO 8601 timestamp
  created_at: string;
  priority: number; // 1-10
}

export type AuditAction = 
  | 'player_created'
  | 'player_deleted'
  | 'photo_uploaded'
  | 'photo_moderated'
  | 'data_export'
  | 'rate_limit_triggered'
  | 'pow_failed'
  | 'admin_action';

export type AuditActorType = 'system' | 'player' | 'admin' | 'anonymous';

export interface AuditLogEntry {
  id: string; // UUID
  timestamp: string; // ISO 8601 timestamp
  action: AuditAction;
  actor_type: AuditActorType;
  actor_id_hash?: string | null; // SHA-256 hash
  target_type?: string | null;
  target_id_hash?: string | null; // SHA-256 hash
  metadata?: Record<string, unknown> | null;
  ip_hash?: string | null; // SHA-256 hash
}

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

// ============================================================================
// Proof-of-Work Utilities
// ============================================================================

/**
 * Solves a proof-of-work challenge by finding a nonce that produces
 * a SHA-256 hash with the required number of leading zeros.
 * 
 * @param challengeNonce - Server-provided nonce
 * @param difficulty - Number of leading zeros required
 * @param timeout - Maximum time in milliseconds (default: 10000)
 * @returns Solution nonce or null if timeout reached
 */
export async function solveProofOfWork(
  challengeNonce: string,
  difficulty: number,
  timeout: number = 10000
): Promise<string | null> {
  const startTime = Date.now();
  const target = '0'.repeat(difficulty);
  let nonce = 0;

  while (Date.now() - startTime < timeout) {
    const nonceStr = nonce.toString(16).padStart(16, '0');
    const data = challengeNonce + nonceStr;
    
    // Use Web Crypto API for SHA-256
    const encoder = new TextEncoder();
    const hashBuffer = await crypto.subtle.digest('SHA-256', encoder.encode(data));
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    
    if (hashHex.startsWith(target)) {
      return nonceStr;
    }
    
    nonce++;
  }
  
  return null; // Timeout reached
}

/**
 * Verifies a proof-of-work solution
 */
export async function verifyProofOfWork(
  challengeNonce: string,
  solutionNonce: string,
  difficulty: number
): Promise<boolean> {
  const target = '0'.repeat(difficulty);
  const data = challengeNonce + solutionNonce;
  
  const encoder = new TextEncoder();
  const hashBuffer = await crypto.subtle.digest('SHA-256', encoder.encode(data));
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  
  return hashHex.startsWith(target);
}

// ============================================================================
// Rate Limit Type Guards
// ============================================================================

export function isRateLimitError(error: unknown): error is RateLimitError {
  return (
    isAPIError(error) &&
    error.error === 'rate_limit_exceeded' &&
    'details' in error &&
    typeof (error as RateLimitError).details?.retry_after_seconds === 'number'
  );
}

export function getRateLimitFromHeaders(headers: Headers): RateLimitInfo | null {
  const limit = headers.get('X-RateLimit-Limit');
  const remaining = headers.get('X-RateLimit-Remaining');
  const reset = headers.get('X-RateLimit-Reset');
  
  if (limit && remaining && reset) {
    return {
      limit: parseInt(limit, 10),
      remaining: parseInt(remaining, 10),
      reset: parseInt(reset, 10),
    };
  }
  
  return null;
}
