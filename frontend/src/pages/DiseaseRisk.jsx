import { useState } from "react";
import { Loader2, ShieldAlert, Sparkles, CheckCircle2 } from "lucide-react";
import { mlApi } from "../services/api";
import { PageHeader } from "../components/Common";
import FarmPicker from "../components/FarmPicker";
import { SeverityBadge } from "../components/Feedback";
import { CROPS, GROWTH_STAGES, titleCase } from "../utils/constants";

const initialForm = {
  crop: "rice", temperature: 28, humidity: 80, rainfall: 150, soil_moisture: 60,
  growth_stage: "vegetative", previous_disease_history: false, farm_id: null,
};

export default function DiseaseRisk() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const numFields = [
    ["temperature", "Temperature", "°C"], ["humidity", "Humidity", "%"],
    ["rainfall", "Rainfall", "mm"], ["soil_moisture", "Soil Moisture", "%"],
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const payload = { ...form };
      numFields.forEach(([key]) => { payload[key] = Number(payload[key]); });
      setResult(await mlApi.predictDisease(payload));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const riskColor = { low: "bg-agro-600", medium: "bg-amber-500", high: "bg-red-600" };

  return (
    <div>
      <PageHeader title="Crop Disease Risk" subtitle="Predict disease risk from environmental conditions and catch problems early." />

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

          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input type="checkbox" checked={form.previous_disease_history}
              onChange={(e) => setForm({ ...form, previous_disease_history: e.target.checked })}
              className="rounded border-agro-300 text-agro-600 focus:ring-agro-400" />
            This crop/field has a history of disease
          </label>

          <FarmPicker value={form.farm_id} onChange={(id) => setForm({ ...form, farm_id: id })} />

          {error && <div className="rounded-xl bg-red-50 border border-red-100 px-4 py-2.5 text-sm text-red-700">{error}</div>}

          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? <Loader2 className="animate-spin" size={18} /> : <><Sparkles size={18} /> Check Disease Risk</>}
          </button>
        </form>

        <div className="card">
          <h3 className="font-display font-semibold text-gray-800 mb-4">Result</h3>
          {!result && !loading && <p className="text-sm text-gray-400 text-center py-16">Fill in the form to check disease risk.</p>}
          {loading && <p className="text-sm text-gray-400 text-center py-16">Analyzing conditions...</p>}
          {result && (
            <div>
              <div className={`rounded-2xl ${riskColor[result.risk_level]} text-white p-6 text-center mb-5`}>
                <ShieldAlert className="mx-auto mb-2" size={28} />
                <p className="text-sm opacity-90">Disease Risk Level</p>
                <p className="font-display text-3xl font-bold mt-1">{titleCase(result.risk_level)}</p>
                <p className="opacity-90 mt-1">{result.risk_percentage}% confidence</p>
              </div>

              <div className="flex items-center gap-2 mb-4">
                <span className="text-sm font-semibold text-gray-700">Possible concern:</span>
                <SeverityBadge severity={result.risk_level} />
                <span className="text-sm text-gray-600">{result.possible_disease_category}</span>
              </div>

              <h4 className="text-sm font-semibold text-gray-700 mb-2">Preventive Suggestions</h4>
              <ul className="space-y-2">
                {result.preventive_suggestions.map((tip, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                    <CheckCircle2 size={16} className="text-agro-600 mt-0.5 shrink-0" /> {tip}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
