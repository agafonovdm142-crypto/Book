/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        burgundy: {
          900: '#4A1A2E',
          700: '#6B2642',
          500: '#7B2D4C',
          300: '#A8577A',
          100: '#E8D5E0',
        },
        gold: {
          900: '#8B623E',
          500: '#C8956C',
          300: '#DEBA9E',
          100: '#F5E6D8',
        },
        cream: {
          DEFAULT: '#FAF6F1',
          dark: '#F5E6D8',
        },
        ink: {
          900: '#0F0C0B',
          700: '#1E1A18',
          500: '#4A4542',
          300: '#8A8580',
          100: '#E8E4E0',
        },
      },
      fontFamily: {
        serif: ['Playfair Display', 'Georgia', 'serif'],
        sans: ['Inter', '-apple-system', 'sans-serif'],
      },
      animation: {
        'fade-slide-up': 'fadeSlideUp 0.5s ease-out',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
      },
      keyframes: {
        fadeSlideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
};
