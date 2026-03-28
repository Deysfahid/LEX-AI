import { useEffect, useState } from 'react'

function RiskScore({ title, data, name }) {
  const score = data?.score || 0
  const reasoning = data?.reasoning || 'No analysis available.'
  const [animatedScore, setAnimatedScore] = useState(0)

  useEffect(() => {
    let start = 0
    const duration = 1500
    const startTime = Date.now()

    const animate = () => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      setAnimatedScore(Math.round(eased * score))
      if (progress < 1) requestAnimationFrame(animate)
    }

    requestAnimationFrame(animate)
  }, [score])

  const getColor = (s) => {
    if (s <= 30) return { stroke: '#22c55e', bg: 'bg-green-500/10', text: 'text-green-400', label: 'Low Risk' }
    if (s <= 60) return { stroke: '#eab308', bg: 'bg-yellow-500/10', text: 'text-yellow-400', label: 'Medium Risk' }
    return { stroke: '#ef4444', bg: 'bg-red-500/10', text: 'text-red-400', label: 'High Risk' }
  }

  const color = getColor(score)
  const circumference = 2 * Math.PI * 45
  const offset = circumference - (animatedScore / 100) * circumference

  return (
    <div className="card-hover">
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wider">{title}</p>
          <p className="text-sm font-medium text-gray-300 truncate max-w-[200px]">{name || 'N/A'}</p>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${color.bg} ${color.text}`}>
          {color.label}
        </span>
      </div>

      <div className="flex items-center gap-6">
        <div className="relative w-28 h-28 flex-shrink-0">
          <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
            <circle
              cx="50" cy="50" r="45"
              fill="none"
              stroke="#1c2541"
              strokeWidth="8"
            />
            <circle
              cx="50" cy="50" r="45"
              fill="none"
              stroke={color.stroke}
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              className="transition-all duration-100"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className={`text-2xl font-bold ${color.text}`}>{animatedScore}</span>
          </div>
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm text-gray-400 leading-relaxed">{reasoning}</p>
        </div>
      </div>
    </div>
  )
}

export default RiskScore
