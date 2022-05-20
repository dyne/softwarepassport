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
  safelist: [
    "alert-success",
    "alert-warning",
    "alert-info",
    "alert-error",
  ],
  plugins: [require("@tailwindcss/typography"), require("daisyui")],
}
