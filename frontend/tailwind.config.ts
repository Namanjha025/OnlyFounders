import type { Config } from 'tailwindcss'

/** Satisfies shadcn CLI + IDE; Tailwind v4 styles load via Vite plugin + src/index.css */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
} satisfies Config
