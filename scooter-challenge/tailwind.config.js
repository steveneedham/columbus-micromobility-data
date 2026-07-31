/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        paper: '#F3F0E8',
        sheet: '#FBFAF6',
        panel: '#E8E4DA',
        rule: '#C8C2B5',
        ink: '#202A2E',
        note: '#5D696D',
        brick: '#A94728',
        'brick-dim': '#D49A83',
        river: '#236A73',
        'river-wash': '#9CC6C9',
        'night-map': '#172126',
      },
      fontFamily: {
        display: ['Newsreader', 'serif'],
        sans: ['"IBM Plex Sans"', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'monospace'],
      },
      borderRadius: {
        sheet: '10px',
        tag: '3px',
      },
    },
  },
  plugins: [],
};
