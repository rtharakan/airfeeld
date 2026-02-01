import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { usePlayer } from '../contexts/PlayerContext'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const { player, logout } = usePlayer()

  const navLinks = [
    { path: '/', label: 'Home' },
    { path: '/play', label: 'Play' },
    { path: '/leaderboard', label: 'Leaderboard' },
    { path: '/upload', label: 'Upload' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-b from-sky-900 to-sky-950">
      {/* Header */}
      <header className="bg-sky-800/50 backdrop-blur-sm border-b border-sky-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-2">
              <svg className="w-8 h-8 text-sky-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/>
              </svg>
              <span className="text-xl font-bold text-white">Airfeeld</span>
            </Link>

            {/* Navigation */}
            <nav className="hidden md:flex items-center space-x-1">
              {navLinks.map(link => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    location.pathname === link.path
                      ? 'bg-sky-700 text-white'
                      : 'text-sky-200 hover:bg-sky-700/50 hover:text-white'
                  }`}
                >
                  {link.label}
                </Link>
              ))}
            </nav>

            {/* Player info */}
            <div className="flex items-center space-x-4">
              {player ? (
                <div className="flex items-center space-x-3">
                  <div className="text-right">
                    <div className="text-sm font-medium text-white">{player.username}</div>
                    <div className="text-xs text-sky-300">{player.totalScore.toLocaleString()} pts</div>
                  </div>
                  <button
                    onClick={logout}
                    className="text-sm text-sky-300 hover:text-white transition-colors"
                  >
                    Logout
                  </button>
                </div>
              ) : (
                <Link
                  to="/play"
                  className="bg-sky-500 hover:bg-sky-400 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                >
                  Start Playing
                </Link>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-sky-900/50 border-t border-sky-800/50 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
            <div className="text-sm text-sky-400">
              Airfeeld &mdash; Privacy-preserving aviation guessing game
            </div>
            <div className="flex items-center space-x-6">
              <Link to="/privacy" className="text-sm text-sky-400 hover:text-sky-300 transition-colors">
                Privacy Policy
              </Link>
              <a 
                href="https://github.com/airfeeld/airfeeld" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-sm text-sky-400 hover:text-sky-300 transition-colors"
              >
                GitHub
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
