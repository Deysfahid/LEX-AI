import { useState } from 'react'
import RiskScore from './RiskScore'
import Timeline from './Timeline'
import Insights from './Insights'
import ReportButton from './ReportButton'

function Dashboard({ data, isDemo, onReset }) {
  const classification = data?.classification || {}
  const summary = data?.summary || {}
  const riskAnalysis = data?.risk_analysis || {}
  const timeline = data?.timeline?.timeline || []

  return (
    <div className="space-y-8 animate-fade-in">
      {isDemo && (
        <div className="p-3 bg-gold-500/10 border border-gold-500/30 rounded-lg text-gold-400 text-center text-sm">
          {data?._demo_note || 'Demo Mode — Showing analysis of an Indian property dispute case. Upload a real document for actual analysis.'}
        </div>
      )}

      {/* Top Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <span className="px-3 py-1 bg-gold-500/10 border border-gold-500/30 rounded-full text-gold-400 text-sm font-medium">
              {classification.case_type || 'N/A'}
            </span>
            <span className="text-gray-500 text-sm">
              Confidence: {classification.confidence || 0}%
            </span>
          </div>
          <h2 className="text-2xl font-bold mt-2 font-['Playfair_Display']">Analysis Results</h2>
        </div>
        <ReportButton analysis={data} />
      </div>

      {/* Summary Card */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gold-400 mb-3">Case Summary</h3>
        <p className="text-gray-300 leading-relaxed">{summary.summary || 'N/A'}</p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6 pt-4 border-t border-navy-600">
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">What Happened</p>
            <p className="text-sm text-gray-300">{summary.what_happened || 'N/A'}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Parties Involved</p>
            <p className="text-sm text-gray-300">{summary.parties_involved || 'N/A'}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Dispute</p>
            <p className="text-sm text-gray-300">{summary.dispute || 'N/A'}</p>
          </div>
        </div>
      </div>

      {/* Risk Scores */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <RiskScore
          title="Plaintiff"
          data={riskAnalysis.plaintiff_risk}
          name={data?.parties?.plaintiff}
        />
        <RiskScore
          title="Defendant"
          data={riskAnalysis.defendant_risk}
          name={data?.parties?.defendant}
        />
      </div>

      {/* Timeline */}
      <Timeline events={timeline} />

      {/* Insights Tabs */}
      <Insights data={data} />
    </div>
  )
}

export default Dashboard
