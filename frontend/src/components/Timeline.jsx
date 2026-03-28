function Timeline({ events }) {
  if (!events || events.length === 0) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-gold-400 mb-4">Case Timeline</h3>
        <p className="text-gray-500">No timeline data available.</p>
      </div>
    )
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gold-400 mb-6">Case Timeline</h3>
      <div className="relative">
        {/* Center Line */}
        <div className="absolute left-1/2 transform -translate-x-1/2 w-0.5 h-full bg-navy-600 hidden md:block"></div>
        {/* Mobile Line */}
        <div className="absolute left-6 top-0 w-0.5 h-full bg-navy-600 md:hidden"></div>

        {events.map((item, idx) => {
          const isLeft = idx % 2 === 0

          return (
            <div key={idx} className="relative mb-8 last:mb-0">
              {/* Desktop Layout */}
              <div className="hidden md:grid grid-cols-2 gap-8">
                {isLeft ? (
                  <>
                    <div className="text-right animate-slide-up" style={{ animationDelay: `${idx * 0.1}s` }}>
                      <div className="card-hover inline-block text-right">
                        <p className="text-gold-400 font-semibold text-sm">{item.date}</p>
                        <p className="text-gray-300 text-sm mt-1">{item.event}</p>
                      </div>
                    </div>
                    <div></div>
                  </>
                ) : (
                  <>
                    <div></div>
                    <div className="animate-slide-up" style={{ animationDelay: `${idx * 0.1}s` }}>
                      <div className="card-hover inline-block">
                        <p className="text-gold-400 font-semibold text-sm">{item.date}</p>
                        <p className="text-gray-300 text-sm mt-1">{item.event}</p>
                      </div>
                    </div>
                  </>
                )}
              </div>

              {/* Center Node */}
              <div className="hidden md:flex absolute left-1/2 top-4 transform -translate-x-1/2 -translate-y-0">
                <div className="w-4 h-4 rounded-full bg-gold-500 border-4 border-navy-800 shadow-lg shadow-gold-500/30 z-10"></div>
              </div>

              {/* Mobile Layout */}
              <div className="md:hidden flex items-start gap-4 pl-2 animate-slide-up" style={{ animationDelay: `${idx * 0.1}s` }}>
                <div className="w-3 h-3 rounded-full bg-gold-500 border-3 border-navy-800 mt-2 flex-shrink-0 z-10 shadow-lg shadow-gold-500/30"></div>
                <div className="card-hover flex-1">
                  <p className="text-gold-400 font-semibold text-sm">{item.date}</p>
                  <p className="text-gray-300 text-sm mt-1">{item.event}</p>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default Timeline
