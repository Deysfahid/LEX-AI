import { useState, useRef, useCallback } from 'react'

function UploadZone({ onAnalyze, onDemo }) {
  const [file, setFile] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const [error, setError] = useState(null)
  const inputRef = useRef(null)

  const validateFile = (f) => {
    if (!f) return 'No file selected'
    if (!f.name.toLowerCase().endsWith('.pdf')) return 'Please upload PDF files only'
    if (f.size > 10 * 1024 * 1024) return 'File size must be under 10MB'
    return null
  }

  const handleFile = useCallback((f) => {
    const err = validateFile(f)
    if (err) {
      setError(err)
      setFile(null)
      return
    }
    setError(null)
    setFile(f)
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragActive(false)
    const droppedFile = e.dataTransfer?.files?.[0]
    if (droppedFile) handleFile(droppedFile)
  }, [handleFile])

  const handleDragOver = (e) => {
    e.preventDefault()
    setDragActive(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setDragActive(false)
  }

  const handleChange = (e) => {
    const selected = e.target.files?.[0]
    if (selected) handleFile(selected)
  }

  const handleClick = () => inputRef.current?.click()

  const handleAnalyzeClick = () => {
    if (file) onAnalyze(file)
  }

  return (
    <div className="max-w-2xl mx-auto animate-fade-in">
      {/* Hero */}
      <div className="text-center mb-10">
        <h2 className="text-4xl sm:text-5xl font-extrabold font-['Playfair_Display'] mb-4">
          <span className="gradient-text">Autonomous Legal</span>
          <br />
          Case Analysis
        </h2>
        <p className="text-gray-400 text-lg max-w-lg mx-auto">
          Upload a legal document and let our AI agent perform a comprehensive 9-step analysis with risk scoring, timeline extraction, and actionable recommendations.
        </p>
      </div>

      {/* Upload Area */}
      <div
        onClick={handleClick}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`card-hover cursor-pointer text-center py-12 transition-all duration-300 ${
          dragActive ? 'border-gold-500 bg-gold-500/5 shadow-gold-500/10 shadow-2xl scale-[1.02]' : ''
        } ${file ? 'border-green-500/50 bg-green-500/5' : ''}`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          onChange={handleChange}
          className="hidden"
        />

        {file ? (
          <div className="space-y-4">
            <div className="w-16 h-16 mx-auto bg-green-500/10 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <p className="text-lg font-semibold text-green-400">{file.name}</p>
              <p className="text-gray-500 text-sm mt-1">
                {(file.size / 1024 / 1024).toFixed(2)} MB — Ready to analyze
              </p>
            </div>
            <p className="text-gray-500 text-sm">Click to change file</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="w-16 h-16 mx-auto bg-navy-700 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-gold-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <div>
              <p className="text-lg font-semibold">Drag & drop your PDF here</p>
              <p className="text-gray-500 mt-1">or click to browse files</p>
            </div>
            <p className="text-gray-600 text-sm">PDF files only — Max 10MB</p>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-center text-sm">
          {error}
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 mt-8">
        <button
          onClick={handleAnalyzeClick}
          disabled={!file}
          className={`flex-1 btn-gold text-center ${!file ? 'opacity-40 cursor-not-allowed' : ''}`}
        >
          Analyze Case
        </button>
        <button onClick={onDemo} className="flex-1 btn-outline text-center">
          Try Demo
        </button>
      </div>

      {/* Features */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-12">
        {[
          { icon: '⚖️', title: '9-Step Analysis', desc: 'Deep agentic case analysis' },
          { icon: '🎯', title: 'Risk Scoring', desc: '0-100 risk for each party' },
          { icon: '📋', title: 'PDF Report', desc: 'Downloadable professional report' },
        ].map((f, i) => (
          <div key={i} className="card text-center py-6" style={{ animationDelay: `${i * 0.1}s` }}>
            <span className="text-3xl">{f.icon}</span>
            <p className="font-semibold mt-2">{f.title}</p>
            <p className="text-gray-500 text-sm mt-1">{f.desc}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default UploadZone
