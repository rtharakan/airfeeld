import { Link } from 'react-router-dom'
import { usePlayer } from '../contexts/PlayerContext'

export default function HomePage() {
  const { player } = usePlayer()

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="text-center py-16">
        <div className="space-y-6">
          <h1 className="text-5xl md:text-6xl font-bold text-white">
            Can You Spot the
            <span className="text-sky-400"> Airport?</span>
          </h1>
          <p className="text-xl text-sky-200 max-w-2xl mx-auto">
            Test your aviation knowledge! Look at photos taken from aircraft windows 
            and guess which airport you're approaching.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link
              to="/play"
              className="bg-sky-500 hover:bg-sky-400 text-white px-8 py-4 rounded-xl text-lg font-bold transition-all transform hover:scale-105 shadow-lg shadow-sky-500/30"
            >
              {player ? 'Continue Playing' : 'Start Playing'}
            </Link>
            <Link
              to="/upload"
              className="bg-sky-800/50 hover:bg-sky-700/50 text-white px-8 py-4 rounded-xl text-lg font-medium transition-colors border border-sky-600/50"
            >
              Upload Your Photo
            </Link>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-8">
        <h2 className="text-3xl font-bold text-white text-center mb-12">How It Works</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-sky-800/30 rounded-2xl p-8 text-center border border-sky-700/30">
            <div className="w-16 h-16 bg-sky-500/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <svg className="w-8 h-8 text-sky-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-white mb-3">View the Photo</h3>
            <p className="text-sky-300">
              See a photo taken from an aircraft window approaching or departing an airport.
            </p>
          </div>

          <div className="bg-sky-800/30 rounded-2xl p-8 text-center border border-sky-700/30">
            <div className="w-16 h-16 bg-sky-500/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <svg className="w-8 h-8 text-sky-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-white mb-3">Make Your Guess</h3>
            <p className="text-sky-300">
              Enter the airport name or IATA code. The closer you are, the more points you earn!
            </p>
          </div>

          <div className="bg-sky-800/30 rounded-2xl p-8 text-center border border-sky-700/30">
            <div className="w-16 h-16 bg-sky-500/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <svg className="w-8 h-8 text-sky-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-white mb-3">Climb the Ranks</h3>
            <p className="text-sky-300">
              Compete on the leaderboard and prove you're the ultimate aviation spotter!
            </p>
          </div>
        </div>
      </section>

      {/* Privacy First */}
      <section className="py-8">
        <div className="bg-gradient-to-r from-sky-800/50 to-sky-700/30 rounded-2xl p-8 md:p-12 border border-sky-600/30">
          <div className="flex flex-col md:flex-row items-center gap-8">
            <div className="flex-1 space-y-4">
              <div className="inline-flex items-center gap-2 bg-green-500/20 text-green-400 px-4 py-2 rounded-full text-sm font-medium">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                Privacy First
              </div>
              <h2 className="text-3xl font-bold text-white">Your Privacy is Protected</h2>
              <p className="text-sky-200 text-lg">
                We never store personal data. All photos have EXIF data stripped. 
                Your IP is hashed for rate limiting only. No accounts, no tracking, just fun.
              </p>
              <Link
                to="/privacy"
                className="inline-flex items-center gap-2 text-sky-400 hover:text-sky-300 transition-colors"
              >
                Learn more about our privacy practices
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </div>
            <div className="flex-shrink-0">
              <div className="w-32 h-32 bg-sky-500/20 rounded-full flex items-center justify-center">
                <svg className="w-16 h-16 text-sky-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      {player && (
        <section className="py-8">
          <h2 className="text-3xl font-bold text-white text-center mb-8">Your Stats</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="bg-sky-800/30 rounded-xl p-6 text-center border border-sky-700/30">
              <div className="text-4xl font-bold text-white">{player.totalScore.toLocaleString()}</div>
              <div className="text-sky-400 mt-1">Total Points</div>
            </div>
            <div className="bg-sky-800/30 rounded-xl p-6 text-center border border-sky-700/30">
              <div className="text-4xl font-bold text-white">{player.roundsPlayed}</div>
              <div className="text-sky-400 mt-1">Rounds Played</div>
            </div>
            <div className="bg-sky-800/30 rounded-xl p-6 text-center border border-sky-700/30">
              <div className="text-4xl font-bold text-white">{player.correctGuesses}</div>
              <div className="text-sky-400 mt-1">Correct Guesses</div>
            </div>
            <div className="bg-sky-800/30 rounded-xl p-6 text-center border border-sky-700/30">
              <div className="text-4xl font-bold text-white">
                {player.roundsPlayed > 0 
                  ? Math.round((player.correctGuesses / player.roundsPlayed) * 100) 
                  : 0}%
              </div>
              <div className="text-sky-400 mt-1">Accuracy</div>
            </div>
          </div>
        </section>
      )}
    </div>
  )
}
