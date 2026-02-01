import { createContext, useContext, useState, useCallback, ReactNode, useEffect } from 'react'

export interface Player {
  id: string
  username: string
  totalScore: number
  roundsPlayed: number
  correctGuesses: number
}

interface PlayerContextType {
  player: Player | null
  isLoading: boolean
  error: string | null
  register: (player: Player) => void
  updatePlayer: (updates: Partial<Player>) => void
  logout: () => void
  clearError: () => void
}

const PlayerContext = createContext<PlayerContextType | null>(null)

const PLAYER_STORAGE_KEY = 'airfeeld_player'

export function PlayerProvider({ children }: { children: ReactNode }) {
  const [player, setPlayer] = useState<Player | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Load player from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(PLAYER_STORAGE_KEY)
    if (stored) {
      try {
        setPlayer(JSON.parse(stored))
      } catch {
        localStorage.removeItem(PLAYER_STORAGE_KEY)
      }
    }
    setIsLoading(false)
  }, [])

  // Save player to localStorage when changed
  useEffect(() => {
    if (player) {
      localStorage.setItem(PLAYER_STORAGE_KEY, JSON.stringify(player))
    } else {
      localStorage.removeItem(PLAYER_STORAGE_KEY)
    }
  }, [player])

  const register = useCallback((newPlayer: Player) => {
    setPlayer(newPlayer)
  }, [])

  const updatePlayer = useCallback((updates: Partial<Player>) => {
    setPlayer(prev => prev ? { ...prev, ...updates } : null)
  }, [])

  const logout = useCallback(() => {
    setPlayer(null)
  }, [])

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  return (
    <PlayerContext.Provider value={{
      player,
      isLoading,
      error,
      register,
      updatePlayer,
      logout,
      clearError,
    }}>
      {children}
    </PlayerContext.Provider>
  )
}

export function usePlayer() {
  const context = useContext(PlayerContext)
  if (!context) {
    throw new Error('usePlayer must be used within a PlayerProvider')
  }
  return context
}

