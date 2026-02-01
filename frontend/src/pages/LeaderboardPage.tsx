import { useState, useEffect } from 'react'
import { usePlayer } from '../contexts/PlayerContext'

interface LeaderboardEntry {
  rank: number
  username: string
  totalScore: number
  roundsPlayed: number
  correctGuesses: number
  accuracy: number
  isCurrentPlayer: boolean
}

export default function LeaderboardPage() {
  const { player } = usePlayer()
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [sortBy, setSortBy] = useState<'score' | 'accuracy' | 'rounds'>('score')

  useEffect(() => {
    async function fetchLeaderboard() {
      try {
        const response = await fetch('/api/v1/players/leaderboard')
        if (!response.ok) {
          throw new Error('Failed to fetch leaderboard')
        }
        const data = await response.json()
        
        // Transform API data
        const entries: LeaderboardEntry[] = data.map((entry: any, index: number) => ({
          rank: index + 1,
          username: entry.username,
          totalScore: entry.total_score,
          roundsPlayed: entry.rounds_played,
          correctGuesses: entry.correct_guesses,
          accuracy: entry.rounds_played > 0 
            ? Math.round((entry.correct_guesses / entry.rounds_played) * 100) 
            : 0,
          isCurrentPlayer: player?.id === entry.id,
        }))
        
        setLeaderboard(entries)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred')
      } finally {
        setLoading(false)
      }
    }

    fetchLeaderboard()
  }, [player])

  const sortedLeaderboard = [...leaderboard].sort((a, b) => {
    switch (sortBy) {
      case 'accuracy':
        return b.accuracy - a.accuracy
      case 'rounds':
        return b.roundsPlayed - a.roundsPlayed
      default:
        return b.totalScore - a.totalScore
    }
  }).map((entry, index) => ({ ...entry, rank: index + 1 }))

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-sky-500 border-t-transparent"></div>
        <p className="text-sky-200 mt-4">Loading leaderboard...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-lg mx-auto text-center">
        <div className="bg-red-900/30 border border-red-500/50 rounded-xl p-6">
          <p className="text-red-200">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-white mb-4">Leaderboard</h1>
        <p className="text-sky-200">See how you stack up against other aviation spotters</p>
      </div>

      {/* Sort controls */}
      <div className="flex justify-center gap-2">
        <button
          onClick={() => setSortBy('score')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            sortBy === 'score'
              ? 'bg-sky-500 text-white'
              : 'bg-sky-800/30 text-sky-300 hover:bg-sky-700/50'
          }`}
        >
          By Score
        </button>
        <button
          onClick={() => setSortBy('accuracy')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            sortBy === 'accuracy'
              ? 'bg-sky-500 text-white'
              : 'bg-sky-800/30 text-sky-300 hover:bg-sky-700/50'
          }`}
        >
          By Accuracy
        </button>
        <button
          onClick={() => setSortBy('rounds')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            sortBy === 'rounds'
              ? 'bg-sky-500 text-white'
              : 'bg-sky-800/30 text-sky-300 hover:bg-sky-700/50'
          }`}
        >
          By Rounds
        </button>
      </div>

      {/* Leaderboard table */}
      <div className="bg-sky-800/30 rounded-2xl border border-sky-700/30 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-sky-900/50">
                <th className="px-6 py-4 text-left text-sm font-semibold text-sky-300">Rank</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-sky-300">Player</th>
                <th className="px-6 py-4 text-right text-sm font-semibold text-sky-300">Score</th>
                <th className="px-6 py-4 text-right text-sm font-semibold text-sky-300">Rounds</th>
                <th className="px-6 py-4 text-right text-sm font-semibold text-sky-300">Correct</th>
                <th className="px-6 py-4 text-right text-sm font-semibold text-sky-300">Accuracy</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-sky-700/30">
              {sortedLeaderboard.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-sky-400">
                    No players yet. Be the first to play!
                  </td>
                </tr>
              ) : (
                sortedLeaderboard.map((entry) => (
                  <tr 
                    key={entry.username}
                    className={`${
                      entry.isCurrentPlayer 
                        ? 'bg-sky-500/20' 
                        : 'hover:bg-sky-800/20'
                    } transition-colors`}
                  >
                    <td className="px-6 py-4">
                      {entry.rank <= 3 ? (
                        <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full font-bold ${
                          entry.rank === 1 
                            ? 'bg-yellow-500/20 text-yellow-400' 
                            : entry.rank === 2 
                              ? 'bg-gray-300/20 text-gray-300' 
                              : 'bg-amber-600/20 text-amber-500'
                        }`}>
                          {entry.rank}
                        </span>
                      ) : (
                        <span className="text-sky-300 pl-2">{entry.rank}</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`font-medium ${entry.isCurrentPlayer ? 'text-sky-400' : 'text-white'}`}>
                        {entry.username}
                        {entry.isCurrentPlayer && (
                          <span className="ml-2 text-xs bg-sky-500/30 text-sky-300 px-2 py-1 rounded">You</span>
                        )}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right font-semibold text-white">
                      {entry.totalScore.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 text-right text-sky-300">
                      {entry.roundsPlayed}
                    </td>
                    <td className="px-6 py-4 text-right text-sky-300">
                      {entry.correctGuesses}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className={`${
                        entry.accuracy >= 75 
                          ? 'text-green-400' 
                          : entry.accuracy >= 50 
                            ? 'text-yellow-400' 
                            : 'text-sky-300'
                      }`}>
                        {entry.accuracy}%
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Current player position if not in top */}
      {player && !sortedLeaderboard.some(e => e.isCurrentPlayer) && (
        <div className="bg-sky-800/30 rounded-xl p-6 border border-sky-700/30 text-center">
          <p className="text-sky-200">
            You haven't played any rounds yet. 
            <a href="/play" className="text-sky-400 hover:text-sky-300 ml-1">Start playing</a> 
            to get on the leaderboard!
          </p>
        </div>
      )}
    </div>
  )
}
