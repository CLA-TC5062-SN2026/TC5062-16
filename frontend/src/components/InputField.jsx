import { useId } from 'react'

function InputField({
  id,
  label,
  error = '',
  helperText = '',
  required = false,
  className = '',
  ...props
}) {
  const generatedId = useId()
  const inputId = id || generatedId
  const helperId = `${inputId}-helper`
  const errorId = `${inputId}-error`

  const describedBy = [
    helperText ? helperId : null,
    error ? errorId : null,
  ]
    .filter(Boolean)
    .join(' ') || undefined

  return (
    <div className="mb-3">
      <label htmlFor={inputId} className="form-label fw-semibold">
        {label}
        {required && <span aria-hidden="true"> *</span>}
      </label>

      <input
        id={inputId}
        className={`form-control ${error ? 'is-invalid' : ''} ${className}`.trim()}
        required={required}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={describedBy}
        {...props}
      />

      {helperText && (
        <div id={helperId} className="form-text">
          {helperText}
        </div>
      )}

      {error && (
        <div id={errorId} className="invalid-feedback d-block">
          {error}
        </div>
      )}
    </div>
  )
}

export default InputField