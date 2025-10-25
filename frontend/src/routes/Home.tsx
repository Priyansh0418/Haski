// Feature Card Component
function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: string;
  title: string;
  description: string;
}) {
  return (
    <div className="card p-8 md:p-10 h-full flex flex-col items-center text-center hover:shadow-lift transition-shadow duration-300">
      <div className="text-5xl md:text-6xl mb-4">{icon}</div>
      <h3 className="headline text-xl md:text-2xl mb-3 text-slate-900 dark:text-white">
        {title}
      </h3>
      <p className="muted text-sm md:text-base leading-relaxed">
        {description}
      </p>
    </div>
  );
}

// Info Badge Component
function InfoBadge({
  icon,
  title,
  description,
}: {
  icon: string;
  title: string;
  description: string;
}) {
  return (
    <div className="flex flex-col items-center text-center">
      <div className="text-4xl md:text-5xl mb-3">{icon}</div>
      <h4 className="headline text-lg md:text-xl mb-2 text-slate-900 dark:text-white">
        {title}
      </h4>
      <p className="muted text-sm md:text-base">
        {description}
      </p>
    </div>
  );
}

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero Section */}
      <main className="flex-1 flex flex-col justify-center py-16 md:py-24 px-4 md:px-6">
        <div className="max-w-4xl mx-auto w-full text-center">
          {/* Hero Headline */}
          <h1 className="headline text-5xl sm:text-6xl md:text-7xl lg:text-8xl text-primary dark:text-primary mb-6">
            Haski
          </h1>

          {/* Subtitle */}
          <h2 className="text-2xl md:text-3xl lg:text-4xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
            AI-powered skin and hair analysis in seconds
          </h2>

          {/* Description */}
          <p className="muted text-base md:text-lg max-w-2xl mx-auto mb-10">
            Upload a photo and get instant AI-powered insights about your skin
            and hair health. Simple, fast, and accurate.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <a
              href="/analyze"
              className="bg-primary hover:bg-primary-600 text-white px-8 md:px-10 py-3 md:py-4 rounded-lg font-bold text-lg transition-colors flex items-center justify-center gap-2 shadow-md hover:shadow-lg"
            >
              Get Started
              <span>→</span>
            </a>
            <a
              href="/login"
              className="text-primary dark:text-primary font-bold text-lg hover:underline transition-colors"
            >
              Sign In
            </a>
          </div>
        </div>
      </main>

      {/* Features Grid Section */}
      <section className="py-16 md:py-24 px-4 md:px-6 bg-gradient-to-b from-transparent via-slate-50/50 to-transparent dark:via-slate-900/50">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
            <FeatureCard
              icon="📸"
              title="Capture"
              description="Take photos directly from your camera or upload existing images from your device in seconds."
            />
            <FeatureCard
              icon="⚡"
              title="Analyze"
              description="Advanced AI algorithms analyze your photos with machine learning to detect skin and hair conditions."
            />
            <FeatureCard
              icon="💡"
              title="Insights"
              description="Get personalized recommendations and actionable insights to improve your skin and hair health."
            />
          </div>
        </div>
      </section>

      {/* Info Badges Section */}
      <section className="py-16 md:py-20 px-4 md:px-6">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-10">
            <InfoBadge
              icon="🔒"
              title="Privacy First"
              description="Your data is encrypted and never shared. 100% private analysis."
            />
            <InfoBadge
              icon="⚠️"
              title="Not Medical Advice"
              description="Haski is for informational purposes only. Consult a dermatologist for medical advice."
            />
            <InfoBadge
              icon="⭐"
              title="Free to Start"
              description="No signup required for basic analysis. Start using Haski today."
            />
          </div>
        </div>
      </section>

      {/* Disclaimer Footer */}
      <footer className="bg-yellow-50 dark:bg-yellow-900/30 border-t border-yellow-200 dark:border-yellow-800 py-6 px-4 md:px-6 mt-auto">
        <div className="max-w-6xl mx-auto text-center text-yellow-900 dark:text-yellow-100 text-sm leading-relaxed">
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
