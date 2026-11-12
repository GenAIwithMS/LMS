/** @type {import('tailwindcss').Config} */

// The Lyceum's look: a school register. Bottle-green ink (the school blazer and the
// register's cloth cover) on warm paper, with serif titles like a printed report card.
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Bottle green: buttons, links, the selected menu item
        primary: {
          50: '#eef4f0',
          100: '#dce9e1',
          200: '#bbd3c5',
          300: '#8fb5a0',
          400: '#5f8f77',
          500: '#3e725d',
          600: '#1f5b45',
          700: '#174734',
          800: '#11372a',
          900: '#0b261d',
        },
        // Warm paper greys instead of Tailwind's blue-tinted ones
        gray: {
          50: '#f8f7f4',
          100: '#f0eee9',
          200: '#e3e0d8',
          300: '#cfcbc1',
          400: '#a39e93',
          500: '#757067',
          600: '#5a564e',
          700: '#45423c',
          800: '#2e2c28',
          900: '#1c1b18',
        },
        // Brass: only for the crest and the "today" marker
        brass: {
          100: '#f3e6cc',
          500: '#b07d2b',
          600: '#94681f',
        },
        paper: '#fbfaf6',
        // The other colours still mark categories (subjects in the timetable, roles,
        // edit buttons) but in muted ink tones, so nothing glows next to the green
        blue: {
          50: '#eef2f7',
          100: '#dbe4ef',
          200: '#b9cadf',
          300: '#8eaaca',
          400: '#6286b0',
          500: '#436a96',
          600: '#335781',
          700: '#2a4769',
          800: '#233a55',
          900: '#1b2c40',
        },
        indigo: {
          50: '#f0f0f6',
          100: '#e0e0ee',
          200: '#c3c2dc',
          300: '#9d9bc3',
          400: '#7774a6',
          500: '#5d5a8c',
          600: '#4c4977',
          700: '#3e3c61',
          800: '#32314e',
          900: '#26253b',
        },
        purple: {
          50: '#f6f0f5',
          100: '#ecdfea',
          200: '#d9bfd5',
          300: '#bf97b9',
          400: '#9f6d98',
          500: '#84527d',
          600: '#6e4268',
          700: '#5a3655',
          800: '#472c44',
          900: '#352133',
        },
        violet: {
          50: '#f6f0f5',
          100: '#ecdfea',
          200: '#d9bfd5',
          300: '#bf97b9',
          400: '#9f6d98',
          500: '#84527d',
          600: '#6e4268',
          700: '#5a3655',
          800: '#472c44',
          900: '#352133',
        },
        pink: {
          50: '#f9f0ef',
          100: '#f2dfdd',
          200: '#e4bfbb',
          300: '#d09891',
          400: '#b8706a',
          500: '#9e554f',
          600: '#854540',
          700: '#6d3935',
          800: '#562e2b',
          900: '#402220',
        },
      },
      fontFamily: {
        sans: ['"Public Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        serif: ['"Source Serif 4"', 'Georgia', 'ui-serif', 'serif'],
      },
      borderRadius: {
        // Softer corners everywhere, but not pill-like
        xl: '0.5rem',
        '2xl': '0.625rem',
        '3xl': '0.75rem',
      },
    },
  },
  plugins: [],
}
