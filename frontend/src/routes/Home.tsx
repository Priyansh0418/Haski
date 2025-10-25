export default function Home() {
  return (
    <div className="w-full py-12 sm:py-16 lg:py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Hero Section */}
        <div className="text-center mb-16 sm:mb-20 lg:mb-24">
          {/* Headline */}
          <div className="mb-6 sm:mb-8">
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-black bg-gradient-to-r from-blue-600 via-cyan-600 to-blue-600 dark:from-blue-400 dark:via-cyan-400 dark:to-blue-400 bg-clip-text text-transparent mb-4 tracking-tight">
              Haski
            </h1>
            <div className="h-1 w-24 bg-gradient-to-r from-blue-600 to-cyan-600 mx-auto rounded-full"></div>
          </div>

          {/* Subtitle */}
          <p className="text-xl sm:text-2xl lg:text-3xl text-slate-700 dark:text-slate-300 mb-8 sm:mb-10 max-w-2xl mx-auto font-medium leading-relaxed">
            AI-powered skin and hair analysis in seconds
          </p>

          {/* Description */}
          <p className="text-base sm:text-lg text-slate-600 dark:text-slate-400 mb-10 sm:mb-12 max-w-2xl mx-auto">
            Upload a photo and get instant AI-powered insights about your skin
            and hair health. Simple, fast, and accurate.
          </p>

          {/* Primary CTA */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <a
              href="/analyze"
              className="inline-block bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 dark:from-blue-700 dark:to-cyan-700 dark:hover:from-blue-800 dark:hover:to-cyan-800 text-white font-bold py-4 px-8 sm:px-10 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 text-lg transform hover:scale-105"
            >
              🚀 Get Started →
            </a>
            <a
              href="/login"
              className="inline-block bg-white/80 dark:bg-slate-800/80 hover:bg-white/90 dark:hover:bg-slate-800/90 text-slate-900 dark:text-white font-semibold py-4 px-8 sm:px-10 rounded-xl border border-slate-200 dark:border-slate-700 transition-all duration-300"
            >
              Sign In
            </a>
          </div>

          {/* Subtext */}
          <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400 mt-6">
            No credit card required • Free to start • 100% private
          </p>
        </div>

        {/* Features Grid */}
        <div className="mb-16 sm:mb-20">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
            {/* Feature 1: Capture */}
            <div className="group bg-white/80 dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 shadow-md hover:shadow-xl transition-all duration-300 border border-slate-100 dark:border-slate-700 hover:border-blue-300 dark:hover:border-blue-600 h-full flex flex-col">
              <div className="text-6xl mb-4 group-hover:scale-110 transition-transform duration-300">
                📸
              </div>
              <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">
                Capture
              </h3>
              <p className="text-slate-600 dark:text-slate-300 flex-grow">
                Take photos directly from your camera or upload existing images
                from your device in seconds.
              </p>
              <div className="mt-4 text-sm text-blue-600 dark:text-blue-400 font-semibold group-hover:translate-x-1 transition-transform">
                → Quick & Easy
              </div>
            </div>

            {/* Feature 2: Analyze */}
            <div className="group bg-white/80 dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 shadow-md hover:shadow-xl transition-all duration-300 border border-slate-100 dark:border-slate-700 hover:border-cyan-300 dark:hover:border-cyan-600 h-full flex flex-col">
              <div className="text-6xl mb-4 group-hover:scale-110 transition-transform duration-300">
                ⚡
              </div>
              <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">
                Analyze
              </h3>
              <p className="text-slate-600 dark:text-slate-300 flex-grow">
                Advanced AI algorithms analyze your photos with machine learning
                to detect skin and hair conditions.
              </p>
              <div className="mt-4 text-sm text-cyan-600 dark:text-cyan-400 font-semibold group-hover:translate-x-1 transition-transform">
                → Accurate Results
              </div>
            </div>

            {/* Feature 3: Insights */}
            <div className="group bg-white/80 dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 shadow-md hover:shadow-xl transition-all duration-300 border border-slate-100 dark:border-slate-700 hover:border-purple-300 dark:hover:border-purple-600 h-full flex flex-col">
              <div className="text-6xl mb-4 group-hover:scale-110 transition-transform duration-300">
                💡
              </div>
              <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">
                Insights
              </h3>
              <p className="text-slate-600 dark:text-slate-300 flex-grow">
                Get personalized recommendations and actionable insights to
                improve your skin and hair health.
              </p>
              <div className="mt-4 text-sm text-purple-600 dark:text-purple-400 font-semibold group-hover:translate-x-1 transition-transform">
                → Personalized
              </div>
            </div>
          </div>
        </div>

        {/* Trust Row - Disclaimers */}
        <div className="border-t border-slate-200 dark:border-slate-700 pt-12 sm:pt-16">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 sm:gap-8">
            {/* Privacy First */}
            <div className="text-center">
              <div className="text-4xl mb-3">🔒</div>
              <h4 className="font-semibold text-slate-900 dark:text-white mb-2">
                Privacy First
              </h4>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Your data is encrypted and never shared. 100% private analysis.
              </p>
            </div>

            {/* No Medical Advice */}
            <div className="text-center">
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
            <div className="text-center">
              <div className="text-4xl mb-3">✨</div>
              <h4 className="font-semibold text-slate-900 dark:text-white mb-2">
                Free to Start
              </h4>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                No signup required for basic analysis. Start using Haski today.
              </p>
            </div>
          </div>

          {/* Disclaimer */}
          <div className="mt-12 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
            <p className="text-xs sm:text-sm text-yellow-800 dark:text-yellow-200 text-center">
              <strong>Disclaimer:</strong> Haski provides AI-powered analysis
              for educational purposes only and is not a substitute for
              professional medical advice, diagnosis, or treatment. Always
              consult a qualified dermatologist or healthcare provider for skin
              and hair concerns.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
