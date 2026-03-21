import { useState, useEffect } from 'react';
import { listDocuments, getUploadUrl, confirmUpload, deleteDocument } from '../api';

const DOC_TYPES = ['resume', 'portfolio', 'case_study', 'certification', 'pitch_deck', 'other'];

export default function Documents() {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [uploading, setUploading] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [uploadForm, setUploadForm] = useState({ title: '', document_type: 'other', file: null });
  const [actionMsg, setActionMsg] = useState('');

  const flash = (msg) => { setActionMsg(msg); setTimeout(() => setActionMsg(''), 3000); };

  const fetchDocs = async () => {
    setLoading(true);
    try {
      const res = await listDocuments();
      setDocs(res.data);
    } catch (err) {
      if (err.response?.status === 404) {
        setError('Create a marketplace profile first.');
      } else {
        setError(err.response?.data?.detail || 'Failed to load documents');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchDocs(); }, []);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!uploadForm.file) { flash('Select a file'); return; }
    setUploading(true);
    try {
      // Step 1: Get presigned URL
      const urlRes = await getUploadUrl({
        file_name: uploadForm.file.name,
        document_type: uploadForm.document_type,
        mime_type: uploadForm.file.type || 'application/octet-stream',
      });

      // Step 2: Upload to S3
      await fetch(urlRes.data.upload_url, {
        method: 'PUT',
        body: uploadForm.file,
        headers: { 'Content-Type': uploadForm.file.type || 'application/octet-stream' },
      });

      // Step 3: Confirm upload
      await confirmUpload({
        s3_key: urlRes.data.s3_key,
        title: uploadForm.title || uploadForm.file.name,
        document_type: uploadForm.document_type,
        file_name: uploadForm.file.name,
        file_size: uploadForm.file.size,
        mime_type: uploadForm.file.type,
        is_public: true,
      });

      flash('Document uploaded!');
      setShowUpload(false);
      setUploadForm({ title: '', document_type: 'other', file: null });
      await fetchDocs();
    } catch (err) {
      flash('Upload failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId, title) => {
    if (!window.confirm(`Delete "${title}"?`)) return;
    try {
      await deleteDocument(docId);
      setDocs(docs.filter(d => d.id !== docId));
      flash('Document deleted');
    } catch (err) {
      flash('Delete failed');
    }
  };

  if (loading) return <div className="text-center py-12 text-gray-400">Loading documents...</div>;
  if (error) return <div className="text-center py-12 text-red-600">{error}</div>;

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Documents</h2>
        <button onClick={() => setShowUpload(!showUpload)}
          className="text-sm bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          {showUpload ? 'Cancel' : 'Upload Document'}
        </button>
      </div>

      {actionMsg && <div className="bg-blue-50 text-blue-700 text-sm p-2 rounded mb-4">{actionMsg}</div>}

      {/* Upload form */}
      {showUpload && (
        <form onSubmit={handleUpload} className="bg-white border rounded-lg p-4 mb-6 space-y-3">
          <h3 className="font-medium text-sm">Upload New Document</h3>
          <input type="text" placeholder="Document Title" value={uploadForm.title}
            onChange={(e) => setUploadForm({ ...uploadForm, title: e.target.value })}
            className="w-full border rounded px-3 py-2 text-sm" />
          <div className="grid grid-cols-2 gap-3">
            <select value={uploadForm.document_type}
              onChange={(e) => setUploadForm({ ...uploadForm, document_type: e.target.value })}
              className="border rounded px-3 py-2 text-sm">
              {DOC_TYPES.map(t => (
                <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>
              ))}
            </select>
            <input type="file"
              onChange={(e) => setUploadForm({ ...uploadForm, file: e.target.files[0] })}
              className="text-sm" />
          </div>
          <button type="submit" disabled={uploading}
            className="bg-blue-600 text-white px-4 py-2 rounded text-sm disabled:opacity-50">
            {uploading ? 'Uploading...' : 'Upload'}
          </button>
        </form>
      )}

      {/* Document list */}
      {docs.length === 0 ? (
        <div className="text-center py-8 text-gray-400 border rounded-lg bg-white">
          <p>No documents yet.</p>
          <p className="text-xs mt-1">Upload resumes, portfolios, case studies, or certifications.</p>
        </div>
      ) : (
        <div className="bg-white border rounded-lg divide-y">
          {docs.map(doc => (
            <div key={doc.id} className="p-4 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">{doc.title}</p>
                <div className="flex gap-3 mt-1 text-xs text-gray-400">
                  <span className="bg-gray-100 px-1.5 py-0.5 rounded">{doc.document_type || 'other'}</span>
                  {doc.mime_type && <span>{doc.mime_type}</span>}
                  {doc.file_size && <span>{(doc.file_size / 1024).toFixed(0)} KB</span>}
                  <span>{doc.is_public ? 'Public' : 'Private'}</span>
                </div>
              </div>
              <button onClick={() => handleDelete(doc.id, doc.title)}
                className="text-xs text-red-600 hover:text-red-800">
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
