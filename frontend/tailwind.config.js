/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        soil: {
          50:  '#faf7f0',
          100: '#f0e8d8',
          200: '#ddd0b0',
          300: '#c4ae82',
          400: '#a8895a',
          500: '#8c6f42',
          600: '#715737',
          700: '#5a452e',
          800: '#483727',
          900: '#3c2f22',
        },
        leaf: {
          50:  '#f0faf0',
          100: '#dcf5dc',
          200: '#bbebb9',
          300: '#8dd98a',
          400: '#5bbf57',
          500: '#3da338',
          600: '#2d862a',
          700: '#266823',
          800: '#22531f',
          900: '#1d441b',
        },
        harvest: {
          50:  '#fffbeb',
          100: '#fff3c4',
          200: '#ffe585',
          300: '#ffd046',
          400: '#ffbc1f',
          500: '#f99b07',
          600: '#dd7302',
          700: '#b75006',
          800: '#943d0c',
          900: '#7a330d',
        },
      },
      fontFamily: {
        display: ['Georgia', 'Cambria', 'serif'],
        body: ['system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
