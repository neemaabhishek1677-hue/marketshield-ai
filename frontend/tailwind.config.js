/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        surface: { DEFAULT: '#0f1419', light: '#1a2332', card: '#151d28' },
        accent: { DEFAULT: '#3b82f6', cyan: '#22d3ee', danger: '#ef4444', warn: '#f59e0b', ok: '#10b981' },
      },
      fontFamily: { sans: ['IBM Plex Sans', 'system-ui', 'sans-serif'], mono: ['JetBrains Mono', 'monospace'] },
    },
  },
  plugins: [],
}
