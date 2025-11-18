'use client'

import { Mail, Phone, Calendar, Award, Loader2, RefreshCw, Trash2 } from 'lucide-react'
import { useState } from 'react'

interface Candidate {
  id: string
  email: string
  fullName: string
  phone?: string
  skills: string[]
  yearsOfExperience?: number
  score?: number
  scoringDetails?: any
  createdAt: string
}

interface CandidateListProps {
  candidates: Candidate[]
  loading: boolean
  onRefresh: () => void
}

export default function CandidateList({ candidates, loading, onRefresh }: CandidateListProps) {
  const [deleting, setDeleting] = useState<string | null>(null)

  const handleDelete = async (candidateId: string) => {
    if (!confirm('Are you sure you want to delete this candidate? This will remove all associated data including cache and vector database entries.')) {
      return
    }

    setDeleting(candidateId)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/candidates/${candidateId}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error('Failed to delete candidate')
      }

      // Refresh the list
      onRefresh()
    } catch (error) {
      console.error('Error deleting candidate:', error)
      alert('Failed to delete candidate. Please try again.')
    } finally {
      setDeleting(null)
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-12 text-center">
        <Loader2 className="w-12 h-12 text-primary-500 animate-spin mx-auto mb-4" />
        <p className="text-gray-600">Loading candidates...</p>
      </div>
    )
  }

  if (candidates.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-12 text-center">
        <p className="text-gray-600 mb-4">No candidates found</p>
        <p className="text-sm text-gray-500">Upload CVs to get started</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">
          Candidates ({candidates.length})
        </h2>
        <button
          onClick={onRefresh}
          className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 transition-colors"
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      <div className="space-y-4">
        {candidates.map((candidate) => (
          <div
            key={candidate.id}
            className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex justify-between items-start mb-4">
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-xl font-semibold text-gray-900">
                    {candidate.fullName}
                  </h3>
                  <button
                    onClick={() => handleDelete(candidate.id)}
                    disabled={deleting === candidate.id}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-md transition-colors disabled:opacity-50"
                    title="Delete candidate"
                  >
                    {deleting === candidate.id ? (
                      <Loader2 size={18} className="animate-spin" />
                    ) : (
                      <Trash2 size={18} />
                    )}
                  </button>
                </div>
                <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                  <div className="flex items-center gap-1">
                    <Mail size={14} />
                    {candidate.email}
                  </div>
                  {candidate.phone && (
                    <div className="flex items-center gap-1">
                      <Phone size={14} />
                      {candidate.phone}
                    </div>
                  )}
                  {candidate.yearsOfExperience !== undefined && (
                    <div className="flex items-center gap-1">
                      <Calendar size={14} />
                      {candidate.yearsOfExperience} years exp.
                    </div>
                  )}
                </div>
              </div>
              
              {candidate.score !== undefined && candidate.score > 0 && (
                <div className="text-center">
                  <div className="flex items-center justify-center w-16 h-16 rounded-full bg-primary-100 mb-2">
                    <span className="text-xl font-bold text-primary-700">
                      {Math.round(candidate.score)}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500">Score</p>
                </div>
              )}
            </div>

            {/* Skills */}
            {candidate.skills && candidate.skills.length > 0 && (
              <div className="mb-4">
                <p className="text-sm font-medium text-gray-700 mb-2">Skills:</p>
                <div className="flex flex-wrap gap-2">
                  {candidate.skills.slice(0, 10).map((skill, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                    >
                      {skill}
                    </span>
                  ))}
                  {candidate.skills.length > 10 && (
                    <span className="px-3 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                      +{candidate.skills.length - 10} more
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Scoring Details */}
            {candidate.scoringDetails && (
              <div className="mt-4 p-4 bg-gray-50 rounded-md">
                <p className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                  <Award size={16} />
                  Evaluation Breakdown:
                </p>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-3">
                  <div>
                    <p className="text-xs text-gray-500">Job Title Match</p>
                    <p className="text-sm font-semibold text-gray-900">
                      {candidate.scoringDetails.jobTitleScore || 0}%
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Job Description</p>
                    <p className="text-sm font-semibold text-gray-900">
                      {candidate.scoringDetails.jobDescriptionScore || 0}%
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Required Skills</p>
                    <p className="text-sm font-semibold text-gray-900">
                      {candidate.scoringDetails.requiredSkillsScore || candidate.scoringDetails.skillsScore || 0}%
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Preferred Skills</p>
                    <p className="text-sm font-semibold text-gray-900">
                      {candidate.scoringDetails.preferredSkillsScore || 0}%
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Years Experience</p>
                    <p className="text-sm font-semibold text-gray-900">
                      {candidate.scoringDetails.yearsExperienceScore || candidate.scoringDetails.experienceScore || 0}%
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Education</p>
                    <p className="text-sm font-semibold text-gray-900">
                      {candidate.scoringDetails.educationScore || 0}%
                    </p>
                  </div>
                </div>
                {candidate.scoringDetails.reasoning && (
                  <p className="text-sm text-gray-600 italic">
                    "{candidate.scoringDetails.reasoning}"
                  </p>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
