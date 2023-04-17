/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./src/**/*.{js,jsx,ts,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['"Segoe UI Semibold"', 'sans-serif'],
            },
            colors: {
                'primary-green': '#51B60D',
                'secondary-grey': '#313131',
            },
        },
    },
    plugins: [],
};