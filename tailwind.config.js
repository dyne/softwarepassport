module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["'Syne', sans-serif"]
      },
      colors: {
        primary: '#FCEFDF',
      }
    },
  },
  plugins: [require("@tailwindcss/typography"), require("daisyui")],
}
