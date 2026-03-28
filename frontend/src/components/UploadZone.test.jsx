import { fireEvent, render, screen } from '@testing-library/react'

import UploadZone from './UploadZone'


describe('UploadZone', () => {
  test('analyze button stays disabled until valid file is selected', () => {
    render(<UploadZone onAnalyze={() => {}} onDemo={() => {}} />)
    expect(screen.getByRole('button', { name: /analyze case/i })).toBeDisabled()
  })

  test('shows validation error for non-pdf file', () => {
    const { container } = render(<UploadZone onAnalyze={() => {}} onDemo={() => {}} />)
    const input = container.querySelector('input[type="file"]')

    const badFile = new File(['hello'], 'evidence.txt', { type: 'text/plain' })
    fireEvent.change(input, { target: { files: [badFile] } })

    expect(screen.getByText(/please upload pdf files only/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /analyze case/i })).toBeDisabled()
  })

  test('calls onAnalyze for valid pdf', () => {
    const onAnalyze = vi.fn()
    const { container } = render(<UploadZone onAnalyze={onAnalyze} onDemo={() => {}} />)
    const input = container.querySelector('input[type="file"]')

    const goodFile = new File(['%PDF-1.4'], 'case.pdf', { type: 'application/pdf' })
    fireEvent.change(input, { target: { files: [goodFile] } })

    fireEvent.click(screen.getByRole('button', { name: /analyze case/i }))
    expect(onAnalyze).toHaveBeenCalledTimes(1)
    expect(onAnalyze).toHaveBeenCalledWith(goodFile)
  })
})
