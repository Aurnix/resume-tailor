import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from '../App'

describe('App', () => {
  it('renders the header', () => {
    render(<App />)
    expect(screen.getByText('Resume Tailor')).toBeInTheDocument()
  })

  it('renders the subtitle', () => {
    render(<App />)
    expect(screen.getByText(/AI-powered resume optimization/i)).toBeInTheDocument()
  })

  it('shows the tailor form initially', () => {
    render(<App />)
    expect(screen.getByText('Your Resume (Markdown format)')).toBeInTheDocument()
    expect(screen.getByText(/Job Description/i)).toBeInTheDocument()
  })

  it('has a submit button', () => {
    render(<App />)
    expect(screen.getByRole('button', { name: /Tailor My Resume/i })).toBeInTheDocument()
  })
})
