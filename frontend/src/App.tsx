import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { PlayerProvider } from './contexts/PlayerContext'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import PlayPage from './pages/PlayPage'
import LeaderboardPage from './pages/LeaderboardPage'
import UploadPage from './pages/UploadPage'
import PrivacyPage from './pages/PrivacyPage'

function App() {
  return (
    <BrowserRouter>
      <PlayerProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/play" element={<PlayPage />} />
            <Route path="/leaderboard" element={<LeaderboardPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/privacy" element={<PrivacyPage />} />
          </Routes>
        </Layout>
      </PlayerProvider>
    </BrowserRouter>
  )
}

export default App
