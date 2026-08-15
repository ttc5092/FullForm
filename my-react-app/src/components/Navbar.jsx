import { useRef, useState } from 'react'
import Button from './Button.jsx'
import logo from '../assets/logofullform.png'
import AnalysisModal from './AnalysisModal'

export default function Navbar() {
  const fileInputRef = useRef(null)
  const [uploading, setUploading] = useState(false)
  const [analysisOpen, setAnalysisOpen] = useState(false)
  const [analysisData, setAnalysisData] = useState(null)
  const [videoUrl, setVideoUrl] = useState(null)

  function handleUploadClick() {
    if (fileInputRef.current) fileInputRef.current.click()
  }

 async function handleFileChange(e) {
    const file = e.target.files && e.target.files[0]
    if (!file) return

    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('video', file)
      formData.append('exercise', 'squats')

      // CHANGED: Use a relative path with the '/api/' prefix for Vercel routing
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      })

      const contentType = response.headers.get('content-type') || ''
      const payload = contentType.includes('application/json') ? await response.json() : null

      if (!response.ok) {
        throw new Error((payload && payload.error) || 'Upload failed')
      }

      const warnings = Array.isArray(payload && payload.warnings) ? payload.warnings : []
      const processedUrl = payload && payload.videoUrl ? payload.videoUrl : URL.createObjectURL(file)

      setVideoUrl(processedUrl)
      setAnalysisData({ warnings, frames: warnings.length || 0, avgAngle: null, minAngle: null, maxAngle: null })
      setAnalysisOpen(true)
    } catch (error) {
      console.error('Upload analysis error:', error)
      // CHANGED: Generic alert message since it will no longer look for localhost:5000 in production
      alert('Upload failed. Please make sure the video is valid and the server is responsive.')
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  return (
    <header className="nav">
      <div className="nav__inner">
        <a className="nav__logo" href="#top">
          <img src={logo} alt="Full Form logo" className="nav__logo-image" />
          <span>FULL FORM</span>
        </a>
        <nav className="nav__links">
          <a href="#how">How it works</a>
          <a href="#feedback">Live feedback</a>
          <a href="#exercises">Exercises</a>
        </nav>
        <Button onClick={handleUploadClick} variant="ghost" size="sm" className="nav__cta">
          {uploading ? 'Uploading...' : 'Upload file'}
        </Button>

        <input
          ref={fileInputRef}
          type="file"
          accept="video/*"
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />
        <AnalysisModal
          open={analysisOpen}
          onClose={() => {
            setAnalysisOpen(false)
            setAnalysisData(null)
            if (videoUrl) {
              try {
                if (videoUrl.startsWith('blob:')) URL.revokeObjectURL(videoUrl)
              } catch (_) {}
              setVideoUrl(null)
            }
          }}
          videoUrl={videoUrl}
          warnings={analysisData && Array.isArray(analysisData.warnings) ? analysisData.warnings : []}
          frames={analysisData && typeof analysisData.frames === 'number' ? analysisData.frames : 0}
          avgAngle={analysisData && analysisData.avgAngle}
          minAngle={analysisData && analysisData.minAngle}
          maxAngle={analysisData && analysisData.maxAngle}
        />
      </div>
    </header>
  )
}
