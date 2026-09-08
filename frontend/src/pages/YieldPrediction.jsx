import { useState } from "react";
import { Loader2, Wheat, Sparkles } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { mlApi } from "../services/api";
import { PageHeader } from "../components/Common";
import FarmPicker from "../components/FarmPicker";
import { CROPS, titleCase } from "../utils/constants";

const initialForm = {
  crop: "rice", area_hectare: 2, nitrogen: 60, phosphorus: 40, potassium: 40,
  temperature: 26, humidity: 65, ph: 6.5, rainfall: 120, farm_id: null,
};

export default function YieldPrediction() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const numFields = [
    ["area_hectare", "Area", "ha"], ["nitrogen", "Nitrogen", "kg/ha"], ["phosphorus", "Phosphorus", "kg/ha"],
    ["potassium", "Potassium", "kg/ha"], ["temperature", "Temperature", "°C"], ["humidity", "Humidity", "%"],
    ["ph", "Soil pH", ""], ["rainfall", "Rainfall", "mm"],
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const payload = { ...form };
      numFields.forEach(([key]) => { payload[key] = Number(payload[key]); });
      setResult(await mlApi.predictYield(payload));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const chartData = result ? [
    { name: "Low", value: result.confidence_range_per_hectare.low },
    { name: "Estimate", value: result.yield_per_hectare },
    { name: "High", value: result.confidence_range_per_hectare.high },
  ] : [];

  return (
    <div>
      <PageHeader title="Crop Yield Prediction" subtitle="Estimate expected yield per hectare and total harvest before you plant." />

      <div className="grid lg:grid-cols-2 gap-5">
        <form onSubmit={handleSubmit} className="card space-y-4">
          <div>
            <label className="label-field">Crop</label>
            <select className="input-field" value={form.crop} onChange={(e) => setForm({ ...form, crop: e.target.value })}>
              {CROPS.map((c) => <option key={c} value={c}>{titleCase(c)}</option>)}
            </select>
          </div>
          <div className="grid sm:grid-cols-2 gap-4">
            {numFields.map(([key, label, unit]) => (
              <div key={key}>
                <label className="label-field">{label} {unit && <span className="text-gray-400">({unit})</span>}</label>
                <input type="number" step="0.1" required className="input-field" value={form[key]}
                  onChange={(e) => setForm({ ...form, [key]: e.target.value })} />
              </div>
            ))}
          </div>

          <FarmPicker value={form.farm_id} onChange={(id) => setForm({ ...form, farm_id: id })} />

          {error && <div className="rounded-xl bg-red-50 border border-red-100 px-4 py-2.5 text-sm text-red-700">{error}</div>}

          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? <Loader2 className="animate-spin" size={18} /> : <><Sparkles size={18} /> Predict Yield</>}
          </button>
        </form>

        <div className="card">
          <h3 className="font-display font-semibold text-gray-800 mb-4">Result</h3>
          {!result && !loading && (
            <p className="text-sm text-gray-400 text-center py-16">Fill in the form to get a yield estimate.</p>
          )}
          {loading && <p className="text-sm text-gray-400 text-center py-16">Running the model...</p>}
          {result && (
            <div>
              <div className="rounded-2xl bg-earth-600 text-white p-6 text-center mb-5">
                <Wheat className="mx-auto mb-2" size={28} />
                <p className="text-sm text-earth-100">Estimated Yield — {titleCase(result.crop)}</p>
                <p className="font-display text-3xl font-bold mt-1">{result.yield_per_hectare} {result.unit}/ha</p>
                <p className="text-earth-100 mt-1">Total: {result.estimated_total_yield} {result.unit}</p>
              </div>

              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0e6d8" />
                  <XAxis dataKey="name" fontSize={12} stroke="#9ca3af" />
                  <YAxis fontSize={12} stroke="#9ca3af" />
                  <Tooltip />
                  <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                    {chartData.map((entry, idx) => (
                      <Cell key={idx} fill={idx === 1 ? "#a06937" : "#e0cbae"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>

              {result.note && (
                <div className="rounded-xl bg-amber-50 p-3 mt-3 text-sm text-amber-800">{result.note}</div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
