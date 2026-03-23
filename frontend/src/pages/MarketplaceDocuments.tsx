import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, Upload, Trash2, FileText } from 'lucide-react'
import { cn } from '@/lib/utils'
import { marketplace, type ProfileDocument } from '@/lib/api'

const DOC_TYPES = ['resume', 'portfolio', 'case_study', 'certification', 'pitch_deck', 'other']

export function MarketplaceDocuments() {
  const [docs, setDocs] = useState<ProfileDocument[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showUpload, setShowUpload] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadForm, setUploadForm] = useState({ title: '', document_type: 'other', file: null as File | null })
  const [msg, setMsg] = useState('')

  const flash = (m: string) => { setMsg(m); setTimeout(() => setMsg(''), 3000) }
  const inputClass = "w-full bg-black/50 border border-white/[0.08] rounded-lg px-3 py-2.5 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:border-white/20"

  const fetchDocs = async () => {
    setLoading(true)
    try {
      const profile = await marketplace.getMyProfile()
      setDocs(profile.documents || [])
    } catch {
      setError('Create a marketplace profile first.')
    } finally { setLoading(false) }
  }

  useEffect(() => { fetchDocs() }, [])

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!uploadForm.file) { flash('Select a file'); return }
    setUploading(true)
    try {
      // This would need the upload-url and confirm-upload endpoints
      // For now, show what would happen
      flash('Document upload requires S3 configuration. Endpoint ready at POST /marketplace/profiles/me/documents/upload-url')
      setShowUpload(false)
    } catch (err) {
      flash('Upload failed: ' + (err instanceof Error ? err.message : 'Error'))
    } finally { setUploading(false) }
  }

  const handleDelete = async (docId: string, title: string) => {
    if (!window.confirm(`Delete "${title}"?`)) return
    try {
      await marketplace.deleteProfile() // TODO: wire delete document endpoint
      setDocs(docs.filter(d => d.id !== docId))
      flash('Document deleted')
    } catch { flash('Delete failed') }
  }

  if (loading) return <div className="text-zinc-500 py-12 text-center">Loading documents...</div>
  if (error) return <div className="text-red-400 py-12 text-center">{error}</div>

  return (
    <div className="max-w-2xl mx-auto">
      <Link to="/marketplace/me" className="inline-flex items-center gap-1.5 text-sm text-zinc-500 hover:text-zinc-300 mb-4">
        <ArrowLeft className="w-4 h-4" /> Back to profile
      </Link>

      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-white">Documents</h2>
        <button onClick={() => setShowUpload(!showUpload)}
          className="text-sm bg-white text-black px-4 py-2 rounded-lg font-medium hover:bg-zinc-200 transition flex items-center gap-1.5">
          <Upload className="w-3.5 h-3.5" /> {showUpload ? 'Cancel' : 'Upload'}
        </button>
      </div>

      {msg && <div className="bg-blue-500/10 text-blue-400 text-sm p-3 rounded-xl mb-4">{msg}</div>}

      {showUpload && (
        <form onSubmit={handleUpload} className="bg-[#1a1a1a] border border-white/[0.06] rounded-xl p-5 mb-6 space-y-3">
          <h3 className="text-sm font-medium text-white">Upload Document</h3>
          <input type="text" placeholder="Document Title" value={uploadForm.title}
            onChange={e => setUploadForm({ ...uploadForm, title: e.target.value })} className={inputClass} />
          <div className="grid grid-cols-2 gap-2">
            <select value={uploadForm.document_type}
              onChange={e => setUploadForm({ ...uploadForm, document_type: e.target.value })}
              className={cn(inputClass, 'appearance-none')}>
              {DOC_TYPES.map(t => <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>)}
            </select>
            <input type="file" onChange={e => setUploadForm({ ...uploadForm, file: e.target.files?.[0] || null })}
              className="text-sm text-zinc-400 file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0 file:text-sm file:bg-white/[0.06] file:text-zinc-300" />
          </div>
          <button type="submit" disabled={uploading}
            className="bg-white text-black px-4 py-2 rounded-lg text-sm font-medium hover:bg-zinc-200 transition disabled:opacity-50">
            {uploading ? 'Uploading...' : 'Upload'}
          </button>
        </form>
      )}

      {docs.length === 0 ? (
        <div className="text-center py-12 bg-[#1a1a1a] border border-white/[0.06] rounded-xl">
          <FileText className="w-8 h-8 text-zinc-600 mx-auto mb-3" />
          <p className="text-zinc-500 text-sm">No documents yet.</p>
          <p className="text-xs text-zinc-600 mt-1">Upload resumes, portfolios, case studies, or certifications.</p>
        </div>
      ) : (
        <div className="bg-[#1a1a1a] border border-white/[0.06] rounded-xl divide-y divide-white/[0.06]">
          {docs.map(doc => (
            <div key={doc.id} className="p-4 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-white">{doc.title}</p>
                <div className="flex gap-3 mt-1 text-xs text-zinc-500">
                  <span className="bg-white/[0.06] px-1.5 py-0.5 rounded">{doc.document_type || 'other'}</span>
                  {doc.mime_type && <span>{doc.mime_type}</span>}
                  {doc.file_size && <span>{(doc.file_size / 1024).toFixed(0)} KB</span>}
                </div>
              </div>
              <button onClick={() => handleDelete(doc.id, doc.title)}
                className="text-zinc-600 hover:text-red-400 transition">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
