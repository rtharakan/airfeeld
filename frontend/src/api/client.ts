/**
 * API Client for Airfeeld Backend
 */

const API_BASE = '/api/v1'

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail?: string
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let detail: string | undefined
    try {
      const data = await response.json()
      detail = data.detail
    } catch {
      // Ignore JSON parse errors
    }
    throw new ApiError(
      detail || `HTTP ${response.status}`,
      response.status,
      detail
    )
  }
  return response.json()
}

// Player API
export interface Player {
  id: string
  username: string
  total_score: number
  rounds_played: number
  correct_guesses: number
  created_at: string
}

export interface PowChallenge {
  challenge_id: string
  prefix: string
  difficulty: number
  expires_at: string
}

export interface RegisterRequest {
  username: string
  challenge_id: string
  solution: string
}

export const playerApi = {
  async getChallenge(): Promise<PowChallenge> {
    const response = await fetch(`${API_BASE}/players/pow/challenge`)
    return handleResponse(response)
  },

  async register(data: RegisterRequest): Promise<Player> {
    const response = await fetch(`${API_BASE}/players/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    return handleResponse(response)
  },

  async getPlayer(id: string): Promise<Player> {
    const response = await fetch(`${API_BASE}/players/${id}`)
    return handleResponse(response)
  },

  async getLeaderboard(limit = 100): Promise<Player[]> {
    const response = await fetch(`${API_BASE}/players/leaderboard?limit=${limit}`)
    return handleResponse(response)
  },
}

// Game API
export interface GameRound {
  round_id: string
  photo_id: string
  difficulty: 'easy' | 'medium' | 'hard'
  expires_at: string
  max_guesses: number
}

export interface GuessResult {
  correct: boolean
  score?: number
  hint?: string
  guesses_remaining: number
  actual_airport?: string
  actual_iata_code?: string
}

export interface RoundResult {
  actual_airport: string
  actual_iata_code: string
  score: number
  correct: boolean
}

export const gameApi = {
  async startRound(playerId: string): Promise<GameRound> {
    const response = await fetch(`${API_BASE}/games/rounds`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId }),
    })
    return handleResponse(response)
  },

  async submitGuess(roundId: string, playerId: string, guess: string): Promise<GuessResult> {
    const response = await fetch(`${API_BASE}/games/rounds/${roundId}/guess`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_id: playerId, guess }),
    })
    return handleResponse(response)
  },

  async getRoundResult(roundId: string): Promise<RoundResult> {
    const response = await fetch(`${API_BASE}/games/rounds/${roundId}/result`)
    return handleResponse(response)
  },
}

// Photo API
export interface Photo {
  id: string
  difficulty: 'easy' | 'medium' | 'hard'
  moderation_status: 'pending' | 'approved' | 'rejected'
}

export interface UploadResult {
  id: string
  message: string
}

export const photoApi = {
  async upload(
    file: File,
    airportName: string,
    iataCode: string,
    difficulty: 'easy' | 'medium' | 'hard',
    uploaderId?: string
  ): Promise<UploadResult> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('airport_name', airportName)
    formData.append('iata_code', iataCode.toUpperCase())
    formData.append('difficulty', difficulty)
    if (uploaderId) {
      formData.append('uploader_id', uploaderId)
    }

    const response = await fetch(`${API_BASE}/photos/upload`, {
      method: 'POST',
      body: formData,
    })
    return handleResponse(response)
  },

  getImageUrl(photoId: string): string {
    return `${API_BASE}/photos/${photoId}/image`
  },

  async getRandomPhoto(): Promise<Photo> {
    const response = await fetch(`${API_BASE}/photos/random`)
    return handleResponse(response)
  },
}

// Health API
export interface HealthStatus {
  status: string
  timestamp: string
  version: string
}

export const healthApi = {
  async check(): Promise<HealthStatus> {
    const response = await fetch(`${API_BASE}/health`)
    return handleResponse(response)
  },
}
