import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="relative flex min-h-screen w-full flex-col font-display group/design-root overflow-x-hidden">
      <div className="layout-container flex h-full grow flex-col">
        <div className="px-4 sm:px-10 md:px-20 lg:px-40 flex flex-1 justify-center py-5">
          <div className="layout-content-container flex flex-col max-w-[960px] flex-1">
            {/* Main Content */}
            <main className="flex-grow">
              {/* HeroSection */}
              <div className="@container py-10">
                <div className="@[480px]:p-4">
                  <div
                    className="flex min-h-[480px] flex-col gap-6 bg-cover bg-center bg-no-repeat @[480px]:gap-8 @[480px]:rounded-xl items-start justify-end px-4 pb-10 @[480px]:px-10"
                    style={{
                      backgroundImage: `linear-gradient(rgba(16, 25, 34, 0.3) 0%, rgba(16, 25, 34, 0.8) 100%), url("https://lh3.googleusercontent.com/aida-public/AB6AXuC5_aj-0DJFwUKVPeCUkWx4_RHiwBSnrAByDNIKOWQ3U-ftAMHXP3n1DtdQEDmbAL-HvUypGUdizEPc6X1cMyw8q_Q9wIGKH7OP2-LJPFvStYL29CCtMjh1ECAmlR_F2JP_q7c5BY0fGMhvdkCmCeq7cdeXQOFWlgQLkIAzTfVBtZaaf4jz3A7O8bHMPVS7IXAQ6AZcx6qT-_7spVgsN6HPDxEsGo61qGpui9foHQSdd2ieRCphKFbDj7MSWHameMd6lja-zCcJH5o")`,
                    }}
                  >
                    <div className="flex flex-col gap-2 text-left">
                      <h1 className="text-white text-4xl font-black leading-tight tracking-[-0.033em] @[480px]:text-5xl @[480px]:font-black @[480px]:leading-tight @[480px]:tracking-[-0.033em]">
                        AI-Powered Skin &amp; Hair Analysis.
                      </h1>
                      <h2 className="text-gray-300 text-sm font-normal leading-normal @[480px]:text-base @[480px]:font-normal @[480px]:leading-normal">
                        Haski uses advanced AI to provide personalized insights
                        into your skin and hair health, helping you understand
                        your unique needs.
                      </h2>
                    </div>
                    <Link
                      to="/analyze"
                      className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 @[480px]:h-12 @[480px]:px-5 bg-[#137fec] text-white text-sm font-bold leading-normal tracking-[0.015em] @[480px]:text-base @[480px]:font-bold @[480px]:leading-normal @[480px]:tracking-[0.015em] hover:bg-opacity-90 transition-opacity"
                    >
                      <span className="truncate">Get Started</span>
                    </Link>
                  </div>
                </div>
              </div>

              {/* FeatureSection */}
              <div className="flex flex-col gap-10 px-4 py-10 @container">
                <div className="flex flex-col gap-4">
                  <h1 className="text-white tracking-light text-[32px] font-bold leading-tight @[480px]:text-4xl @[480px]:font-black @[480px]:leading-tight @[480px]:tracking-[-0.033em] max-w-[720px]">
                    How It Works
                  </h1>
                  <p className="text-gray-400 text-base font-normal leading-normal max-w-[720px]">
                    A simple three-step process to unlock personalized insights
                    for your skin and hair.
                  </p>
                </div>
                <div className="grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))] gap-4 p-0">
                  {/* Capture Card */}
                  <div className="flex flex-1 gap-4 rounded-lg border border-[#324d67] bg-[#192633] p-4 flex-col transition-all hover:border-[#137fec]">
                    <div className="text-[#137fec]">
                      <svg
                        className="w-8 h-8"
                        fill="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5z" />
                      </svg>
                    </div>
                    <div className="flex flex-col gap-1">
                      <h3 className="text-white text-base font-bold leading-tight">
                        Capture
                      </h3>
                      <p className="text-[#92adc9] text-sm font-normal leading-normal">
                        Easily upload or take a high-quality photo of your skin
                        or hair using your device.
                      </p>
                    </div>
                  </div>

                  {/* Analyze Card */}
                  <div className="flex flex-1 gap-4 rounded-lg border border-[#324d67] bg-[#192633] p-4 flex-col transition-all hover:border-[#137fec]">
                    <div className="text-[#137fec]">
                      <svg
                        className="w-8 h-8"
                        fill="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                      </svg>
                    </div>
                    <div className="flex flex-col gap-1">
                      <h3 className="text-white text-base font-bold leading-tight">
                        Analyze
                      </h3>
                      <p className="text-[#92adc9] text-sm font-normal leading-normal">
                        Our advanced AI processes your image to identify key
                        metrics and characteristics.
                      </p>
                    </div>
                  </div>

                  {/* Insights Card */}
                  <div className="flex flex-1 gap-4 rounded-lg border border-[#324d67] bg-[#192633] p-4 flex-col transition-all hover:border-[#137fec]">
                    <div className="text-[#137fec]">
                      <svg
                        className="w-8 h-8"
                        fill="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path d="M5 9.2h3V19H5zM10.6 5h2.8v14h-2.8zm5.6 8H19v6h-2.8z" />
                      </svg>
                    </div>
                    <div className="flex flex-col gap-1">
                      <h3 className="text-white text-base font-bold leading-tight">
                        Insights
                      </h3>
                      <p className="text-[#92adc9] text-sm font-normal leading-normal">
                        Receive a detailed, personalized report with actionable
                        recommendations for your routine.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </main>

            {/* Footer */}
            <footer className="flex flex-col gap-8 px-5 py-10 text-center @container border-t border-solid border-[#233648] mt-10">
              <div className="flex flex-wrap items-center justify-center gap-6 @[480px]:flex-row @[480px]:justify-center">
                <a
                  href="#"
                  className="text-[#92adc9] text-sm font-normal leading-normal min-w-24 hover:text-[#137fec] transition-colors"
                >
                  About
                </a>
                <a
                  href="#"
                  className="text-[#92adc9] text-sm font-normal leading-normal min-w-24 hover:text-[#137fec] transition-colors"
                >
                  Contact
                </a>
                <a
                  href="#"
                  className="text-[#92adc9] text-sm font-normal leading-normal min-w-24 hover:text-[#137fec] transition-colors"
                >
                  Privacy Policy
                </a>
                <a
                  href="#"
                  className="text-[#92adc9] text-sm font-normal leading-normal min-w-24 hover:text-[#137fec] transition-colors"
                >
                  Terms of Service
                </a>
              </div>
              <div className="flex flex-wrap justify-center gap-4">
                <a
                  aria-label="Twitter"
                  href="#"
                  className="hover:text-[#137fec] transition-colors"
                >
                  <svg
                    className="h-6 w-6 text-[#92adc9] hover:text-[#137fec] transition-colors"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                  </svg>
                </a>
                <a
                  aria-label="Instagram"
                  href="#"
                  className="hover:text-[#137fec] transition-colors"
                >
                  <svg
                    className="h-6 w-6 text-[#92adc9] hover:text-[#137fec] transition-colors"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.85s-.011 3.584-.069 4.85c-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07s-3.584-.012-4.85-.07c-3.252-.148-4.771-1.691-4.919-4.919-.058-1.265-.069-1.645-.069-4.85s.011-3.584.069-4.85c.149-3.225 1.664-4.771 4.919-4.919 1.266-.057 1.644-.069 4.85-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948s.014 3.667.072 4.947c.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072s3.667-.014 4.947-.072c4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.947s-.014-3.667-.072-4.947c-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.689-.073-4.948-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.162 6.162 6.162 6.162-2.759 6.162-6.162-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4s1.791-4 4-4 4 1.79 4 4-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44 1.441-.645 1.441-1.44-.645-1.44-1.441-1.44z" />
                  </svg>
                </a>
                <a
                  aria-label="Facebook"
                  href="#"
                  className="hover:text-[#137fec] transition-colors"
                >
                  <svg
                    className="h-6 w-6 text-[#92adc9] hover:text-[#137fec] transition-colors"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z" />
                  </svg>
                </a>
              </div>
              <p className="text-[#92adc9] text-sm font-normal leading-normal">
                © 2024 Haski. All rights reserved.
              </p>
            </footer>
          </div>
        </div>
      </div>
    </div>
  );
}


