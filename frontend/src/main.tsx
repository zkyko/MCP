import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Error boundary for better error handling
import { ErrorBoundary } from 'react-error-boundary'

// Error fallback component
function ErrorFallback({ error, resetErrorBoundary }: { error: Error; resetErrorBoundary: () => void }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-rose-100 p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6 text-center">
        <div className="text-red-500 mb-4">
          <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.314 15.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-gray-800 mb-2">
          Oops! Something went wrong
        </h2>
        <p className="text-gray-600 mb-4 text-sm">
          {error.message || 'An unexpected error occurred while loading the trading dashboard.'}
        </p>
        <div className="space-y-2">
          <button
            onClick={resetErrorBoundary}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
          >
            Try Again
          </button>
          <button
            onClick={() => window.location.reload()}
            className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2 px-4 rounded-lg transition-colors"
          >
            Reload Page
          </button>
        </div>
        {process.env.NODE_ENV === 'development' && (
          <details className="mt-4 text-left">
            <summary className="text-sm text-gray-500 cursor-pointer hover:text-gray-700">
              Show error details
            </summary>
            <pre className="mt-2 text-xs bg-gray-100 p-2 rounded overflow-auto max-h-32">
              {error.stack}
            </pre>
          </details>
        )}
      </div>
    </div>
  )
}

// Loading component
function LoadingSpinner() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="text-center">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
          <div className="absolute inset-0 w-16 h-16 border-4 border-transparent border-t-purple-400 rounded-full animate-spin mx-auto" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
        </div>
        <h2 className="text-xl font-semibold text-gray-700 mb-2">
          Loading Trading Dashboard
        </h2>
        <p className="text-gray-500 text-sm">
          Please wait while we prepare your analytics...
        </p>
      </div>
    </div>
  )
}

// Main app wrapper with providers and error handling
function AppWrapper() {
  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      onError={(error, errorInfo) => {
        // Log error to console in development
        if (process.env.NODE_ENV === 'development') {
          console.error('Trading Dashboard Error:', error, errorInfo)
        }
        
        // In production, you might want to send this to an error reporting service
        // Example: Sentry.captureException(error, { extra: errorInfo })
      }}
      onReset={() => {
        // Clear any error state or reload the page
        window.location.reload()
      }}
    >
      <StrictMode>
        <App />
      </StrictMode>
    </ErrorBoundary>
  )
}

// Initialize the app
const rootElement = document.getElementById('root')

if (!rootElement) {
  throw new Error('Root element not found. Make sure you have a div with id="root" in your index.html')
}

// Add some global styles and meta tags for better UX
document.documentElement.setAttribute('data-theme', 'light')

// Add viewport meta tag if it doesn't exist
if (!document.querySelector('meta[name="viewport"]')) {
  const viewport = document.createElement('meta')
  viewport.name = 'viewport'
  viewport.content = 'width=device-width, initial-scale=1.0'
  document.head.appendChild(viewport)
}

// Add description meta tag for SEO
if (!document.querySelector('meta[name="description"]')) {
  const description = document.createElement('meta')
  description.name = 'description'
  description.content = 'Professional trading analysis dashboard for tracking performance, analyzing trades, and managing your trading portfolio.'
  document.head.appendChild(description)
}

// Set page title
if (document.title === 'Vite + React + TS' || !document.title) {
  document.title = 'Trading Analysis Dashboard'
}

// Add favicon if it doesn't exist
if (!document.querySelector('link[rel="icon"]')) {
  const favicon = document.createElement('link')
  favicon.rel = 'icon'
  favicon.href = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">📈</text></svg>'
  document.head.appendChild(favicon)
}

// Performance monitoring (optional)
if ('performance' in window && 'measure' in window.performance) {
  window.addEventListener('load', () => {
    setTimeout(() => {
      const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart
      if (process.env.NODE_ENV === 'development') {
        console.log(`Trading Dashboard loaded in ${loadTime}ms`)
      }
    }, 0)
  })
}

// Service Worker registration (for future PWA capabilities)
if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration)
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError)
      })
  })
}

// Render the app
const root = createRoot(rootElement)

root.render(<AppWrapper />)