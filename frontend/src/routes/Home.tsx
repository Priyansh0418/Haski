import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0f1a23] via-[#14202b] to-[#0a1218] overflow-x-hidden">
      {/* Page Container */}
      <main className="max-w-[960px] mx-auto px-4 sm:px-10 md:px-20 lg:px-40 py-12">
        {/* Hero Section */}
        <section className="mt-8">
          <div className="relative rounded-xl overflow-hidden bg-[#14202b] border border-[#233648] shadow-[0_10px_30px_rgba(2,6,23,0.35)]">
            {/* Background Image */}
            <img
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuC5_aj-0DJFwUKVPeCUkWx4_RHiwBSnrAByDNIKOWQ3U-ftAMHXP3n1DtdQEDmbAL-HvUypGUdizEPc6X1cMyw8q_Q9wIGKH7OP2-LJPFvStYL29CCtMjh1ECAmlR_F2JP_q7c5BY0fGMhvdkCmCeq7cdeXQOFWlgQLkIAzTfVBtZaaf4jz3A7O8bHMPVS7IXAQ6AZcx6qT-_7spVgsN6HPDxEsGo61qGpui9foHQSdd2ieRCphKFbDj7MSWHameMd6lja-zCcJH5o"
              alt="Haski background"
              className="absolute inset-0 h-full w-full object-cover opacity-70"
            />
            {/* Dark Overlay Gradient */}
            <div className="absolute inset-0 bg-gradient-to-b from-[rgba(10,18,28,0.5)] via-[rgba(10,18,28,0.7)] to-[rgba(10,18,28,0.85)]" />

            {/* Content */}
            <div className="relative z-10 p-6 sm:p-8 md:p-12 lg:p-14 flex items-end min-h-[480px]">
              <div className="max-w-[720px]">
                <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold leading-tight text-white">
                  AI-Powered Skin &amp; Hair Analysis.
                </h1>
                <p className="mt-3 text-slate-300 text-base sm:text-lg">
                  Haski uses advanced AI to provide personalized insights into
                  your skin and hair health, helping you understand your unique
                  needs.
                </p>
                {/* Button Row */}
                <div className="mt-6 flex items-center gap-3">
                  <Link
                    to="/analyze"
                    className="inline-flex items-center rounded-lg bg-[#2b72ff] hover:bg-[#1f5fe6] text-white px-5 py-2.5 font-semibold shadow transition"
                  >
                    Get Started
                  </Link>
                  <Link
                    to="/login"
                    className="text-slate-300 hover:text-white underline underline-offset-4 transition"
                  >
                    Sign In
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* How It Works Section */}
        <section className="mt-14 md:mt-16">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
            How It Works
          </h2>
          <p className="mt-2 text-slate-400 max-w-[720px]">
            A simple three-step process to unlock personalized insights for your
            skin and hair.
          </p>

          {/* Cards Grid */}
          <div className="mt-8 grid gap-5 sm:gap-6 grid-cols-1 sm:grid-cols-3">
            {/* Capture Card */}
            <div className="h-full rounded-lg border border-[#324d67] bg-[#192633] p-5 hover:border-[#2b72ff] transition">
              <div className="text-[#2b72ff] text-xl">
                <svg
                  className="w-6 h-6"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5z" />
                </svg>
              </div>
              <h3 className="mt-3 text-white font-semibold">Capture</h3>
              <p className="mt-1 text-slate-400 text-sm">
                Easily upload or take a high-quality photo of your skin or hair
                using your device.
              </p>
            </div>

            {/* Analyze Card */}
            <div className="h-full rounded-lg border border-[#324d67] bg-[#192633] p-5 hover:border-[#2b72ff] transition">
              <div className="text-[#2b72ff] text-xl">
                <svg
                  className="w-6 h-6"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                </svg>
              </div>
              <h3 className="mt-3 text-white font-semibold">Analyze</h3>
              <p className="mt-1 text-slate-400 text-sm">
                Our advanced AI processes your image to identify key metrics and
                characteristics.
              </p>
            </div>

            {/* Insights Card */}
            <div className="h-full rounded-lg border border-[#324d67] bg-[#192633] p-5 hover:border-[#2b72ff] transition">
              <div className="text-[#2b72ff] text-xl">
                <svg
                  className="w-6 h-6"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M5 9.2h3V19H5zM10.6 5h2.8v14h-2.8zm5.6 8H19v6h-2.8z" />
                </svg>
              </div>
              <h3 className="mt-3 text-white font-semibold">Insights</h3>
              <p className="mt-1 text-slate-400 text-sm">
                Receive a detailed, personalized report with actionable
                recommendations for your routine.
              </p>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="mt-14 md:mt-16 border-t border-[#233648] pt-6 pb-10">
          <div className="flex flex-wrap items-center justify-center gap-6 text-slate-400">
            <a href="#" className="hover:text-white transition">
              About
            </a>
            <a href="#" className="hover:text-white transition">
              Contact
            </a>
            <a href="#" className="hover:text-white transition">
              Privacy Policy
            </a>
            <a href="#" className="hover:text-white transition">
              Terms of Service
            </a>
          </div>

          {/* Social Icons */}
          <div className="mt-6 flex items-center justify-center gap-5 text-slate-400">
            <a
              href="#"
              aria-label="Twitter"
              className="hover:text-white transition"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
              </svg>
            </a>
            <a
              href="#"
              aria-label="Instagram"
              className="hover:text-white transition"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.85s-.011 3.584-.069 4.85c-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07s-3.584-.012-4.85-.07c-3.252-.148-4.771-1.691-4.919-4.919-.058-1.265-.069-1.645-.069-4.85s.011-3.584.069-4.85c.149-3.225 1.664-4.771 4.919-4.919 1.266-.057 1.644-.069 4.85-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948s.014 3.667.072 4.947c.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072s3.667-.014 4.947-.072c4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.947s-.014-3.667-.072-4.947c-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.689-.073-4.948-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.162 6.162 6.162 6.162-2.759 6.162-6.162-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4s1.791-4 4-4 4 1.79 4 4-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44 1.441-.645 1.441-1.44-.645-1.44-1.441-1.44z" />
              </svg>
            </a>
            <a
              href="#"
              aria-label="Facebook"
              className="hover:text-white transition"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z" />
              </svg>
            </a>
          </div>

          {/* Copyright */}
          <p className="mt-6 text-center text-slate-500 text-sm">
            © 2024 Haski. All rights reserved.
          </p>
        </footer>
      </main>
    </div>
  );
}
