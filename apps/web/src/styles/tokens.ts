/**
 * VORACLE Design System Tokens
 * 
 * VALORANT dark theme with Cloud9 cyan accents
 * JetBrains-inspired clean typography
 */

export const tokens = {
  colors: {
    // VALORANT Dark Background
    bg: {
      primary: '#0F1923',
      secondary: '#1A2634',
      card: '#1F2D3D',
      elevated: '#243447',
    },
    
    // Border Colors
    border: {
      default: '#2A3A4D',
      hover: '#3A4A5D',
      active: '#00AEEF',
      subtle: '#1E2E3E',
    },
    
    // Cloud9 Cyan Accent
    accent: {
      primary: '#00AEEF',
      light: '#4DCAFF',
      dark: '#0088CC',
      muted: 'rgba(0, 174, 239, 0.15)',
    },
    
    // VALORANT Red
    red: {
      primary: '#FF4655',
      dark: '#BD3944',
      muted: 'rgba(255, 70, 85, 0.15)',
    },
    
    // Severity Colors
    severity: {
      high: '#FF4655',
      med: '#F59E0B',
      low: '#22C55E',
    },
    
    // Confidence Colors
    confidence: {
      high: '#22C55E',
      medium: '#F59E0B',
      low: '#6B7280',
    },
    
    // Status Colors
    status: {
      success: '#22C55E',
      warning: '#F59E0B',
      danger: '#EF4444',
      info: '#00AEEF',
    },
    
    // Text Colors
    text: {
      primary: '#FFFFFF',
      secondary: '#8B9EB7',
      muted: '#5A6A7A',
      inverse: '#0F1923',
    },
    
    // Map Veto Colors
    veto: {
      ban: '#FF4655',
      pick: '#22C55E',
      neutral: '#6B7280',
    },
  },
  
  // Border Radius
  radius: {
    xs: '2px',
    sm: '4px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    '2xl': '20px',
    full: '9999px',
  },
  
  // Shadows
  shadows: {
    sm: '0 1px 2px rgba(0, 0, 0, 0.3)',
    md: '0 4px 6px rgba(0, 0, 0, 0.3)',
    lg: '0 10px 15px rgba(0, 0, 0, 0.3)',
    xl: '0 20px 25px rgba(0, 0, 0, 0.3)',
    card: '0 4px 20px rgba(0, 0, 0, 0.4)',
    glow: '0 0 20px rgba(0, 174, 239, 0.4)',
    glowStrong: '0 0 40px rgba(0, 174, 239, 0.6)',
    glowRed: '0 0 20px rgba(255, 70, 85, 0.4)',
  },
  
  // Spacing
  spacing: {
    '0': '0',
    px: '1px',
    '0.5': '2px',
    '1': '4px',
    '1.5': '6px',
    '2': '8px',
    '2.5': '10px',
    '3': '12px',
    '4': '16px',
    '5': '20px',
    '6': '24px',
    '8': '32px',
    '10': '40px',
    '12': '48px',
    '16': '64px',
    '20': '80px',
  },
  
  // Typography
  typography: {
    fontFamily: {
      sans: "'Inter', system-ui, -apple-system, sans-serif",
      mono: "'JetBrains Mono', 'Fira Code', monospace",
      display: "'Inter', system-ui, sans-serif",
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem',
      '5xl': '3rem',
    },
    fontWeight: {
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
      extrabold: '800',
    },
    lineHeight: {
      none: '1',
      tight: '1.25',
      snug: '1.375',
      normal: '1.5',
      relaxed: '1.625',
      loose: '2',
    },
    letterSpacing: {
      tighter: '-0.05em',
      tight: '-0.025em',
      normal: '0',
      wide: '0.025em',
      wider: '0.05em',
      widest: '0.1em',
    },
  },
  
  // Animation
  animation: {
    duration: {
      fast: '150ms',
      normal: '300ms',
      slow: '500ms',
    },
    easing: {
      default: 'cubic-bezier(0.4, 0, 0.2, 1)',
      in: 'cubic-bezier(0.4, 0, 1, 1)',
      out: 'cubic-bezier(0, 0, 0.2, 1)',
      inOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    },
  },
  
  // Z-Index
  zIndex: {
    hide: -1,
    auto: 'auto',
    base: 0,
    docked: 10,
    dropdown: 1000,
    sticky: 1100,
    banner: 1200,
    overlay: 1300,
    modal: 1400,
    popover: 1500,
    skipLink: 1600,
    toast: 1700,
    tooltip: 1800,
  },
};

// Semantic color aliases
export const semanticColors = {
  // Backgrounds
  background: tokens.colors.bg.primary,
  surface: tokens.colors.bg.card,
  elevated: tokens.colors.bg.elevated,
  
  // Interactive
  interactive: tokens.colors.accent.primary,
  interactiveHover: tokens.colors.accent.light,
  interactiveActive: tokens.colors.accent.dark,
  
  // Feedback
  success: tokens.colors.status.success,
  warning: tokens.colors.status.warning,
  error: tokens.colors.status.danger,
  info: tokens.colors.status.info,
  
  // Text
  textPrimary: tokens.colors.text.primary,
  textSecondary: tokens.colors.text.secondary,
  textMuted: tokens.colors.text.muted,
};

export default tokens;
