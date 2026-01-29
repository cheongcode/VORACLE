import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // VALORANT Dark Theme
        valorant: {
          dark: '#0F1923',
          darker: '#0A1018',
          card: '#1A2634',
          border: '#2A3A4D',
          red: '#FF4655',
          redDark: '#BD3944',
        },
        // Cloud9 Accent
        c9: {
          cyan: '#00AEEF',
          cyanLight: '#4DCAFF',
          cyanDark: '#0088CC',
        },
        // Status Colors
        status: {
          success: '#22C55E',
          warning: '#F59E0B',
          danger: '#EF4444',
        },
        // Text Colors
        text: {
          primary: '#FFFFFF',
          secondary: '#8B9EB7',
          muted: '#5A6A7A',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['DIN 2014', 'Inter', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'valorant-gradient': 'linear-gradient(135deg, #0F1923 0%, #1A2634 50%, #0F1923 100%)',
        'card-gradient': 'linear-gradient(180deg, #1A2634 0%, #0F1923 100%)',
        'glow-cyan': 'radial-gradient(ellipse at center, rgba(0, 174, 239, 0.15) 0%, transparent 70%)',
        'glow-red': 'radial-gradient(ellipse at center, rgba(255, 70, 85, 0.15) 0%, transparent 70%)',
      },
      boxShadow: {
        'glow-sm': '0 0 15px rgba(0, 174, 239, 0.3)',
        'glow-md': '0 0 30px rgba(0, 174, 239, 0.4)',
        'glow-lg': '0 0 50px rgba(0, 174, 239, 0.5)',
        'glow-red': '0 0 30px rgba(255, 70, 85, 0.4)',
        'card': '0 4px 20px rgba(0, 0, 0, 0.4)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'slide-up': 'slideUp 0.5s ease-out',
        'fade-in': 'fadeIn 0.5s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 20px rgba(0, 174, 239, 0.4)' },
          '100%': { boxShadow: '0 0 40px rgba(0, 174, 239, 0.6)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};

export default config;
