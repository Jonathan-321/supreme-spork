// Theme configuration for the AgriFinance mobile app
// Designed with high contrast for sunlight visibility and cultural relevance

export const theme = {
  // Color palette designed for high visibility in sunlight
  colors: {
    // Primary colors - vibrant green representing growth and agriculture
    primary: '#1A8D1A', // Vibrant green
    primaryDark: '#146814', // Darker green for contrast
    primaryLight: '#7DC97D', // Lighter green for backgrounds
    
    // Secondary colors - warm earth tones representing soil and agriculture
    secondary: '#E67E22', // Warm orange/earth tone
    secondaryDark: '#BA6419', // Darker orange
    secondaryLight: '#F5B041', // Lighter orange
    
    // Accent colors for visual interest and cultural relevance
    accent1: '#8E44AD', // Purple - represents prosperity in many African cultures
    accent2: '#D35400', // Terracotta - represents earth/clay in traditional buildings
    accent3: '#F1C40F', // Yellow - represents sunshine and harvest
    
    // Neutral colors
    background: '#FFFFFF',
    backgroundDark: '#F5F5F5',
    backgroundLight: '#FFFFFF',
    
    // Text colors - high contrast for readability in sunlight
    text: '#212121', // Near black for maximum contrast
    textLight: '#424242',
    textInverted: '#FFFFFF',
    
    // Status colors
    success: '#27AE60',
    warning: '#F39C12',
    error: '#E74C3C',
    info: '#3498DB',
    
    // Border colors
    border: '#BDBDBD',
    borderLight: '#E0E0E0',
    
    // Risk level colors for climate and credit risk visualization
    riskLow: '#27AE60',    // Green
    riskMedium: '#F39C12', // Amber
    riskHigh: '#E74C3C',   // Red
  },
  
  // Typography
  typography: {
    fontFamily: {
      primary: '"Nunito", "Segoe UI", Roboto, "Helvetica Neue", sans-serif',
      secondary: '"Montserrat", Arial, sans-serif',
    },
    fontSize: {
      xs: '0.75rem',    // 12px
      sm: '0.875rem',   // 14px
      base: '1rem',     // 16px
      md: '1.125rem',   // 18px
      lg: '1.25rem',    // 20px
      xl: '1.5rem',     // 24px
      xxl: '1.875rem',  // 30px
      xxxl: '2.25rem',  // 36px
    },
    fontWeight: {
      light: 300,
      regular: 400,
      medium: 500,
      semiBold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.2,
      normal: 1.5,
      relaxed: 1.75,
    },
  },
  
  // Spacing
  spacing: {
    xs: '0.25rem',   // 4px
    sm: '0.5rem',    // 8px
    md: '1rem',      // 16px
    lg: '1.5rem',    // 24px
    xl: '2rem',      // 32px
    xxl: '3rem',     // 48px
  },
  
  // Borders
  borders: {
    radius: {
      sm: '0.25rem',  // 4px
      md: '0.5rem',   // 8px
      lg: '1rem',     // 16px
      xl: '1.5rem',   // 24px
      full: '9999px', // Fully rounded
    },
    width: {
      thin: '1px',
      medium: '2px',
      thick: '4px',
    },
  },
  
  // Shadows
  shadows: {
    sm: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
    md: '0 3px 6px rgba(0,0,0,0.15), 0 2px 4px rgba(0,0,0,0.12)',
    lg: '0 10px 20px rgba(0,0,0,0.15), 0 3px 6px rgba(0,0,0,0.10)',
    xl: '0 14px 28px rgba(0,0,0,0.25), 0 10px 10px rgba(0,0,0,0.22)',
  },
  
  // Breakpoints for responsive design
  breakpoints: {
    xs: '320px',
    sm: '576px',
    md: '768px',
    lg: '992px',
    xl: '1200px',
  },
  
  // Z-index scale
  zIndex: {
    base: 0,
    elevated: 1,
    dropdown: 1000,
    sticky: 1100,
    fixed: 1200,
    modalBackdrop: 1300,
    modal: 1400,
    popover: 1500,
    tooltip: 1600,
    toast: 1700,
  },
  
  // Transitions
  transitions: {
    duration: {
      fast: '150ms',
      normal: '300ms',
      slow: '500ms',
    },
    timing: {
      ease: 'ease',
      linear: 'linear',
      easeIn: 'ease-in',
      easeOut: 'ease-out',
      easeInOut: 'ease-in-out',
    },
  },
};

// Custom media queries
export const media = {
  mobile: `@media (max-width: ${theme.breakpoints.sm})`,
  tablet: `@media (min-width: ${theme.breakpoints.sm}) and (max-width: ${theme.breakpoints.lg})`,
  desktop: `@media (min-width: ${theme.breakpoints.lg})`,
  darkMode: '@media (prefers-color-scheme: dark)',
  lightMode: '@media (prefers-color-scheme: light)',
  reducedMotion: '@media (prefers-reduced-motion: reduce)',
  highContrast: '@media (prefers-contrast: high)',
  touchDevice: '@media (hover: none) and (pointer: coarse)',
  mouseDevice: '@media (hover: hover) and (pointer: fine)',
};
