'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import axios from 'axios'
import { Upload, CheckCircle, XCircle, Loader2 } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001'

interface CVUploadProps {
  onUploadSuccess: () => void
}

export default function CVUpload({ onUploadSuccess }: CVUploadProps) {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [formData, setFormData] = useState({
    email: '',
    fullName: '',
    phone: '',
  })

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return
    
    const file = acceptedFiles[0]
    
    if (!formData.email || !formData.fullName) {
      setMessage({ type: 'error', text: 'Please fill in email and full name' })
      return
    }

    setLoading(true)
    setMessage(null)

    try {
      const uploadFormData = new FormData()
      uploadFormData.append('file', file)
      uploadFormData.append('email', formData.email)
      uploadFormData.append('fullName', formData.fullName)
      if (formData.phone) {
        uploadFormData.append('phone', formData.phone)
      }

      await axios.post(`${API_URL}/api/candidates/upload`, uploadFormData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setMessage({ type: 'success', text: 'CV uploaded and parsed successfully!' })
      setFormData({ email: '', fullName: '', phone: '' })
      setTimeout(() => {
        onUploadSuccess()
      }, 1500)
    } catch (error: any) {
      setMessage({
        type: 'error',
        text: error.response?.data?.message || 'Failed to upload CV',
      })
    } finally {
      setLoading(false)
    }
  }, [formData, onUploadSuccess])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxFiles: 1,
    disabled: loading,
  })

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Upload Candidate CV</h2>

      <div className="space-y-6">
        {/* Form Fields */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Address *
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="candidate@example.com"
              disabled={loading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Full Name *
            </label>
            <input
              type="text"
              value={formData.fullName}
              onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="John Doe"
              disabled={loading}
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Phone Number (Optional)
            </label>
            <input
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="+1 234 567 8900"
              disabled={loading}
            />
          </div>
        </div>

        {/* Dropzone */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all ${
            isDragActive
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-300 hover:border-primary-400'
          } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center">
            {loading ? (
              <>
                <Loader2 className="w-12 h-12 text-primary-500 animate-spin mb-4" />
                <p className="text-gray-600">Processing CV...</p>
              </>
            ) : (
              <>
                <Upload className="w-12 h-12 text-gray-400 mb-4" />
                {isDragActive ? (
                  <p className="text-primary-600 font-medium">Drop the CV here</p>
                ) : (
                  <>
                    <p className="text-gray-700 font-medium mb-2">
                      Drag & drop CV here, or click to select
                    </p>
                    <p className="text-sm text-gray-500">Supports PDF and DOCX files</p>
                  </>
                )}
              </>
            )}
          </div>
        </div>

        {/* Message */}
        {message && (
          <div
            className={`flex items-center gap-2 p-4 rounded-md ${
              message.type === 'success'
                ? 'bg-green-50 text-green-800'
                : 'bg-red-50 text-red-800'
            }`}
          >
            {message.type === 'success' ? (
              <CheckCircle className="w-5 h-5" />
            ) : (
              <XCircle className="w-5 h-5" />
            )}
            <p>{message.text}</p>
          </div>
        )}
      </div>
    </div>
  )
}
