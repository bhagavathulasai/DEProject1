/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        navy: {
          50: '#f2f7ff',
          100: '#dfeeff',
          200: '#bfdcff',
          300: '#8ebef8',
          400: '#5d98f2',
          500: '#2c6ee0',
          600: '#204fb3',
          700: '#1d3e88',
          800: '#183366',
          900: '#0d1e36',
        },
        teal: {
          50: '#ecfeff',
          100: '#cffafe',
          200: '#a5f3fc',
          300: '#67e8f9',
          400: '#22d3ee',
          500: '#14b8d6',
          600: '#0f8ea8',
          700: '#0d6f86',
          800: '#115d70',
          900: '#124a5c',
        },
      },
      boxShadow: {
        soft: '0 10px 30px rgba(13,30,54,0.12)',
      },
    },
  },
  plugins: [],
}
