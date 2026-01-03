import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { TailorForm } from '../components/TailorForm'
import { ProcessingView } from '../components/ProcessingView'
import { ResultsView } from '../components/ResultsView'
import { JobStatus } from '../types'

describe('TailorForm', () => {
  it('renders all input fields', () => {
    render(<TailorForm onSubmit={() => {}} error={null} />)

    expect(screen.getByLabelText(/Your Resume/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Job Description/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Company Name/i)).toBeInTheDocument()
  })

  it('shows error message when error prop is provided', () => {
    render(<TailorForm onSubmit={() => {}} error="Something went wrong" />)

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
  })

  it('disables submit button when fields are empty', () => {
    render(<TailorForm onSubmit={() => {}} error={null} />)

    const button = screen.getByRole('button', { name: /Tailor My Resume/i })
    expect(button).toBeDisabled()
  })

  it('enables submit button when required fields are filled', () => {
    render(<TailorForm onSubmit={() => {}} error={null} />)

    fireEvent.change(screen.getByLabelText(/Your Resume/i), {
      target: { value: '# My Resume' },
    })
    fireEvent.change(screen.getByLabelText(/Job Description/i), {
      target: { value: 'Software Engineer position' },
    })

    const button = screen.getByRole('button', { name: /Tailor My Resume/i })
    expect(button).not.toBeDisabled()
  })

  it('calls onSubmit with form data when submitted', () => {
    const onSubmit = vi.fn()
    render(<TailorForm onSubmit={onSubmit} error={null} />)

    fireEvent.change(screen.getByLabelText(/Your Resume/i), {
      target: { value: '# My Resume' },
    })
    fireEvent.change(screen.getByLabelText(/Job Description/i), {
      target: { value: 'Software Engineer position' },
    })
    fireEvent.click(screen.getByRole('button', { name: /Tailor My Resume/i }))

    expect(onSubmit).toHaveBeenCalledWith({
      resume_text: '# My Resume',
      job_description: 'Software Engineer position',
      company_name: undefined,
    })
  })
})

describe('ProcessingView', () => {
  it('shows processing status', () => {
    const status: JobStatus = {
      job_id: '123',
      status: 'processing',
      current_step: 2,
      total_steps: 5,
      step_description: 'Parsing resume...',
      result: null,
      error: null,
    }

    render(<ProcessingView status={status} />)

    expect(screen.getByText('Tailoring Your Resume')).toBeInTheDocument()
    expect(screen.getByText('Parsing resume...')).toBeInTheDocument()
    expect(screen.getByText('Step 2 of 5')).toBeInTheDocument()
  })

  it('shows all step labels', () => {
    render(<ProcessingView status={null} />)

    expect(screen.getByText('Analyzing job description')).toBeInTheDocument()
    expect(screen.getByText('Parsing resume')).toBeInTheDocument()
    expect(screen.getByText('Matching experience to requirements')).toBeInTheDocument()
    expect(screen.getByText('Calculating fit score')).toBeInTheDocument()
    expect(screen.getByText('Tailoring resume content')).toBeInTheDocument()
  })
})

describe('ResultsView', () => {
  const mockStatus: JobStatus = {
    job_id: '123',
    status: 'completed',
    current_step: 5,
    total_steps: 5,
    step_description: 'Complete!',
    result: {
      fit_score: 0.85,
      keywords_matched: 12,
      keywords_total: 15,
      gaps: ['Need more cloud experience'],
      strengths: ['Strong Python skills'],
      talking_points: ['Discuss leadership experience'],
      seniority_fit: 'match',
      job_title: 'Software Engineer',
      company: 'Acme Corp',
      docx_filename: 'resume_acme_20240101.docx',
      tailored_summary: 'Experienced engineer...',
      bullets_rewritten: 8,
      keywords_added: ['AWS', 'Docker'],
    },
    error: null,
  }

  it('displays the match score', () => {
    render(<ResultsView status={mockStatus} onReset={() => {}} />)

    expect(screen.getByText('85%')).toBeInTheDocument()
    expect(screen.getByText('Match Score')).toBeInTheDocument()
  })

  it('displays job title and company', () => {
    render(<ResultsView status={mockStatus} onReset={() => {}} />)

    expect(screen.getByText('Software Engineer at Acme Corp')).toBeInTheDocument()
  })

  it('shows download button when docx is available', () => {
    render(<ResultsView status={mockStatus} onReset={() => {}} />)

    expect(screen.getByText('Download Tailored Resume')).toBeInTheDocument()
  })

  it('displays strengths and gaps', () => {
    render(<ResultsView status={mockStatus} onReset={() => {}} />)

    expect(screen.getByText('Strong Python skills')).toBeInTheDocument()
    expect(screen.getByText('Need more cloud experience')).toBeInTheDocument()
  })

  it('calls onReset when start over button is clicked', () => {
    const onReset = vi.fn()
    render(<ResultsView status={mockStatus} onReset={onReset} />)

    fireEvent.click(screen.getByText('Tailor Another Resume'))
    expect(onReset).toHaveBeenCalled()
  })
})
