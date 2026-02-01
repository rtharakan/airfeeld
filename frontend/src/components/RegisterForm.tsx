import { useState, useEffect } from 'react'
import { usePlayer } from '../contexts/PlayerContext'
import { solveProofOfWork } from '../utils/pow'

interface PowChallenge {
  challengeId: string
  prefix: string
  difficulty: number
  expiresAt: string
}

export default function RegisterForm() {
  const { register } = usePlayer()
  const [username, setUsername] = useState('')
  const [challenge, setChallenge] = useState<PowChallenge | null>(null)
  const [solving, setSolving] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  // Fetch PoW challenge on mount
  useEffect(() => {
    async function fetchChallenge() {
      try {
        const response = await fetch('/api/v1/players/pow/challenge')
        if (!response.ok) throw new Error('Failed to get challenge')
        const data = await response.json()
        setChallenge({
          challengeId: data.challenge_id,
          prefix: data.prefix,
          difficulty: data.difficulty,
          expiresAt: data.expires_at,
        })
      } catch (err) {
        setError('Failed to initialize. Please refresh the page.')
      }
    }
    fetchChallenge()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!username.trim()) {
      setError('Please enter a username')
      return
    }

    if (username.length < 3) {
      setError('Username must be at least 3 characters')
      return
    }

    if (username.length > 20) {
      setError('Username must be 20 characters or less')
      return
    }

    if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
      setError('Username can only contain letters, numbers, underscores, and hyphens')
      return
    }

    if (!challenge) {
      setError('Challenge not loaded. Please refresh the page.')
      return
    }

    setError(null)
    setSolving(true)
    setProgress(0)

    try {
      // Solve the proof of work challenge
      const solution = await solveProofOfWork(
        challenge.prefix,
        challenge.difficulty,
        (p) => setProgress(p)
      )

      setSolving(false)
      setLoading(true)

      // Register with the solution
      const response = await fetch('/api/v1/players/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username.trim(),
          challenge_id: challenge.challengeId,
          solution: solution,
        }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Registration failed')
      }

      const data = await response.json()
      
      // Register in player context
      register({
        id: data.id,
        username: data.username,
        totalScore: data.total_score || 0,
        roundsPlayed: data.rounds_played || 0,
        correctGuesses: data.correct_guesses || 0,
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      // Get a new challenge
      try {
        const response = await fetch('/api/v1/players/pow/challenge')
        if (response.ok) {
          const data = await response.json()
          setChallenge({
            challengeId: data.challenge_id,
            prefix: data.prefix,
            difficulty: data.difficulty,
            expiresAt: data.expires_at,
          })
        }
      } catch {
        // Ignore
      }
    } finally {
      setSolving(false)
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="bg-sky-800/30 rounded-2xl p-8 border border-sky-700/30">
        <div className="space-y-4">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-sky-200 mb-2">
              Choose a Username
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="AviationFan123"
              disabled={solving || loading}
              className="w-full px-4 py-3 bg-sky-900/50 border border-sky-600/50 rounded-lg text-white placeholder-sky-500 focus:outline-none focus:border-sky-400 disabled:opacity-50"
              maxLength={20}
            />
            <p className="text-xs text-sky-500 mt-2">
              3-20 characters, letters, numbers, underscores, and hyphens only
            </p>
          </div>

          {error && (
            <div className="bg-red-900/30 border border-red-500/50 rounded-lg p-4 text-red-200 text-sm">
              {error}
            </div>
          )}

          {solving && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-sky-300">Solving puzzle...</span>
                <span className="text-sky-400">{Math.round(progress * 100)}%</span>
              </div>
              <div className="h-2 bg-sky-900/50 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-sky-500 transition-all duration-200"
                  style={{ width: `${progress * 100}%` }}
                />
              </div>
              <p className="text-xs text-sky-500">
                Solving a proof-of-work puzzle to verify you're human...
              </p>
            </div>
          )}

          <button
            type="submit"
            disabled={!challenge || solving || loading || !username.trim()}
            className="w-full py-3 bg-sky-500 hover:bg-sky-400 disabled:bg-sky-700 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
          >
            {solving ? 'Solving Puzzle...' : loading ? 'Registering...' : 'Start Playing'}
          </button>
        </div>
      </div>

      {/* Privacy note */}
      <div className="text-center text-sm text-sky-400">
        <p>
          No email or password required. We don't track you.{' '}
          <a href="/privacy" className="text-sky-300 hover:text-sky-200 underline">
            Learn more
          </a>
        </p>
      </div>
    </form>
  )
}
