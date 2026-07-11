/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js",
  ],
  safelist: [
    "sm:grid-cols-2",  // dynamic :class in _modal_model_settings.html
    "bg-emerald-500", "text-white", "border-emerald-500",
    "bg-emerald-50", "text-emerald-700", "border-emerald-200", "hover:bg-emerald-100",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
<<<<<<< HEAD
      
=======

>>>>>>> 7bea4ba3213ebf96303ce6b51b347bbaaf088462
      colors: {
        surface: {
          0: 'var(--surface-0)',
          1: 'var(--surface-1)',
          2: 'var(--surface-2)',
          3: 'var(--surface-3)',
          4: 'var(--surface-4)',
          DEFAULT: 'var(--surface-0)',
          alt: 'var(--surface-1)',
          muted: 'var(--surface-2)',
        },
        fg: {
          DEFAULT: 'var(--text-body)',
          display: 'var(--text-display)',
          title: 'var(--text-title)',
          heading: 'var(--text-heading)',
          caption: 'var(--text-caption)',
          secondary: 'var(--text-secondary)',
          tertiary: 'var(--text-tertiary)',
          muted: 'var(--text-muted)',
        },
        line: {
          DEFAULT: 'var(--border-faint)',
          strong: 'var(--border-normal)',
        },
        accent: {
          execution: 'var(--accent-execution)',
          runtime: 'var(--accent-runtime)',
          planning: 'var(--accent-planning)',
          success: 'var(--accent-success)',
          warning: 'var(--accent-warning)',
          error: 'var(--accent-error)',
          DEFAULT: 'var(--accent-runtime)',
          hover: 'var(--accent-runtime-hover)',
          fg: 'var(--text-inverse)',
        },
        danger: {
          DEFAULT: 'var(--accent-error)',
          bg: 'var(--bg-danger-hover)',
        },
        code: 'var(--code-bg)',
      },
animation: {
        'fade-in-up': 'fadeInUp 0.5s ease-out forwards',
      },
      keyframes: {
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'none' },
        }
      }
    },
  },
  plugins: [],
}
