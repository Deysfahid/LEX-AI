import { useState } from 'react'

const TABS = [
  'Summary',
  'Key Issues',
  'Parties Involved',
  'Missing Evidence',
  'Recommendations',
  'Similar Cases',
]

function Insights({ data }) {
  const [activeTab, setActiveTab] = useState(0)

  const summary = data?.summary || {}
  const keyIssues = data?.key_issues?.issues || []
  const parties = data?.parties || {}
  const missing = data?.missing_evidence || {}
  const recommendations = data?.recommendations?.recommendations || []
  const similarCases = data?.similar_cases?.similar_cases || []

  const renderContent = () => {
    switch (activeTab) {
      case 0: // Summary
        return (
          <div className="space-y-4">
            <div>
              <h4 className="text-sm font-semibold text-gold-400 mb-2">Overview</h4>
              <p className="text-gray-300 leading-relaxed">{summary.summary || 'N/A'}</p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 border-t border-navy-600">
              <div className="p-4 bg-navy-700/50 rounded-lg">
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">What Happened</p>
                <p className="text-sm text-gray-300">{summary.what_happened || 'N/A'}</p>
              </div>
              <div className="p-4 bg-navy-700/50 rounded-lg">
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Parties Involved</p>
                <p className="text-sm text-gray-300">{summary.parties_involved || 'N/A'}</p>
              </div>
              <div className="p-4 bg-navy-700/50 rounded-lg">
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Core Dispute</p>
                <p className="text-sm text-gray-300">{summary.dispute || 'N/A'}</p>
              </div>
            </div>
          </div>
        )

      case 1: // Key Issues
        return (
          <div className="space-y-3">
            {keyIssues.length > 0 ? (
              keyIssues.map((issue, idx) => (
                <div key={idx} className="flex items-start gap-3 p-3 bg-navy-700/30 rounded-lg">
                  <span className="w-7 h-7 flex-shrink-0 bg-gold-500/10 text-gold-400 rounded-full flex items-center justify-center text-sm font-bold">
                    {idx + 1}
                  </span>
                  <p className="text-gray-300 text-sm leading-relaxed">{issue}</p>
                </div>
              ))
            ) : (
              <p className="text-gray-500">No key issues identified.</p>
            )}
          </div>
        )

      case 2: // Parties
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-4 bg-navy-700/30 rounded-lg border-l-4 border-blue-500">
                <p className="text-xs text-blue-400 uppercase tracking-wider mb-1">Plaintiff</p>
                <p className="text-white font-medium">{parties.plaintiff || 'N/A'}</p>
              </div>
              <div className="p-4 bg-navy-700/30 rounded-lg border-l-4 border-red-500">
                <p className="text-xs text-red-400 uppercase tracking-wider mb-1">Defendant</p>
                <p className="text-white font-medium">{parties.defendant || 'N/A'}</p>
              </div>
            </div>
            <div className="p-4 bg-navy-700/30 rounded-lg">
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Legal Representatives</p>
              {parties.lawyers && parties.lawyers.length > 0 ? (
                <div className="space-y-1">
                  {parties.lawyers.map((lawyer, idx) => (
                    <p key={idx} className="text-gray-300 text-sm">{lawyer}</p>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-sm">No lawyers identified.</p>
              )}
            </div>
            <div className="p-4 bg-navy-700/30 rounded-lg">
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Presiding Judge</p>
              <p className="text-gray-300 text-sm">{parties.judge || 'Not mentioned'}</p>
            </div>
          </div>
        )

      case 3: // Missing Evidence
        return (
          <div className="space-y-6">
            {missing.missing_documents && missing.missing_documents.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-red-400 mb-3">Missing Documents</h4>
                <div className="space-y-2">
                  {missing.missing_documents.map((doc, idx) => (
                    <div key={idx} className="flex items-start gap-2 text-sm">
                      <span className="text-red-400 mt-0.5">✗</span>
                      <p className="text-gray-300">{doc}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {missing.weak_arguments && missing.weak_arguments.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-yellow-400 mb-3">Weak Arguments</h4>
                <div className="space-y-2">
                  {missing.weak_arguments.map((arg, idx) => (
                    <div key={idx} className="flex items-start gap-2 text-sm">
                      <span className="text-yellow-400 mt-0.5">⚠</span>
                      <p className="text-gray-300">{arg}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {missing.gaps && missing.gaps.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-orange-400 mb-3">Case Gaps</h4>
                <div className="space-y-2">
                  {missing.gaps.map((gap, idx) => (
                    <div key={idx} className="flex items-start gap-2 text-sm">
                      <span className="text-orange-400 mt-0.5">→</span>
                      <p className="text-gray-300">{gap}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )

      case 4: // Recommendations
        return (
          <div className="space-y-3">
            {recommendations.length > 0 ? (
              recommendations.map((rec, idx) => (
                <div key={idx} className="flex items-start gap-3 p-3 bg-green-500/5 border border-green-500/10 rounded-lg">
                  <span className="w-7 h-7 flex-shrink-0 bg-green-500/10 text-green-400 rounded-full flex items-center justify-center text-sm">
                    💡
                  </span>
                  <p className="text-gray-300 text-sm leading-relaxed">{rec}</p>
                </div>
              ))
            ) : (
              <p className="text-gray-500">No recommendations available.</p>
            )}
          </div>
        )

      case 5: // Similar Cases
        return (
          <div className="space-y-4">
            {similarCases.length > 0 ? (
              similarCases.map((c, idx) => (
                <div key={idx} className="p-4 bg-navy-700/30 rounded-lg border border-navy-600/50">
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="text-sm font-semibold text-white">{c.name}</h4>
                    <span className="text-xs px-2 py-0.5 bg-gold-500/10 text-gold-400 rounded-full flex-shrink-0">
                      {c.year}
                    </span>
                  </div>
                  <p className="text-gray-400 text-sm mt-2"><span className="text-gray-500">Outcome:</span> {c.outcome}</p>
                  <p className="text-gray-400 text-sm mt-1"><span className="text-gray-500">Relevance:</span> {c.relevance}</p>
                </div>
              ))
            ) : (
              <p className="text-gray-500">No similar cases identified.</p>
            )}
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gold-400 mb-4">Detailed Insights</h3>

      {/* Tab Navigation */}
      <div className="flex flex-wrap gap-2 mb-6 border-b border-navy-600 pb-4">
        {TABS.map((tab, idx) => (
          <button
            key={idx}
            onClick={() => setActiveTab(idx)}
            className={`px-3 py-1.5 text-sm rounded-lg transition-all duration-200 ${
              activeTab === idx
                ? 'bg-gold-500/10 text-gold-400 border border-gold-500/30'
                : 'text-gray-500 hover:text-gray-300 hover:bg-navy-700'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="animate-fade-in" key={activeTab}>
        {renderContent()}
      </div>
    </div>
  )
}

export default Insights
