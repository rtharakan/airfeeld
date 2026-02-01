import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { usePlayer } from '../contexts/PlayerContext'

type UploadStep = 'select' | 'preview' | 'details' | 'uploading' | 'success' | 'error'

interface PhotoDetails {
  airport_name: string
  iata_code: string
  difficulty: 'easy' | 'medium' | 'hard'
}

export default function UploadPage() {
  const { player } = usePlayer()
  const [step, setStep] = useState<UploadStep>('select')
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [details, setDetails] = useState<PhotoDetails>({
    airport_name: '',
    iata_code: '',
    difficulty: 'medium',
  })
  const [error, setError] = useState<string | null>(null)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (file) {
      setFile(file)
      setPreview(URL.createObjectURL(file))
      setStep('preview')
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/webp': ['.webp'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: false,
  })

  const handleDetailsChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setDetails(prev => ({ ...prev, [name]: value }))
  }

  const handleUpload = async () => {
    if (!file || !details.airport_name || !details.iata_code) {
      setError('Please fill in all required fields')
      return
    }

    setStep('uploading')
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('airport_name', details.airport_name)
      formData.append('iata_code', details.iata_code.toUpperCase())
      formData.append('difficulty', details.difficulty)
      if (player) {
        formData.append('uploader_id', player.id)
      }

      const response = await fetch('/api/v1/photos/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Upload failed')
      }

      setStep('success')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      setStep('error')
    }
  }

  const resetUpload = () => {
    setFile(null)
    setPreview(null)
    setDetails({ airport_name: '', iata_code: '', difficulty: 'medium' })
    setStep('select')
    setError(null)
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-white mb-4">Upload Photo</h1>
        <p className="text-sky-200">
          Share your aviation photos to help grow the game! 
          All EXIF data will be automatically stripped for privacy.
        </p>
      </div>

      {/* Step: Select file */}
      {step === 'select' && (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-sky-400 bg-sky-500/10'
              : 'border-sky-600/50 hover:border-sky-500 hover:bg-sky-800/20'
          }`}
        >
          <input {...getInputProps()} />
          <svg className="w-16 h-16 text-sky-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          {isDragActive ? (
            <p className="text-xl text-sky-300">Drop the photo here...</p>
          ) : (
            <>
              <p className="text-xl text-white mb-2">Drag & drop your photo here</p>
              <p className="text-sky-400">or click to select a file</p>
              <p className="text-sm text-sky-500 mt-4">JPEG, PNG, or WebP • Max 10MB</p>
            </>
          )}
        </div>
      )}

      {/* Step: Preview */}
      {step === 'preview' && preview && (
        <div className="space-y-6">
          <div className="relative rounded-2xl overflow-hidden">
            <img src={preview} alt="Preview" className="w-full h-auto" />
            <button
              onClick={resetUpload}
              className="absolute top-4 right-4 bg-black/50 hover:bg-black/70 text-white p-2 rounded-lg transition-colors"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div className="flex justify-center gap-4">
            <button
              onClick={resetUpload}
              className="px-6 py-3 bg-sky-800/50 hover:bg-sky-700/50 text-white rounded-lg font-medium transition-colors"
            >
              Choose Different Photo
            </button>
            <button
              onClick={() => setStep('details')}
              className="px-6 py-3 bg-sky-500 hover:bg-sky-400 text-white rounded-lg font-medium transition-colors"
            >
              Continue
            </button>
          </div>
        </div>
      )}

      {/* Step: Details */}
      {step === 'details' && (
        <div className="bg-sky-800/30 rounded-2xl p-8 border border-sky-700/30 space-y-6">
          <h2 className="text-2xl font-bold text-white">Photo Details</h2>
          
          {preview && (
            <img src={preview} alt="Preview" className="w-full h-48 object-cover rounded-lg" />
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="airport_name" className="block text-sm font-medium text-sky-200 mb-2">
                Airport Name *
              </label>
              <input
                type="text"
                id="airport_name"
                name="airport_name"
                value={details.airport_name}
                onChange={handleDetailsChange}
                placeholder="e.g., Los Angeles International Airport"
                className="w-full px-4 py-3 bg-sky-900/50 border border-sky-600/50 rounded-lg text-white placeholder-sky-500 focus:outline-none focus:border-sky-400"
                required
              />
            </div>

            <div>
              <label htmlFor="iata_code" className="block text-sm font-medium text-sky-200 mb-2">
                IATA Code *
              </label>
              <input
                type="text"
                id="iata_code"
                name="iata_code"
                value={details.iata_code}
                onChange={handleDetailsChange}
                placeholder="e.g., LAX"
                maxLength={3}
                className="w-full px-4 py-3 bg-sky-900/50 border border-sky-600/50 rounded-lg text-white placeholder-sky-500 focus:outline-none focus:border-sky-400 uppercase"
                required
              />
              <p className="text-xs text-sky-500 mt-1">
                3-letter airport code (e.g., JFK, LHR, NRT)
              </p>
            </div>

            <div>
              <label htmlFor="difficulty" className="block text-sm font-medium text-sky-200 mb-2">
                Difficulty
              </label>
              <select
                id="difficulty"
                name="difficulty"
                value={details.difficulty}
                onChange={handleDetailsChange}
                className="w-full px-4 py-3 bg-sky-900/50 border border-sky-600/50 rounded-lg text-white focus:outline-none focus:border-sky-400"
              >
                <option value="easy">Easy - Distinctive landmarks visible</option>
                <option value="medium">Medium - Some identifying features</option>
                <option value="hard">Hard - Minimal identifying features</option>
              </select>
            </div>
          </div>

          {error && (
            <div className="bg-red-900/30 border border-red-500/50 rounded-lg p-4 text-red-200">
              {error}
            </div>
          )}

          <div className="flex justify-between pt-4">
            <button
              onClick={() => setStep('preview')}
              className="px-6 py-3 bg-sky-800/50 hover:bg-sky-700/50 text-white rounded-lg font-medium transition-colors"
            >
              Back
            </button>
            <button
              onClick={handleUpload}
              disabled={!details.airport_name || !details.iata_code}
              className="px-6 py-3 bg-sky-500 hover:bg-sky-400 disabled:bg-sky-700 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
            >
              Upload Photo
            </button>
          </div>
        </div>
      )}

      {/* Step: Uploading */}
      {step === 'uploading' && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-sky-500 border-t-transparent mx-auto"></div>
          <p className="text-xl text-white mt-6">Uploading your photo...</p>
          <p className="text-sky-400 mt-2">Stripping EXIF data and processing</p>
        </div>
      )}

      {/* Step: Success */}
      {step === 'success' && (
        <div className="bg-green-900/30 border border-green-500/50 rounded-2xl p-8 text-center">
          <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-10 h-10 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-white mb-4">Upload Successful!</h2>
          <p className="text-green-200 mb-6">
            Thank you for contributing! Your photo has been submitted for moderation 
            and will appear in the game once approved.
          </p>
          <button
            onClick={resetUpload}
            className="px-6 py-3 bg-sky-500 hover:bg-sky-400 text-white rounded-lg font-medium transition-colors"
          >
            Upload Another Photo
          </button>
        </div>
      )}

      {/* Step: Error */}
      {step === 'error' && (
        <div className="bg-red-900/30 border border-red-500/50 rounded-2xl p-8 text-center">
          <div className="w-20 h-20 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-10 h-10 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-white mb-4">Upload Failed</h2>
          <p className="text-red-200 mb-6">{error || 'An unexpected error occurred'}</p>
          <button
            onClick={() => setStep('details')}
            className="px-6 py-3 bg-sky-500 hover:bg-sky-400 text-white rounded-lg font-medium transition-colors"
          >
            Try Again
          </button>
        </div>
      )}

      {/* Info box */}
      <div className="bg-sky-800/20 rounded-xl p-6 border border-sky-700/30">
        <h3 className="text-lg font-semibold text-white mb-4">Photo Guidelines</h3>
        <ul className="space-y-2 text-sky-300">
          <li className="flex items-start gap-2">
            <svg className="w-5 h-5 text-sky-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span>Photos must be taken from an aircraft window</span>
          </li>
          <li className="flex items-start gap-2">
            <svg className="w-5 h-5 text-sky-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span>Airport or surrounding landmarks should be visible</span>
          </li>
          <li className="flex items-start gap-2">
            <svg className="w-5 h-5 text-sky-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span>No people, flight information, or identifying text visible</span>
          </li>
          <li className="flex items-start gap-2">
            <svg className="w-5 h-5 text-sky-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span>All EXIF/GPS data will be automatically removed</span>
          </li>
        </ul>
      </div>
    </div>
  )
}
