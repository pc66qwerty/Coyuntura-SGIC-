/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary:   '#1E3A5F',
        secondary: '#8B5CF6',
        success:   '#16A34A',
        warning:   '#D97706',
        danger:    '#DC2626',
        surface:   '#FFFFFF',
        neutral:   '#111827',
      },
      fontFamily: {
        display: ['Barlow Condensed', 'sans-serif'],
        sans:    ['DM Sans', 'sans-serif'],
        mono:    ['JetBrains Mono', 'monospace'],
      },
      fontWeight: {
        thin:       '100',
        extralight: '200',
        light:      '300',
        normal:     '400',
        medium:     '500',
        semibold:   '600',
      },
      fontSize: {
        'xs':   ['12px', '16px'],
        'sm':   ['14px', '20px'],
        'base': ['16px', '24px'],
        'lg':   ['18px', '28px'],
        'xl':   ['24px', '32px'],
        '2xl':  ['32px', '40px'],
        '3xl':  ['40px', '48px'],
      },
    },
  },
  plugins: [],
}
