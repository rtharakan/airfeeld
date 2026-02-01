import { useState, useEffect } from 'react'

interface GameRoundProps {
  roundId: string
  photoUrl: string
  difficulty: 'easy' | 'medium' | 'hard'
  expiresAt: string
  maxGuesses: number
  playerId: string
  onComplete: (result: {
    correct: boolean
    score: number
    actualAirport: string
    actualIataCode: string
    distance?: number
    timeTaken: number
    guessesUsed: number
  }) => void
}

export default function GameRound({
  roundId,
  photoUrl,
  difficulty,
  expiresAt,
  maxGuesses,
  playerId,
  onComplete,
}: GameRoundProps) {
  const [guess, setGuess] = useState('')
  const [guessHistory, setGuessHistory] = useState<Array<{ guess: string; hint?: string }>>([])
  const [guessesUsed, setGuessesUsed] = useState(0)
  const [timeLeft, setTimeLeft] = useState(0)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [startTime] = useState(Date.now())

  // Calculate time remaining
  useEffect(() => {
    const updateTimer = () => {
      const expires = new Date(expiresAt).getTime()
      const remaining = Math.max(0, Math.floor((expires - Date.now()) / 1000))
      setTimeLeft(remaining)

      if (remaining === 0) {
        // Time's up - submit final answer
        handleTimeUp()
      }
    }

    updateTimer()
    const interval = setInterval(updateTimer, 1000)
    return () => clearInterval(interval)
  }, [expiresAt])

  const handleTimeUp = async () => {
    // Get the round result
    try {
      const response = await fetch(`/api/v1/games/rounds/${roundId}/result`, {
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        onComplete({
          correct: false,
          score: 0,
          actualAirport: data.actual_airport,
          actualIataCode: data.actual_iata_code,
          timeTaken: Math.floor((Date.now() - startTime) / 1000),
          guessesUsed,
        })
      }
    } catch {
      // Silently fail
    }
  }

  const submitGuess = async () => {
    if (!guess.trim() || submitting) return

    setSubmitting(true)
    setError(null)

    try {
      const response = await fetch(`/api/v1/games/rounds/${roundId}/guess`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          player_id: playerId,
          guess: guess.trim(),
        }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to submit guess')
      }

      const data = await response.json()
      const newGuessesUsed = guessesUsed + 1
      setGuessesUsed(newGuessesUsed)

      if (data.correct) {
        // Correct answer!
        onComplete({
          correct: true,
          score: data.score,
          actualAirport: data.actual_airport,
          actualIataCode: data.actual_iata_code,
          timeTaken: Math.floor((Date.now() - startTime) / 1000),
          guessesUsed: newGuessesUsed,
        })
      } else {
        // Wrong answer
        setGuessHistory(prev => [...prev, { guess: guess.trim(), hint: data.hint }])
        setGuess('')

        if (data.guesses_remaining === 0) {
          // Out of guesses
          onComplete({
            correct: false,
            score: 0,
            actualAirport: data.actual_airport,
            actualIataCode: data.actual_iata_code,
            timeTaken: Math.floor((Date.now() - startTime) / 1000),
            guessesUsed: newGuessesUsed,
          })
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setSubmitting(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      submitGuess()
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const difficultyColors = {
    easy: 'bg-green-500/20 text-green-400 border-green-500/50',
    medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
    hard: 'bg-red-500/20 text-red-400 border-red-500/50',
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header with timer and stats */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <span className={`px-3 py-1 rounded-full text-sm font-medium border ${difficultyColors[difficulty]}`}>
            {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
          </span>
          <span className="text-sky-300">
            Guesses: {guessesUsed}/{maxGuesses}
          </span>
        </div>
        <div className={`text-2xl font-mono font-bold ${timeLeft < 30 ? 'text-red-400' : 'text-white'}`}>
          {formatTime(timeLeft)}
        </div>
      </div>

      {/* Photo */}
      <div className="relative rounded-2xl overflow-hidden bg-sky-900/30">
        <img
          src={photoUrl}
          alt="Airport view from aircraft"
          className="w-full h-auto max-h-[60vh] object-contain"
        />
        <div className="absolute inset-0 pointer-events-none ring-1 ring-inset ring-white/10 rounded-2xl" />
      </div>

      {/* Guess history */}
      {guessHistory.length > 0 && (
        <div className="space-y-2">
          {guessHistory.map((item, index) => (
            <div key={index} className="flex items-center gap-3 bg-sky-800/20 rounded-lg px-4 py-2">
              <svg className="w-5 h-5 text-red-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
              <span className="text-sky-300 line-through">{item.guess}</span>
              {item.hint && (
                <span className="text-sky-500 text-sm ml-auto">Hint: {item.hint}</span>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Guess input */}
      <div className="space-y-4">
        <div className="flex gap-3">
          <input
            type="text"
            value={guess}
            onChange={(e) => setGuess(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Enter airport name or IATA code (e.g., LAX, Heathrow)"
            disabled={submitting}
            className="flex-1 px-4 py-4 bg-sky-900/50 border border-sky-600/50 rounded-xl text-white placeholder-sky-500 text-lg focus:outline-none focus:border-sky-400 disabled:opacity-50"
            autoFocus
          />
          <button
            onClick={submitGuess}
            disabled={!guess.trim() || submitting}
            className="px-8 py-4 bg-sky-500 hover:bg-sky-400 disabled:bg-sky-700 disabled:cursor-not-allowed text-white rounded-xl font-bold text-lg transition-colors"
          >
            {submitting ? 'Checking...' : 'Guess'}
          </button>
        </div>

        {error && (
          <div className="bg-red-900/30 border border-red-500/50 rounded-lg p-3 text-red-200 text-sm">
            {error}
          </div>
        )}

        <p className="text-center text-sky-400 text-sm">
          Enter the airport name, city, or 3-letter IATA code
        </p>
      </div>

      {/* Tips */}
      <div className="bg-sky-800/20 rounded-xl p-4 border border-sky-700/30">
        <h4 className="text-sm font-semibold text-sky-300 mb-2">💡 Tips</h4>
        <ul className="text-sm text-sky-400 space-y-1">
          <li>• Look for distinctive landmarks, skylines, or geographical features</li>
          <li>• Check runway configurations and surrounding terrain</li>
          <li>• Airport codes (LAX, JFK, LHR) work as guesses too!</li>
        </ul>
      </div>
    </div>
  )
}
