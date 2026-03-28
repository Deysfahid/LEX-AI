import { useState, useCallback } from 'react'
import UploadZone from './components/UploadZone'
import Dashboard from './components/Dashboard'

const STEP_LABELS = [
  { icon: '🔍', label: 'Classifying case type...' },
  { icon: '📝', label: 'Summarizing the case...' },
  { icon: '⚖️', label: 'Extracting legal issues...' },
  { icon: '👥', label: 'Identifying parties...' },
  { icon: '📅', label: 'Building timeline...' },
  { icon: '🎯', label: 'Calculating risk scores...' },
  { icon: '🔎', label: 'Finding evidence gaps...' },
  { icon: '💡', label: 'Generating recommendations...' },
  { icon: '📚', label: 'Searching similar cases...' },
]

function App() {
  const [appState, setAppState] = useState('UPLOAD') // UPLOAD | ANALYZING | RESULTS
  const [analysisData, setAnalysisData] = useState(null)
  const [currentStep, setCurrentStep] = useState(0)
  const [error, setError] = useState(null)
  const [isDemo, setIsDemo] = useState(false)
  const [lastAction, setLastAction] = useState(null)
  const [activeController, setActiveController] = useState(null)

  const parseEventData = (eventBlock) => {
    const dataLines = eventBlock
      .split('\n')
      .filter((line) => line.startsWith('data: '))
      .map((line) => line.slice(6))

    if (!dataLines.length) return null
    return JSON.parse(dataLines.join('\n'))
  }

  const runUploadAnalysis = useCallback(async (file, signal) => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch('/analyze-stream-upload', {
      method: 'POST',
      body: formData,
      signal,
    })

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}))
      const message = errData?.error?.message || errData.detail || 'Analysis failed, please try again'
      throw new Error(message)
    }

    if (!response.body) {
      throw new Error('No stream received from server')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let hasResult = false

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const events = buffer.split('\n\n')
      buffer = events.pop() || ''

      for (const eventBlock of events) {
        const trimmed = eventBlock.trim()
        if (!trimmed) continue

        const data = parseEventData(trimmed)
        if (!data) continue

        if (data.step === -1) {
          throw new Error(data.label || 'Analysis failed')
        }

        if (data.step) {
          setCurrentStep(data.step)
        }

        if (data.result) {
          hasResult = true
          setIsDemo(data.result?._mode === 'demo')
          setAnalysisData(data.result)
          setAppState('RESULTS')
          return
        }
      }
    }

    if (!hasResult) {
      throw new Error('Analysis stream ended before returning a result')
    }
  }, [])

  const handleAnalyze = useCallback(async (file) => {
    setAppState('ANALYZING')
    setCurrentStep(0)
    setError(null)
    setIsDemo(false)
    setLastAction({ type: 'file', file })

    const controller = new AbortController()
    setActiveController(controller)

    try {
      await runUploadAnalysis(file, controller.signal)
    } catch (err) {
      if (err.name === 'AbortError') {
        setError('Analysis cancelled.')
      } else {
        console.error('Analysis error:', err)
        setError(err.message || 'Analysis failed, please try again')
      }
      setAppState('UPLOAD')
    } finally {
      setActiveController(null)
    }
  }, [runUploadAnalysis])

  const handleDemo = useCallback(async () => {
    setAppState('ANALYZING')
    setCurrentStep(0)
    setError(null)
    setIsDemo(true)
    setLastAction({ type: 'demo' })

    const controller = new AbortController()
    setActiveController(controller)

    try {
      const response = await fetch('/demo', { signal: controller.signal })
      if (!response.ok) {
        throw new Error('Failed to load demo data')
      }
      const demoData = await response.json()

      for (let i = 1; i <= 9; i++) {
        await new Promise(resolve => setTimeout(resolve, 800))
        if (controller.signal.aborted) {
          throw new DOMException('Cancelled', 'AbortError')
        }
        setCurrentStep(i)
      }

      setAnalysisData(demoData)
      setAppState('RESULTS')
    } catch (err) {
      if (err.name === 'AbortError') {
        setError('Analysis cancelled.')
      } else {
        setError('Failed to load demo data')
      }
      setAppState('UPLOAD')
    } finally {
      setActiveController(null)
    }
  }, [])

  const handleCancel = useCallback(() => {
    if (activeController) {
      activeController.abort()
    }
  }, [activeController])

  const handleRetry = useCallback(() => {
    if (!lastAction) return
    if (lastAction.type === 'file' && lastAction.file) {
      handleAnalyze(lastAction.file)
      return
    }
    if (lastAction.type === 'demo') {
      handleDemo()
    }
  }, [lastAction, handleAnalyze, handleDemo])

  const handleReset = useCallback(() => {
    if (activeController) {
      activeController.abort()
    }
    setAppState('UPLOAD')
    setAnalysisData(null)
    setCurrentStep(0)
    setError(null)
    setIsDemo(false)
    setActiveController(null)
  }, [activeController])

  return (
    <div className="min-h-screen bg-navy-900">
      {/* Header */}
      <header className="border-b border-navy-600/50 bg-navy-900/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <button onClick={handleReset} className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-gold-400 to-gold-600 flex items-center justify-center shadow-lg shadow-gold-500/30 group-hover:shadow-gold-500/50 transition-shadow">
              <span className="text-navy-900 font-bold text-xl font-['Playfair_Display']">L</span>
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">
                <span className="gradient-text font-['Playfair_Display']">LexAI</span>
              </h1>
              <p className="text-[10px] text-gray-500 tracking-widest uppercase">Agentic Legal Analysis</p>
            </div>
          </button>
          {appState === 'RESULTS' && (
            <button onClick={handleReset} className="btn-outline text-sm">
              New Analysis
            </button>
          )}
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 animate-fade-in">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <span>{error}</span>
              {lastAction && (
                <button onClick={handleRetry} className="btn-outline text-sm self-start sm:self-auto">
                  Retry
                </button>
              )}
            </div>
          </div>
        )}

        {appState === 'UPLOAD' && (
          <UploadZone onAnalyze={handleAnalyze} onDemo={handleDemo} />
        )}

        {appState === 'ANALYZING' && (
          <div className="max-w-2xl mx-auto animate-fade-in">
            <div className="text-center mb-10">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gold-500/10 border border-gold-500/30 text-gold-400 text-sm mb-6">
                <div className="w-2 h-2 rounded-full bg-gold-500 animate-pulse"></div>
                {isDemo ? 'Running Demo Analysis' : 'Agent Running'}
              </div>
              <h2 className="text-3xl font-bold font-['Playfair_Display'] mb-2">Analyzing Your Case</h2>
              <p className="text-gray-400">Our AI agent is performing a 9-step deep analysis</p>
            </div>

            <div className="card space-y-3">
              {STEP_LABELS.map((step, idx) => {
                const stepNum = idx + 1
                let statusClass = 'step-pending'
                if (stepNum < currentStep) statusClass = 'step-done'
                else if (stepNum === currentStep) statusClass = 'step-active'

                return (
                  <div
                    key={idx}
                    className={`flex items-center gap-4 p-4 rounded-lg border transition-all duration-500 ${statusClass}`}
                  >
                    <span className="text-2xl">{step.icon}</span>
                    <span className="font-medium flex-1">{step.label}</span>
                    {stepNum < currentStep && (
                      <svg className="w-5 h-5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    )}
                    {stepNum === currentStep && (
                      <div className="w-5 h-5 border-2 border-gold-500 border-t-transparent rounded-full animate-spin"></div>
                    )}
                  </div>
                )
              })}
            </div>

            <div className="mt-5 flex justify-center">
              <button onClick={handleCancel} className="btn-outline text-sm">
                Cancel Analysis
              </button>
            </div>
          </div>
        )}

        {appState === 'RESULTS' && analysisData && (
          <Dashboard data={analysisData} isDemo={isDemo} onReset={handleReset} />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-navy-600/30 mt-16 py-8 text-center text-gray-600 text-sm">
        <p>LexAI — Agentic AI for Autonomous Legal Case Analysis</p>
        <p className="mt-1 text-xs">For informational purposes only. Not legal advice.</p>
      </footer>
    </div>
  )
}

export default App
