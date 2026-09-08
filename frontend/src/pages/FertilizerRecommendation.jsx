import { useState } from "react";
import { Loader2, FlaskConical, Sparkles, Info } from "lucide-react";
import { mlApi } from "../services/api";
import { PageHeader } from "../components/Common";
import FarmPicker from "../components/FarmPicker";
import { CROPS, SOIL_TYPES, GROWTH_STAGES, titleCase } from "../utils/constants";

const initialForm = {
  crop: "rice", nitrogen: 40, phosphorus: 30, potassium: 30, ph: 6.5,
  soil_type: "loamy", growth_stage: "vegetative", farm_id: null,
};

const deficiencyTone = { sufficient: "text-agro-700 bg-agro-50", "mildly deficient": "text-amber-700 bg-amber-50", "significantly deficient": "text-red-700 bg-red-50" };

export default function FertilizerRecommendation() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const payload = { ...form, nitrogen: Number(form.nitrogen), phosphorus: Number(form.phosphorus),
        potassium: Number(form.potassium), ph: Number(form.ph) };
      setResult(await mlApi.recommendFertilizer(payload));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <PageHeader title="Fertilizer Recommendation" subtitle="Find out which nutrients your soil needs and roughly how much to apply." />

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
            <div>
              <label className="label-field">Soil Type</label>
              <select className="input-field" value={form.soil_type} onChange={(e) => setForm({ ...form, soil_type: e.target.value })}>
                {SOIL_TYPES.map((s) => <option key={s} value={s}>{titleCase(s)}</option>)}
              </select>
            </div>
            <div>
              <label className="label-field">Soil pH</label>
              <input type="number" step="0.1" className="input-field" value={form.ph} onChange={(e) => setForm({ ...form, ph: e.target.value })} />
            </div>
            <div>
              <label className="label-field">Nitrogen (kg/ha)</label>
              <input type="number" step="0.1" className="input-field" value={form.nitrogen} onChange={(e) => setForm({ ...form, nitrogen: e.target.value })} />
            </div>
            <div>
              <label className="label-field">Phosphorus (kg/ha)</label>
              <input type="number" step="0.1" className="input-field" value={form.phosphorus} onChange={(e) => setForm({ ...form, phosphorus: e.target.value })} />
            </div>
            <div>
              <label className="label-field">Potassium (kg/ha)</label>
              <input type="number" step="0.1" className="input-field" value={form.potassium} onChange={(e) => setForm({ ...form, potassium: e.target.value })} />
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
          {!result && !loading && <p className="text-sm text-gray-400 text-center py-16">Fill in the form to get a fertilizer plan.</p>}
          {loading && <p className="text-sm text-gray-400 text-center py-16">Calculating...</p>}
          {result && (
            <div>
              <div className="rounded-2xl bg-earth-500 text-white p-5 mb-5 flex items-center gap-4">
                <FlaskConical size={28} />
                <div>
                  <p className="text-sm text-earth-50">Recommended Fertilizer</p>
                  <p className="font-display text-lg font-bold">{result.recommended_fertilizer.join(", ")}</p>
                </div>
              </div>

              <h4 className="text-sm font-semibold text-gray-700 mb-2">Nutrient Deficiency</h4>
              <div className="grid grid-cols-3 gap-2 mb-5">
                {Object.entries(result.nutrient_deficiency).map(([nutrient, status]) => (
                  <div key={nutrient} className={`rounded-xl p-3 text-center ${deficiencyTone[status]}`}>
                    <p className="font-display font-bold">{nutrient}</p>
                    <p className="text-xs mt-1">{status}</p>
                    <p className="text-xs font-semibold mt-1">
                      +{result.approximate_quantity_kg_per_hectare[nutrient]} kg/ha
                    </p>
                  </div>
                ))}
              </div>

              <div className="rounded-xl bg-gray-50 p-4 text-sm text-gray-600 mb-3">{result.reason}</div>
              <div className="flex items-start gap-2 text-xs text-amber-700 bg-amber-50 rounded-xl p-3">
                <Info size={14} className="mt-0.5 shrink-0" /> {result.disclaimer}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
