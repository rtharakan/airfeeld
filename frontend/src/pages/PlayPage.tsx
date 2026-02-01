import { useState, useEffect, useCallback } from 'react'
import { usePlayer } from '../contexts/PlayerContext'
import RegisterForm from '../components/RegisterForm'
import GameRound from '../components/GameRound'

interface RoundData {
  roundId: string
  photoUrl: string
  difficulty: 'easy' | 'medium' | 'hard'
  expiresAt: string
  maxGuesses: number
}

interface RoundResult {
  correct: boolean
  score: number
  actualAirport: string
  actualIataCode: string
  distance?: number
  timeTaken: number
  guessesUsed: number
}

export default function PlayPage() {
  const { player, updatePlayer } = usePlayer()
  const [round, setRound] = useState<RoundData | null>(null)
  const [result, setResult] = useState<RoundResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const startNewRound = useCallback(async () => {
    if (!player) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('/api/v1/games/rounds', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          playerId: player.id,
        }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to start new round')
      }

      const data = await response.json()
      setRound({
        roundId: data.round_id,
        photoUrl: `/api/v1/photos/${data.photo_id}/image`,
        difficulty: data.difficulty,
        expiresAt: data.expires_at,
        maxGuesses: data.max_guesses,
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }, [player])

  const handleRoundComplete = useCallback((roundResult: RoundResult) => {
    setResult(roundResult)
    setRound(null)

    // Update player stats
    if (player) {
      updatePlayer({
        totalScore: player.totalScore + roundResult.score,
        roundsPlayed: player.roundsPlayed + 1,
        correctGuesses: player.correctGuesses + (roundResult.correct ? 1 : 0),
      })
    }
  }, [player, updatePlayer])

  // Auto-start round for logged in players
  useEffect(() => {
    if (player && !round && !result && !loading) {
      startNewRound()
    }
  }, [player, round, result, loading, startNewRound])

  if (!player) {
    return (
      <div className="max-w-lg mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-4">Join the Game</h1>
          <p className="text-sky-200">
            Choose a username to start playing. No email or password required!
          </p>
        </div>
        <RegisterForm />
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-sky-500 border-t-transparent"></div>
        <p className="text-sky-200 mt-4">Loading next round...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-lg mx-auto text-center">
        <div className="bg-red-900/30 border border-red-500/50 rounded-xl p-6">
          <svg className="w-12 h-12 text-red-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <h2 className="text-xl font-bold text-white mb-2">Oops!</h2>
          <p className="text-red-200 mb-4">{error}</p>
          <button
            onClick={startNewRound}
            className="bg-sky-500 hover:bg-sky-400 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  if (result) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className={`rounded-2xl p-8 text-center border ${
          result.correct 
            ? 'bg-green-900/30 border-green-500/50' 
            : 'bg-amber-900/30 border-amber-500/50'
        }`}>
          {result.correct ? (
            <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-10 h-10 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          ) : (
            <div className="w-20 h-20 bg-amber-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-10 h-10 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          )}

          <h2 className="text-3xl font-bold text-white mb-2">
            {result.correct ? 'Correct!' : 'Not quite!'}
          </h2>
          
          <p className="text-xl text-sky-200 mb-6">
            The airport was <strong className="text-white">{result.actualAirport}</strong>
            {' '}({result.actualIataCode})
          </p>

          <div className="grid grid-cols-3 gap-4 mb-8">
            <div className="bg-sky-800/30 rounded-xl p-4">
              <div className="text-3xl font-bold text-sky-400">+{result.score}</div>
              <div className="text-sm text-sky-300">Points</div>
            </div>
            <div className="bg-sky-800/30 rounded-xl p-4">
              <div className="text-3xl font-bold text-sky-400">{result.timeTaken}s</div>
              <div className="text-sm text-sky-300">Time</div>
            </div>
            <div className="bg-sky-800/30 rounded-xl p-4">
              <div className="text-3xl font-bold text-sky-400">{result.guessesUsed}</div>
              <div className="text-sm text-sky-300">Guesses</div>
            </div>
          </div>

          <button
            onClick={startNewRound}
            className="bg-sky-500 hover:bg-sky-400 text-white px-8 py-4 rounded-xl text-lg font-bold transition-all transform hover:scale-105 shadow-lg shadow-sky-500/30"
          >
            Next Round
          </button>
        </div>
      </div>
    )
  }

  if (round) {
    return (
      <GameRound
        roundId={round.roundId}
        photoUrl={round.photoUrl}
        difficulty={round.difficulty}
        expiresAt={round.expiresAt}
        maxGuesses={round.maxGuesses}
        playerId={player.id}
        onComplete={handleRoundComplete}
      />
    )
  }

  return null
}
