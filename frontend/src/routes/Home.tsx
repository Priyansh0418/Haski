export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <main className="flex-grow container mx-auto px-4 sm:px-6 lg:px-8 text-center flex flex-col justify-center py-16 md:py-20">
        {/* Hero Section */}
        <div className="mb-12 sm:mb-16 lg:mb-20">
          {/* Headline */}
          <h1 className="text-6xl md:text-7xl lg:text-8xl font-bold text-blue-600 dark:text-blue-500 mb-4">
            Haski
          </h1>

          {/* Subtitle */}
          <h2 className="text-2xl md:text-3xl lg:text-4xl font-semibold text-slate-900 dark:text-slate-100 mb-2">
            AI-powered skin and hair analysis in seconds
          </h2>

          {/* Description */}
          <p className="text-base md:text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto mb-8">
            Upload a photo and get instant AI-powered insights about your skin
            and hair health. Simple, fast, and accurate.
          </p>

          {/* Primary CTA */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-6">
            <a
              href="/analyze"
              className="bg-blue-600 hover:bg-blue-700 text-white py-3 px-8 rounded-lg font-semibold text-lg transition-colors flex items-center justify-center gap-2"
            >
              Get Started
              <span className="text-xl">→</span>
            </a>
            <a
              href="/login"
              className="text-blue-600 dark:text-blue-400 font-semibold text-lg hover:underline"
            >
              Sign In
            </a>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12 sm:mb-16">
          {/* Feature 1: Capture */}
          <div className="bg-white dark:bg-slate-800 p-8 rounded-lg shadow-md hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
            <div className="flex justify-center mb-4">
              <span className="text-5xl">📸</span>
            </div>
            <h3 className="text-2xl font-semibold text-slate-900 dark:text-white mb-2">
              Capture
            </h3>
            <p className="text-slate-600 dark:text-slate-400 text-sm">
              Take photos directly from your camera or upload existing images
              from your device in seconds.
            </p>
          </div>

          {/* Feature 2: Analyze */}
          <div className="bg-white dark:bg-slate-800 p-8 rounded-lg shadow-md hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
            <div className="flex justify-center mb-4">
              <span className="text-5xl">⚡</span>
            </div>
            <h3 className="text-2xl font-semibold text-slate-900 dark:text-white mb-2">
              Analyze
            </h3>
            <p className="text-slate-600 dark:text-slate-400 text-sm">
              Advanced AI algorithms analyze your photos with machine learning
              to detect skin and hair conditions.
            </p>
          </div>

          {/* Feature 3: Insights */}
          <div className="bg-white dark:bg-slate-800 p-8 rounded-lg shadow-md hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
            <div className="flex justify-center mb-4">
              <span className="text-5xl">💡</span>
            </div>
            <h3 className="text-2xl font-semibold text-slate-900 dark:text-white mb-2">
              Insights
            </h3>
            <p className="text-slate-600 dark:text-slate-400 text-sm">
              Get personalized recommendations and actionable insights to
              improve your skin and hair health.
            </p>
          </div>
        </div>

        {/* Trust Row - Disclaimers */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-8">
          {/* Privacy First */}
          <div className="flex flex-col items-center">
            <div className="text-4xl mb-3">🔒</div>
            <h4 className="font-semibold text-slate-900 dark:text-white mb-2">
              Privacy First
            </h4>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Your data is encrypted and never shared. 100% private analysis.
            </p>
          </div>

          {/* No Medical Advice */}
          <div className="flex flex-col items-center">
            <div className="text-4xl mb-3">⚠️</div>
            <h4 className="font-semibold text-slate-900 dark:text-white mb-2">
              Not Medical Advice
            </h4>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Haski is for informational purposes only. Consult a
              dermatologist for medical advice.
            </p>
          </div>

          {/* Free & Open */}
          <div className="flex flex-col items-center">
            <div className="text-4xl mb-3">⭐</div>
            <h4 className="font-semibold text-slate-900 dark:text-white mb-2">
              Free to Start
            </h4>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              No signup required for basic analysis. Start using Haski today.
            </p>
          </div>
        </div>
      </main>

      {/* Footer Disclaimer */}
      <footer className="bg-yellow-100 dark:bg-yellow-900 p-4">
        <div className="container mx-auto text-center text-yellow-800 dark:text-yellow-200 text-sm">
          <p>
            <strong>Disclaimer:</strong> Haski provides AI-powered analysis for
            educational purposes only and is not a substitute for professional
            medical advice, diagnosis, or treatment. Always consult a qualified
            dermatologist or healthcare provider for skin and hair concerns.
          </p>
        </div>
      </footer>
    </div>
  );
}
