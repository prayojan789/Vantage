/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // VANTAGE Design System
        // Core: deep ink-black background, cyan-gold accent, crimson alert
        base: {
          950: "#080B0F",  // deepest background
          900: "#0D1117",  // primary bg
          800: "#161B22",  // card bg
          700: "#21262D",  // elevated card
          600: "#30363D",  // border
          500: "#484F58",  // muted border
          400: "#6E7681",  // placeholder text
          300: "#8B949E",  // secondary text
          200: "#C9D1D9",  // primary text
          100: "#E6EDF3",  // strong text
        },
        cyan: {
          400: "#00D4FF",
          500: "#0EB5D9",
          600: "#0891B2",
        },
        gold: {
          400: "#F5C542",
          500: "#E6A817",
          600: "#C4820F",
        },
        crimson: {
          400: "#FF6B6B",
          500: "#EF4444",
          600: "#DC2626",
        },
        emerald: {
          400: "#34D399",
          500: "#10B981",
        },
        // Bias gradient: green(neutral) → yellow(moderate) → red(biased)
        bias: {
          low: "#34D399",
          mid: "#F5C542",
          high: "#FF6B6B",
        },
      },
      fontFamily: {
        // Display: Space Grotesk — sharp, technical, editorial
        display: ["Space Grotesk", "system-ui", "sans-serif"],
        // Body: Inter — clean readability
        body: ["Inter", "system-ui", "sans-serif"],
        // Mono: JetBrains Mono — data, scores, code
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      backgroundImage: {
        "glow-cyan": "radial-gradient(ellipse at top, rgba(0,212,255,0.08) 0%, transparent 70%)",
        "glow-gold": "radial-gradient(ellipse at bottom right, rgba(245,197,66,0.06) 0%, transparent 60%)",
        "grid-pattern": "linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)",
      },
      backgroundSize: {
        "grid": "40px 40px",
      },
      boxShadow: {
        "glass": "0 4px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05)",
        "glow-cyan": "0 0 20px rgba(0,212,255,0.15), 0 0 40px rgba(0,212,255,0.05)",
        "glow-gold": "0 0 20px rgba(245,197,66,0.15)",
        "glow-red": "0 0 20px rgba(255,107,107,0.2)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "fade-in": "fadeIn 0.4s ease-out",
        "slide-up": "slideUp 0.4s ease-out",
        "shimmer": "shimmer 2s linear infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
    },
  },
  plugins: [],
};
