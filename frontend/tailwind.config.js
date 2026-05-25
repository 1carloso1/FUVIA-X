/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // 1. COLORES SEMÁNTICOS
      colors: {
        brand: {
          DEFAULT: '#00357a', // Tu azul principal
          hover: '#002a60',   // Tu azul oscuro para hover
          light: '#0a2e5c',   // Azul para textos/títulos
        },
        concrete: {
          light: '#94a3b8', // Ceniza
          dark: '#383b1e',  // Cemento
        }
      },
      // 2. FUENTES (Opcional, si quieres una específica)
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      // 3. ANIMACIONES (Para tus cargas y apariciones)
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      }
    },
  },
  plugins: [],
}