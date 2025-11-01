export type ExtractionStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface Candidate {
  document_requests: string;
  company: string;
  documents: {};
  updated_at: string | number | Date;
  created_at: string | number | Date;
  status: string | null | undefined;
  id: string;
  name: string | null;
  email: string | null;
  phone: string | null;
  curr_company: string | null;
  designation: string | null;
  parsed_data: string | null;
  skills: string[];
  extractionStatus: ExtractionStatus;
  updatedAt: string;
}

export interface ConfidenceScores {
  name?: number;
  email?: number;
  phone?: number;
  company?: number;
  designation?: number;
  skills?: number;
}

export interface CandidateProfileData {
  candidate: Candidate;
  confidence: ConfidenceScores;
  resumeUrl?: string;
}


