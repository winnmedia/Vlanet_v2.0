/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      // ========================================
      //   (Color System)
      // ========================================
      colors: {
        //  
        brand: {
          primary: '#1631F8',
          'primary-dark': '#0F23C9',
          secondary: '#6C5CE7',
          accent: '#00D4FF',
        },
        
        //   
        phase: {
          planning: {
            DEFAULT: '#3B82F6',
            light: '#DBEAFE',
            dark: '#1E40AF',
          },
          production: {
            DEFAULT: '#F59E0B',
            light: '#FEF3C7',
            dark: '#D97706',
          },
          'post-production': {
            DEFAULT: '#8B5CF6',
            light: '#EDE9FE',
            dark: '#7C3AED',
          },
          review: {
            DEFAULT: '#06B6D4',
            light: '#CFFAFE',
            dark: '#0891B2',
          },
          completed: {
            DEFAULT: '#10B981',
            light: '#D1FAE5',
            dark: '#059669',
          },
          'on-hold': {
            DEFAULT: '#6B7280',
            light: '#F3F4F6',
            dark: '#4B5563',
          },
        },
        
        //   
        feedback: {
          pending: {
            DEFAULT: '#F59E0B',
            light: '#FEF3C7',
          },
          'in-progress': {
            DEFAULT: '#3B82F6',
            light: '#DBEAFE',
          },
          resolved: {
            DEFAULT: '#10B981',
            light: '#D1FAE5',
          },
          rejected: {
            DEFAULT: '#EF4444',
            light: '#FEE2E2',
          },
        },
        
        //  
        priority: {
          critical: {
            DEFAULT: '#DC2626',
            light: '#FEE2E2',
          },
          high: {
            DEFAULT: '#EA580C',
            light: '#FFEDD5',
          },
          medium: {
            DEFAULT: '#D97706',
            light: '#FEF3C7',
          },
          low: {
            DEFAULT: '#059669',
            light: '#D1FAE5',
          },
        },
        
        // AI  
        ai: {
          generate: {
            DEFAULT: '#8B5CF6',
            light: '#EDE9FE',
          },
          analyze: {
            DEFAULT: '#06B6D4',
            light: '#CFFAFE',
          },
          recommend: {
            DEFAULT: '#F59E0B',
            light: '#FEF3C7',
          },
        },
      },
      
      // ========================================
      //  (Typography)
      // ========================================
      fontFamily: {
        sans: ['Pretendard', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Courier New', 'monospace'],
      },
      
      fontSize: {
        '2xs': ['0.625rem', { lineHeight: '0.875rem' }], // 10px
        'xs': ['0.75rem', { lineHeight: '1rem' }],       // 12px
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],   // 14px
        'base': ['1rem', { lineHeight: '1.5rem' }],      // 16px
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],   // 18px
        'xl': ['1.25rem', { lineHeight: '1.875rem' }],   // 20px
        '2xl': ['1.5rem', { lineHeight: '2rem' }],       // 24px
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],  // 30px
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],    // 36px
        '5xl': ['3rem', { lineHeight: '1.16' }],         // 48px
        '6xl': ['3.75rem', { lineHeight: '1.16' }],      // 60px
      },
      
      // ========================================
      //   (Spacing)
      // ========================================
      spacing: {
        '4.5': '1.125rem',  // 18px
        '13': '3.25rem',    // 52px
        '15': '3.75rem',    // 60px
        '17': '4.25rem',    // 68px
        '18': '4.5rem',     // 72px
        '19': '4.75rem',    // 76px
        '21': '5.25rem',    // 84px
        '22': '5.5rem',     // 88px
        '25': '6.25rem',    // 100px
        '26': '6.5rem',     // 104px
        '30': '7.5rem',     // 120px
      },
      
      // ========================================
      //   (Border Radius)
      // ========================================
      borderRadius: {
        'xs': '0.125rem',   // 2px
        'sm': '0.25rem',    // 4px
        'DEFAULT': '0.375rem', // 6px
        'md': '0.5rem',     // 8px
        'lg': '0.75rem',    // 12px
        'xl': '1rem',       // 16px
        '2xl': '1.5rem',    // 24px
        '3xl': '2rem',      // 32px
      },
      
      // ========================================
      //  (Box Shadow)
      // ========================================
      boxShadow: {
        'xs': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'sm': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
        'DEFAULT': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
        'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
        '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        'inner': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.05)',
        'brand': '0 4px 14px 0 rgba(22, 49, 248, 0.15)',
        'card': '0 2px 8px rgba(0, 0, 0, 0.08)',
        'hover': '0 8px 24px rgba(0, 0, 0, 0.12)',
        'modal': '0 20px 60px rgba(0, 0, 0, 0.3)',
      },
      
      // ========================================
      //  (Animation)
      // ========================================
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'fade-out': 'fadeOut 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'slide-left': 'slideLeft 0.3s ease-out',
        'slide-right': 'slideRight 0.3s ease-out',
        'scale-up': 'scaleUp 0.2s ease-out',
        'scale-down': 'scaleDown 0.2s ease-out',
        'spin-slow': 'spin 3s linear infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'progress': 'progress 1s ease-in-out infinite',
      },
      
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeOut: {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideLeft: {
          '0%': { transform: 'translateX(10px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideRight: {
          '0%': { transform: 'translateX(-10px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        scaleUp: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        scaleDown: {
          '0%': { transform: 'scale(1.05)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
        progress: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
      },
      
      // ========================================
      //  (Transition)
      // ========================================
      transitionDuration: {
        '0': '0ms',
        '100': '100ms',
        '200': '200ms',
        '300': '300ms',
        '400': '400ms',
        '500': '500ms',
        '600': '600ms',
        '700': '700ms',
        '800': '800ms',
        '900': '900ms',
        '1000': '1000ms',
      },
      
      transitionTimingFunction: {
        'ease-in-out-cubic': 'cubic-bezier(0.645, 0.045, 0.355, 1)',
        'ease-out-cubic': 'cubic-bezier(0.215, 0.61, 0.355, 1)',
        'ease-in-cubic': 'cubic-bezier(0.55, 0.055, 0.675, 0.19)',
        'ease-out-expo': 'cubic-bezier(0.19, 1, 0.22, 1)',
        'bounce': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
      },
      
      // ========================================
      //   (Screens)
      // ========================================
      screens: {
        'xs': '480px',
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1536px',
        '3xl': '1920px',
        'tablet': '768px',
        'laptop': '1024px',
        'desktop': '1280px',
        'wide': '1536px',
      },
      
      // ========================================
      // Z-Index
      // ========================================
      zIndex: {
        '1': '1',
        '2': '2',
        '3': '3',
        '4': '4',
        '5': '5',
        '60': '60',
        '70': '70',
        '80': '80',
        '90': '90',
        '100': '100',
        'dropdown': '1000',
        'sticky': '1020',
        'fixed': '1030',
        'modal-backdrop': '1040',
        'modal': '1050',
        'popover': '1060',
        'tooltip': '1070',
        'toast': '1080',
      },
      
      // ========================================
      // /  (Min/Max)
      // ========================================
      minWidth: {
        '0': '0',
        'xs': '20rem',
        'sm': '24rem',
        'md': '28rem',
        'lg': '32rem',
        'xl': '36rem',
        '2xl': '42rem',
        '3xl': '48rem',
        '4xl': '56rem',
        '5xl': '64rem',
        '6xl': '72rem',
      },
      
      maxWidth: {
        '2xs': '16rem',
        'xs': '20rem',
        'sm': '24rem',
        'md': '28rem',
        'lg': '32rem',
        'xl': '36rem',
        '2xl': '42rem',
        '3xl': '48rem',
        '4xl': '56rem',
        '5xl': '64rem',
        '6xl': '72rem',
        '7xl': '80rem',
        '8xl': '88rem',
        '9xl': '96rem',
      },
      
      // ========================================
      //   (Backdrop)
      // ========================================
      backdropBlur: {
        xs: '2px',
        sm: '4px',
        DEFAULT: '8px',
        md: '12px',
        lg: '16px',
        xl: '24px',
        '2xl': '40px',
        '3xl': '64px',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
    require('@tailwindcss/container-queries'),
    require('@tailwindcss/line-clamp'),
    //   
    function({ addUtilities }) {
      const newUtilities = {
        //  
        '.text-gradient': {
          'background-clip': 'text',
          '-webkit-background-clip': 'text',
          '-webkit-text-fill-color': 'transparent',
        },
        //  
        '.scrollbar-hide': {
          /* IE and Edge */
          '-ms-overflow-style': 'none',
          /* Firefox */
          'scrollbar-width': 'none',
          /* Safari and Chrome */
          '&::-webkit-scrollbar': {
            display: 'none',
          },
        },
        // 
        '.glass': {
          'background': 'rgba(255, 255, 255, 0.1)',
          'backdrop-filter': 'blur(10px)',
          'border': '1px solid rgba(255, 255, 255, 0.2)',
        },
        //   
        '.no-select': {
          '-webkit-user-select': 'none',
          '-moz-user-select': 'none',
          '-ms-user-select': 'none',
          'user-select': 'none',
        },
        //   ()
        '.safe-top': {
          'padding-top': 'env(safe-area-inset-top)',
        },
        '.safe-bottom': {
          'padding-bottom': 'env(safe-area-inset-bottom)',
        },
        '.safe-left': {
          'padding-left': 'env(safe-area-inset-left)',
        },
        '.safe-right': {
          'padding-right': 'env(safe-area-inset-right)',
        },
        // Line clamp  (   )
        '.line-clamp-1': {
          'display': '-webkit-box',
          '-webkit-line-clamp': '1',
          '-webkit-box-orient': 'vertical',
          'overflow': 'hidden',
        },
        '.line-clamp-2': {
          'display': '-webkit-box',
          '-webkit-line-clamp': '2',
          '-webkit-box-orient': 'vertical',
          'overflow': 'hidden',
        },
        '.line-clamp-3': {
          'display': '-webkit-box',
          '-webkit-line-clamp': '3',
          '-webkit-box-orient': 'vertical',
          'overflow': 'hidden',
        },
      }
      addUtilities(newUtilities)
    },
  ],
}