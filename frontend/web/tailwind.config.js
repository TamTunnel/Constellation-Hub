/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Space-themed color palette
                'space': {
                    900: '#0a0a1a',
                    800: '#12122a',
                    700: '#1a1a3a',
                    600: '#22224a',
                    500: '#2a2a5a',
                },
                'cosmic': {
                    400: '#818cf8',
                    500: '#6366f1',
                    600: '#4f46e5',
                },
                'nebula': {
                    400: '#c084fc',
                    500: '#a855f7',
                    600: '#9333ea',
                },
                'aurora': {
                    400: '#34d399',
                    500: '#10b981',
                    600: '#059669',
                },
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
                mono: ['JetBrains Mono', 'Menlo', 'monospace'],
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'glow': 'glow 2s ease-in-out infinite alternate',
            },
            keyframes: {
                glow: {
                    '0%': { boxShadow: '0 0 5px 0 rgba(99, 102, 241, 0.5)' },
                    '100%': { boxShadow: '0 0 20px 5px rgba(99, 102, 241, 0.8)' },
                },
            },
        },
    },
    plugins: [],
}
