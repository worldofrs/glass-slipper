import { useState } from 'react'
import Markdown from 'react-markdown'
import './App.css'

interface FaceResult {
  name: string | null
  gender: string
  ageRange: { Low: number; High: number }
  emotions: string[]
  smile: boolean
  eyeglasses: boolean
  sunglasses: boolean
  beard: boolean
  mustache: boolean
  eyesOpen: boolean
  mouthOpen: boolean
  pose: { Pitch: number; Roll: number; Yaw: number }
  makeupRecommendations: string
}

interface AnalysisResult {
  filename: string
  faces: FaceResult[]
}

function App() {
  const [showUpload, setShowUpload] = useState(false)
  const [preview, setPreview] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setResults(null)
      setError(null)
      const reader = new FileReader()
      reader.onload = () => setPreview(reader.result as string)
      reader.readAsDataURL(file)
    }
  }

  async function handleSubmit() {
    if (!selectedFile) return

    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await fetch('http://localhost:8000/upload/demo_user', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const detail = await response.json().catch(() => null)
        throw new Error(detail?.detail || `Server error: ${response.status}`)
      }

      const data: AnalysisResult = await response.json()
      setResults(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <img src="/glasslogo.png" alt="GlassSlipper Logo" className="logo" />
      <h1>Upload Your Celeb Inspo</h1>
      <button onClick={() => setShowUpload(true)}>Click Here Gorgeous :)</button>
      {showUpload && (
        <section>
          <input type="file" accept="image/*" onChange={handleFileChange} />
          {preview && <img src={preview} alt="Preview" className="preview" />}
          {selectedFile && !loading && (
            <button className="submit-btn" onClick={handleSubmit}>
              Analyze My Look
            </button>
          )}
          {loading && (
            <div className="loading">
              <div className="spinner" />
              <p>Analyzing your look...</p>
            </div>
          )}
        </section>
      )}

      {error && <div className="error-message">{error}</div>}

      {results && (
        <div className="results-container">
          <h2>Results for {results.filename}</h2>
          {results.faces.length === 0 && <p>No faces detected in the image.</p>}
          {results.faces.map((face, i) => (
            <div key={i} className="face-card">
              <h3>{face.name ? face.name : `Face ${i + 1}`}</h3>
              <ul className="traits-list">
                <li><strong>Gender:</strong> {face.gender}</li>
                <li><strong>Age Range:</strong> {face.ageRange.Low}–{face.ageRange.High}</li>
                <li><strong>Emotions:</strong> {face.emotions.join(', ') || 'None detected'}</li>
                <li><strong>Smile:</strong> {face.smile ? 'Yes' : 'No'}</li>
                <li><strong>Eyeglasses:</strong> {face.eyeglasses ? 'Yes' : 'No'}</li>
                <li><strong>Sunglasses:</strong> {face.sunglasses ? 'Yes' : 'No'}</li>
                <li><strong>Beard:</strong> {face.beard ? 'Yes' : 'No'}</li>
                <li><strong>Mustache:</strong> {face.mustache ? 'Yes' : 'No'}</li>
                <li><strong>Eyes Open:</strong> {face.eyesOpen ? 'Yes' : 'No'}</li>
                <li><strong>Mouth Open:</strong> {face.mouthOpen ? 'Yes' : 'No'}</li>
              </ul>
              <div className="recommendations">
                <h4>Makeup Recommendations</h4>
                <Markdown>{face.makeupRecommendations}</Markdown>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default App
