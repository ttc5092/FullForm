import React from 'react'

export default function AnalysisModal({ open, onClose, videoUrl, warnings = [], frames = 0, avgAngle = null, minAngle = null, maxAngle = null }) {
  if (!open) return null
  return (
    <div className="analysis-modal">
      <div className="analysis-modal__backdrop" onClick={onClose} />
      <div className="analysis-modal__panel" role="dialog" aria-modal="true">
        <div className="analysis-modal__content">
          <div className="analysis-modal__video-wrap">
            <video src={videoUrl} controls autoPlay muted className="analysis-modal__video" />
          </div>
          <div className="analysis-modal__details">
            <h3>Analysis</h3>
            <div className="analysis-modal__stats">
              <div><strong>Frames checked:</strong> {frames}</div>
              <div><strong>Knee angle (avg/min/max):</strong> {avgAngle ? Math.round(avgAngle) : 'N/A'}° / {minAngle ? Math.round(minAngle) : 'N/A'}° / {maxAngle ? Math.round(maxAngle) : 'N/A'}°</div>
            </div>
            <h4>Warnings</h4>
            <ul className="analysis-modal__list">
              {warnings && warnings.length ? warnings.map((w, i) => (
                <li key={i} className="warn">{w}</li>
              )) : <li className="ok">No warnings detected</li>}
            </ul>
            <div className="analysis-modal__actions">
              <button className="btn btn--solid" onClick={onClose}>Done</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
