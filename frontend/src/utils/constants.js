export const SOIL_TYPES = ["loamy", "sandy", "clay", "black", "red"];

export const CROPS = [
  "rice", "maize", "chickpea", "kidneybeans", "wheat", "cotton", "sugarcane",
  "banana", "coffee", "mango", "grapes", "watermelon", "lentil", "orange", "coconut",
];

export const GROWTH_STAGES = ["seedling", "vegetative", "flowering", "maturity"];

export function formatDate(dateStr) {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

export function titleCase(str) {
  if (!str) return "";
  return str.charAt(0).toUpperCase() + str.slice(1);
}
