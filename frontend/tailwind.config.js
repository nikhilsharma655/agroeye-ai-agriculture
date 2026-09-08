/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        agro: {
          50: "#f2f8ee",
          100: "#e1efd6",
          200: "#c4dfae",
          300: "#a0cb7d",
          400: "#7db553",
          500: "#5e9a37",
          600: "#487a29",
          700: "#396023",
          800: "#2f4d20",
          900: "#28421d",
          950: "#12240c",
        },
        earth: {
          50: "#faf6f1",
          100: "#f0e6d8",
          200: "#e0cbae",
          300: "#cca77c",
          400: "#b8834f",
          500: "#a06937",
          600: "#87532c",
          700: "#6c4025",
          800: "#5a3622",
          900: "#4c2e1f",
        },
        sky: {
          50: "#eefaff",
          100: "#d9f1ff",
          400: "#38b6ea",
          500: "#1a9bd6",
        },
      },
      fontFamily: {
        display: ["'Poppins'", "sans-serif"],
        body: ["'Inter'", "sans-serif"],
      },
      boxShadow: {
        card: "0 2px 10px rgba(40, 66, 29, 0.08)",
        cardHover: "0 8px 24px rgba(40, 66, 29, 0.14)",
      },
    },
  },
  plugins: [],
}
