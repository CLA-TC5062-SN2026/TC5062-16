function Button({
  children,
  variant = 'primary',
  isLoading = false,
  loadingText = 'Cargando...',
  disabled = false,
  className = '',
  type = 'button',
  ...props
}) {
  const variantClass =
    variant === 'secondary' ? 'btn-outline-secondary' : 'btn-primary'

  return (
    <button
      type={type}
      className={`btn ${variantClass} ${className}`.trim()}
      disabled={disabled || isLoading}
      aria-busy={isLoading ? 'true' : undefined}
      {...props}
    >
      {isLoading ? (
        <>
          <span
            className="spinner-border spinner-border-sm me-2"
            aria-hidden="true"
          />
          {loadingText}
        </>
      ) : (
        children
      )}
    </button>
  )
}

export default Button