import { useState } from "react";
import { Loader2, Leaf, Sparkles } from "lucide-react";
import { mlApi } from "../services/api";
import { PageHeader } from "../components/Common";
import FarmPicker from "../components/FarmPicker";
import { SOIL_TYPES, titleCase } from "../utils/constants";

const initialForm = {
  nitrogen: 60, phosphorus: 40, potassium: 40, temperature: 26,
  humidity: 65, ph: 6.5, rainfall: 120, soil_type: "loamy", farm_id: null,
};

export default function CropRecommendation() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const numFields = [
    ["nitrogen", "Nitrogen (N)", "kg/ha"], ["phosphorus", "Phosphorus (P)", "kg/ha"],
    ["potassium", "Potassium (K)", "kg/ha"], ["temperature", "Temperature", "°C"],
    ["humidity", "Humidity", "%"], ["ph", "Soil pH", ""], ["rainfall", "Rainfall", "mm"],
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const payload = { ...form };
      numFields.forEach(([key]) => { payload[key] = Number(payload[key]); });
      setResult(await mlApi.recommendCrop(payload));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <PageHeader title="AI Crop Recommendation" subtitle="Enter your soil and climate readings to get the best-suited crops, ranked by AI confidence." />

      <div className="grid lg:grid-cols-2 gap-5">
        <form onSubmit={handleSubmit} className="card space-y-4">
          <div className="grid sm:grid-cols-2 gap-4">
            {numFields.map(([key, label, unit]) => (
              <div key={key}>
                <label className="label-field">{label} {unit && <span className="text-gray-400">({unit})</span>}</label>
                <input type="number" step="0.1" required className="input-field" value={form[key]}
                  onChange={(e) => setForm({ ...form, [key]: e.target.value })} />
              </div>
            ))}
            <div>
              <label className="label-field">Soil Type</label>
              <select className="input-field" value={form.soil_type} onChange={(e) => setForm({ ...form, soil_type: e.target.value })}>
                {SOIL_TYPES.map((s) => <option key={s} value={s}>{titleCase(s)}</option>)}
              </select>
            </div>
          </div>

          <FarmPicker value={form.farm_id} onChange={(id) => setForm({ ...form, farm_id: id })} />

          {error && <div className="rounded-xl bg-red-50 border border-red-100 px-4 py-2.5 text-sm text-red-700">{error}</div>}

          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? <Loader2 className="animate-spin" size={18} /> : <><Sparkles size={18} /> Get Recommendation</>}
          </button>
        </form>

        <div className="card">
          <h3 className="font-display font-semibold text-gray-800 mb-4">Result</h3>
          {!result && !loading && (
            <p className="text-sm text-gray-400 text-center py-16">Fill in the form to get an AI-powered crop recommendation.</p>
          )}
          {loading && <p className="text-sm text-gray-400 text-center py-16">Running the model...</p>}
          {result && (
            <div>
              <div className="rounded-2xl bg-agro-600 text-white p-6 text-center mb-5">
                <Leaf className="mx-auto mb-2" size={28} />
                <p className="text-sm text-agro-100">Recommended Crop</p>
                <p className="font-display text-3xl font-bold mt-1">{titleCase(result.recommended_crop)}</p>
                <p className="text-agro-100 mt-1">Suitability: {result.suitability_score}%</p>
              </div>

              <h4 className="text-sm font-semibold text-gray-700 mb-2">Other suitable crops</h4>
              <div className="space-y-2 mb-5">
                {result.top_recommendations.map((c, idx) => (
                  <div key={c.crop} className="flex items-center gap-3">
                    <span className="text-xs text-gray-400 w-4">{idx + 1}.</span>
                    <span className="text-sm font-medium text-gray-700 w-24">{titleCase(c.crop)}</span>
                    <div className="flex-1 h-2 rounded-full bg-agro-50 overflow-hidden">
                      <div className="h-full bg-agro-500" style={{ width: `${c.confidence}%` }} />
                    </div>
                    <span className="text-xs text-gray-500 w-10 text-right">{c.confidence}%</span>
                  </div>
                ))}
              </div>

              <div className="rounded-xl bg-agro-50 p-4">
                <p className="text-sm text-gray-600">{result.explanation}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
