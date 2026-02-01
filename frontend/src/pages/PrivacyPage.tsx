import { Link } from 'react-router-dom'

export default function PrivacyPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-12">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-white mb-4">Privacy Policy</h1>
        <p className="text-sky-200">
          Last updated: {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
        </p>
      </div>

      {/* Constitution Badge */}
      <div className="bg-gradient-to-r from-green-900/30 to-green-800/20 rounded-2xl p-6 border border-green-500/30">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 bg-green-500/20 rounded-xl flex items-center justify-center flex-shrink-0">
            <svg className="w-6 h-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <div>
            <h2 className="text-xl font-bold text-white mb-2">Privacy by Design</h2>
            <p className="text-green-200">
              Airfeeld is built with privacy as a core principle, not an afterthought. 
              Our entire architecture is designed to minimize data collection while 
              maximizing your enjoyment of the game.
            </p>
          </div>
        </div>
      </div>

      {/* Principles */}
      <section className="space-y-6">
        <h2 className="text-2xl font-bold text-white">Our Privacy Principles</h2>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-sky-800/30 rounded-xl p-6 border border-sky-700/30">
            <div className="w-10 h-10 bg-sky-500/20 rounded-lg flex items-center justify-center mb-4">
              <span className="text-xl">🚫</span>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">No Personal Data Collection</h3>
            <p className="text-sky-300">
              We don't collect your name, email, phone number, or any other personal information. 
              Your username is the only identifier you provide.
            </p>
          </div>

          <div className="bg-sky-800/30 rounded-xl p-6 border border-sky-700/30">
            <div className="w-10 h-10 bg-sky-500/20 rounded-lg flex items-center justify-center mb-4">
              <span className="text-xl">🔒</span>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">IP Hashing</h3>
            <p className="text-sky-300">
              Your IP address is cryptographically hashed immediately upon connection. 
              We can never reverse this hash to reveal your actual IP address.
            </p>
          </div>

          <div className="bg-sky-800/30 rounded-xl p-6 border border-sky-700/30">
            <div className="w-10 h-10 bg-sky-500/20 rounded-lg flex items-center justify-center mb-4">
              <span className="text-xl">📷</span>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">EXIF Data Stripping</h3>
            <p className="text-sky-300">
              All uploaded photos have their EXIF metadata (including GPS coordinates, 
              camera info, and timestamps) completely removed before storage.
            </p>
          </div>

          <div className="bg-sky-800/30 rounded-xl p-6 border border-sky-700/30">
            <div className="w-10 h-10 bg-sky-500/20 rounded-lg flex items-center justify-center mb-4">
              <span className="text-xl">🍪</span>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">No Tracking Cookies</h3>
            <p className="text-sky-300">
              We don't use any tracking cookies, analytics services, or third-party scripts 
              that monitor your behavior across the web.
            </p>
          </div>
        </div>
      </section>

      {/* What We Store */}
      <section className="space-y-6">
        <h2 className="text-2xl font-bold text-white">What We Store</h2>
        
        <div className="bg-sky-800/30 rounded-xl overflow-hidden border border-sky-700/30">
          <table className="w-full">
            <thead className="bg-sky-900/50">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-semibold text-sky-300">Data</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-sky-300">Purpose</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-sky-300">Retention</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-sky-700/30">
              <tr>
                <td className="px-6 py-4 text-white">Username</td>
                <td className="px-6 py-4 text-sky-300">Display on leaderboard</td>
                <td className="px-6 py-4 text-sky-400">Until account deletion</td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-white">Player ID</td>
                <td className="px-6 py-4 text-sky-300">Link scores to player</td>
                <td className="px-6 py-4 text-sky-400">Until account deletion</td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-white">Game scores</td>
                <td className="px-6 py-4 text-sky-300">Leaderboard & statistics</td>
                <td className="px-6 py-4 text-sky-400">Until account deletion</td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-white">Hashed IP (SHA-256)</td>
                <td className="px-6 py-4 text-sky-300">Rate limiting only</td>
                <td className="px-6 py-4 text-sky-400">24 hours</td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-white">Uploaded photos</td>
                <td className="px-6 py-4 text-sky-300">Game content</td>
                <td className="px-6 py-4 text-sky-400">Indefinitely (EXIF stripped)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* Security Measures */}
      <section className="space-y-6">
        <h2 className="text-2xl font-bold text-white">Security Measures</h2>
        
        <div className="space-y-4">
          <div className="flex items-start gap-4 bg-sky-800/20 rounded-xl p-4">
            <div className="w-8 h-8 bg-sky-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg className="w-4 h-4 text-sky-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <div>
              <h4 className="font-semibold text-white">Proof of Work</h4>
              <p className="text-sky-300 text-sm">
                Registration requires solving a computational puzzle, preventing automated 
                bot registrations without requiring personal information.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-4 bg-sky-800/20 rounded-xl p-4">
            <div className="w-8 h-8 bg-sky-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg className="w-4 h-4 text-sky-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h4 className="font-semibold text-white">Rate Limiting</h4>
              <p className="text-sky-300 text-sm">
                All API endpoints are rate-limited using hashed IPs to prevent abuse 
                while maintaining your privacy.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-4 bg-sky-800/20 rounded-xl p-4">
            <div className="w-8 h-8 bg-sky-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg className="w-4 h-4 text-sky-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h4 className="font-semibold text-white">Security Headers</h4>
              <p className="text-sky-300 text-sm">
                OWASP-recommended security headers are applied to all responses, 
                protecting against common web vulnerabilities.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-4 bg-sky-800/20 rounded-xl p-4">
            <div className="w-8 h-8 bg-sky-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg className="w-4 h-4 text-sky-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h4 className="font-semibold text-white">Audit Logging</h4>
              <p className="text-sky-300 text-sm">
                Security-relevant events are logged using hashed identifiers, 
                never raw IP addresses or personal data.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Your Rights */}
      <section className="space-y-6">
        <h2 className="text-2xl font-bold text-white">Your Rights</h2>
        
        <div className="bg-sky-800/30 rounded-xl p-6 border border-sky-700/30 space-y-4">
          <p className="text-sky-200">Since we collect minimal data, exercising your rights is simple:</p>
          
          <ul className="space-y-3">
            <li className="flex items-start gap-3 text-sky-300">
              <span className="text-sky-400">•</span>
              <span><strong className="text-white">Data Access:</strong> Your public data (username, scores) is visible on your profile and the leaderboard.</span>
            </li>
            <li className="flex items-start gap-3 text-sky-300">
              <span className="text-sky-400">•</span>
              <span><strong className="text-white">Data Deletion:</strong> Log out and your session data is removed. Contact us to fully delete your player record.</span>
            </li>
            <li className="flex items-start gap-3 text-sky-300">
              <span className="text-sky-400">•</span>
              <span><strong className="text-white">Data Portability:</strong> Since we only store your username and scores, there's minimal data to export.</span>
            </li>
          </ul>
        </div>
      </section>

      {/* Open Source */}
      <section className="space-y-6">
        <h2 className="text-2xl font-bold text-white">Open Source</h2>
        
        <div className="bg-sky-800/30 rounded-xl p-6 border border-sky-700/30">
          <p className="text-sky-200 mb-4">
            Airfeeld is open source. You can verify our privacy claims by reviewing our code:
          </p>
          <a 
            href="https://github.com/airfeeld/airfeeld" 
            target="_blank" 
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 bg-sky-700/50 hover:bg-sky-600/50 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
            </svg>
            View on GitHub
          </a>
        </div>
      </section>

      {/* Contact */}
      <section className="space-y-6">
        <h2 className="text-2xl font-bold text-white">Contact Us</h2>
        
        <div className="bg-sky-800/30 rounded-xl p-6 border border-sky-700/30">
          <p className="text-sky-200">
            If you have any questions about this privacy policy or want to exercise your data rights, 
            please open an issue on our GitHub repository or contact us at{' '}
            <a href="mailto:privacy@airfeeld.app" className="text-sky-400 hover:text-sky-300">
              privacy@airfeeld.app
            </a>
          </p>
        </div>
      </section>

      {/* Back to home */}
      <div className="text-center pt-8">
        <Link
          to="/"
          className="inline-flex items-center gap-2 text-sky-400 hover:text-sky-300 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Home
        </Link>
      </div>
    </div>
  )
}
