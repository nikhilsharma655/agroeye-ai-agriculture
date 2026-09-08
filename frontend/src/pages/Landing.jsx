import { Link } from "react-router-dom";
import {
  Leaf, Sprout, Wheat, Droplets, ShieldAlert, FlaskConical,
  ArrowRight, BarChart3, Zap,
} from "lucide-react";

const FEATURES = [
  { icon: Sprout, title: "AI Crop Recommendation", desc: "Get the top crops suited to your soil, climate, and season — ranked by confidence score." },
  { icon: Wheat, title: "Yield Prediction", desc: "Estimate expected yield per hectare before you plant, based on real environmental data." },
  { icon: FlaskConical, title: "Fertilizer Guidance", desc: "Know exactly which nutrients your soil is missing and how much to apply." },
  { icon: ShieldAlert, title: "Disease Risk Alerts", desc: "Catch disease risk early with predictive alerts sent straight to your phone." },
  { icon: Droplets, title: "Smart Irrigation", desc: "Backend-calculated water requirements so you never over- or under-water." },
  { icon: BarChart3, title: "Farm Analytics", desc: "Track soil health, moisture, and yield history across every farm you manage." },
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-[#f7faf5]">
      <header className="flex items-center justify-between px-6 lg:px-12 py-5 max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
          <div className="rounded-xl bg-agro-600 p-2 text-white">
            <Leaf size={20} />
          </div>
          <span className="font-display text-xl font-bold text-agro-900">AgroEye</span>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/login" className="btn-secondary">Sign in</Link>
          <Link to="/register" className="btn-primary">Get started <ArrowRight size={16} /></Link>
        </div>
      </header>

      <section className="max-w-6xl mx-auto px-6 lg:px-12 pt-16 pb-24 text-center">
        <span className="inline-flex items-center gap-2 rounded-full bg-agro-100 text-agro-800 px-4 py-1.5 text-sm font-medium mb-6">
          <Zap size={14} /> AI-powered decisions for real farms
        </span>
        <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-bold text-agro-950 leading-tight max-w-4xl mx-auto">
          Grow smarter with an AI assistant built for farmers
        </h1>
        <p className="mt-6 text-lg text-gray-600 max-w-2xl mx-auto">
          AgroEye turns your soil, weather, and crop data into clear recommendations — what to plant,
          how much to fertilize, when to irrigate, and how to catch disease before it spreads.
        </p>
        <div className="mt-10 flex items-center justify-center gap-4">
          <Link to="/register" className="btn-primary text-base px-7 py-3">
            Start free <ArrowRight size={18} />
          </Link>
          <Link to="/login" className="btn-secondary text-base px-7 py-3">
            I already have an account
          </Link>
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-6 lg:px-12 pb-24">
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {FEATURES.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="card hover:shadow-cardHover transition-shadow">
              <div className="h-11 w-11 rounded-xl bg-agro-100 text-agro-700 flex items-center justify-center mb-4">
                <Icon size={22} />
              </div>
              <h3 className="font-display font-semibold text-gray-900">{title}</h3>
              <p className="text-sm text-gray-500 mt-1.5">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="border-t border-agro-100 py-8 text-center text-sm text-gray-500">
        © {new Date().getFullYear()} AgroEye. Built to help farmers make better decisions.
      </footer>
    </div>
  );
}
