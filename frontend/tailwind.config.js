/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "media",
  theme: {
    fontFamily: {
      sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
    },
    extend: {
      colors: {
        primary: {
          DEFAULT: "#2563eb",
          600: "#1d4ed8",
        },
        surface: "#f7f8fb",
        ink: "#0f172a",
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.25rem",
      },
      boxShadow: {
        lift: "0 8px 24px -8px rgba(2,6,23,0.15)",
      },
    },
  },
  plugins: [],
};
