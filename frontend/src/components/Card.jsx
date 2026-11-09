import { useId } from 'react'

function Card({
  title,
  children,
  footer,
  className = '',
}) {
  const titleId = useId()

  return (
    <section
      className={`card shadow-sm border-0 ${className}`.trim()}
      aria-labelledby={title ? titleId : undefined}
    >
      <div className="card-body p-4">
        {title && (
          <h2 id={titleId} className="h4 card-title mb-3">
            {title}
          </h2>
        )}

        {children}
      </div>

      {footer && (
        <div className="card-footer bg-transparent">
          {footer}
        </div>
      )}
    </section>
  )
}

export default Card