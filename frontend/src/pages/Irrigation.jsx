import { useState } from "react";
import { Loader2, Droplets, Sparkles } from "lucide-react";
import { mlApi } from "../services/api";
import { PageHeader } from "../components/Common";
import FarmPicker from "../components/FarmPicker";
import { CROPS, GROWTH_STAGES, titleCase } from "../utils/constants";

const initialForm = {
  crop: "rice", soil_moisture: 40, temperature: 30, humidity: 55, rainfall: 20,
  growth_stage: "vegetative", area_hectare: 2, farm_id: null,
};

const statusTone = {
  Adequate: "bg-agro-600", Moderate: "bg-sky-500", Low: "bg-amber-500", Critical: "bg-red-600",
};

export default function Irrigation() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const numFields = [
    ["soil_moisture", "Soil Moisture", "%"], ["temperature", "Temperature", "°C"],
    ["humidity", "Humidity", "%"], ["rainfall", "Recent Rainfall", "mm"], ["area_hectare", "Area", "ha"],
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const payload = { ...form };
      numFields.forEach(([key]) => { payload[key] = Number(payload[key]); });
      setResult(await mlApi.recommendIrrigation(payload));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <PageHeader title="Irrigation Recommendation" subtitle="Know exactly how much water your crop needs — calculated in the backend, not guessed." />

      <div className="grid lg:grid-cols-2 gap-5">
        <form onSubmit={handleSubmit} className="card space-y-4">
          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="label-field">Crop</label>
              <select className="input-field" value={form.crop} onChange={(e) => setForm({ ...form, crop: e.target.value })}>
                {CROPS.map((c) => <option key={c} value={c}>{titleCase(c)}</option>)}
              </select>
            </div>
            <div>
              <label className="label-field">Growth Stage</label>
              <select className="input-field" value={form.growth_stage} onChange={(e) => setForm({ ...form, growth_stage: e.target.value })}>
                {GROWTH_STAGES.map((s) => <option key={s} value={s}>{titleCase(s)}</option>)}
              </select>
            </div>
            {numFields.map(([key, label, unit]) => (
              <div key={key}>
                <label className="label-field">{label} <span className="text-gray-400">({unit})</span></label>
                <input type="number" step="0.1" className="input-field" value={form[key]}
                  onChange={(e) => setForm({ ...form, [key]: e.target.value })} />
              </div>
            ))}
          </div>

          <FarmPicker value={form.farm_id} onChange={(id) => setForm({ ...form, farm_id: id })} />

          {error && <div className="rounded-xl bg-red-50 border border-red-100 px-4 py-2.5 text-sm text-red-700">{error}</div>}

          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? <Loader2 className="animate-spin" size={18} /> : <><Sparkles size={18} /> Get Irrigation Plan</>}
          </button>
        </form>

        <div className="card">
          <h3 className="font-display font-semibold text-gray-800 mb-4">Result</h3>
          {!result && !loading && <p className="text-sm text-gray-400 text-center py-16">Fill in the form to get an irrigation recommendation.</p>}
          {loading && <p className="text-sm text-gray-400 text-center py-16">Calculating water balance...</p>}
          {result && (
            <div>
              <div className={`rounded-2xl ${statusTone[result.water_status]} text-white p-6 text-center mb-5`}>
                <Droplets className="mx-auto mb-2" size={28} />
                <p className="text-sm opacity-90">Water Status</p>
                <p className="font-display text-3xl font-bold mt-1">{result.water_status}</p>
                <p className="opacity-90 mt-1">
                  {result.irrigation_required ? `Irrigation recommended: ${result.recommended_level}` : "No irrigation needed"}
                </p>
              </div>

              {result.irrigation_required && (
                <div className="rounded-xl bg-sky-50 p-4 text-center mb-4">
                  <p className="text-xs text-sky-700">Estimated requirement</p>
                  <p className="font-display text-xl font-bold text-sky-800">
                    {result.estimated_requirement_litres.low.toLocaleString()}–{result.estimated_requirement_litres.high.toLocaleString()} litres
                  </p>
                </div>
              )}

              <div className="rounded-xl bg-gray-50 p-4 text-sm text-gray-600">{result.reason}</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
