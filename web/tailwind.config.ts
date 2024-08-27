import type { Config } from "tailwindcss";
import daisyui from "daisyui";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
      colors: {
        primary: {
          100: "#ffe5e5",
          200: "#ffb3b3",
          300: "#ff8080",
          400: "#ff4d4d",
          500: "#ff1a1a", // Main primary red
          600: "#e60000",
          700: "#b80000",
          800: "#8b0000",
          900: "#5e0000",
        },
        secondary: {
          100: "#f5f5f5",
          200: "#e6e6e6",
          300: "#cccccc",
          400: "#b3b3b3",
          500: "#999999", // Gray-white for secondary elements
          600: "#808080",
          700: "#666666",
          800: "#4d4d4d",
          900: "#333333",
        },
        tertiary: {
          100: "#e6e6e6",
          200: "#cccccc",
          300: "#b3b3b3",
          400: "#999999",
          500: "#808080", // Dark gray-black for accents
          600: "#666666",
          700: "#4d4d4d",
          800: "#333333",
          900: "#1a1a1a",
        },
      },
    },
  },
  plugins: [
    daisyui
  ],
};
export default config;
