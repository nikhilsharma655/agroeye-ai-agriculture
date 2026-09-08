import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2 } from "lucide-react";
import { farmApi } from "../services/api";
import { PageHeader } from "../components/Common";
import { SOIL_TYPES, CROPS, titleCase } from "../utils/constants";

const initialForm = {
  name: "", location: "", area: "", soil_type: "loamy", soil_ph: "",
  nitrogen: "", phosphorus: "", potassium: "", moisture: "", temperature: "",
  humidity: "", current_crop: "", planting_date: "", expected_harvest_date: "",
};

export default function AddFarm() {
  const navigate = useNavigate();
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const payload = {
        ...form,
        area: Number(form.area),
        soil_ph: form.soil_ph ? Number(form.soil_ph) : null,
        nitrogen: form.nitrogen ? Number(form.nitrogen) : null,
        phosphorus: form.phosphorus ? Number(form.phosphorus) : null,
        potassium: form.potassium ? Number(form.potassium) : null,
        moisture: form.moisture ? Number(form.moisture) : null,
        temperature: form.temperature ? Number(form.temperature) : null,
        humidity: form.humidity ? Number(form.humidity) : null,
        planting_date: form.planting_date || null,
        expected_harvest_date: form.expected_harvest_date || null,
      };
      const farm = await farmApi.create(payload);
      navigate(`/farms/${farm.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl">
      <PageHeader title="Add a New Farm" subtitle="Tell us about your farm so AgroEye can start generating recommendations." />

      {error && (
        <div className="mb-4 rounded-xl bg-red-50 border border-red-100 px-4 py-2.5 text-sm text-red-700">{error}</div>
      )}

      <form onSubmit={handleSubmit} className="card space-y-6">
        <div>
          <h3 className="font-display font-semibold text-gray-800 mb-3">Basic Information</h3>
          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="label-field">Farm name *</label>
              <input name="name" required value={form.name} onChange={handleChange} className="input-field" placeholder="North Field" />
            </div>
            <div>
              <label className="label-field">Location</label>
              <input name="location" value={form.location} onChange={handleChange} className="input-field" placeholder="Ludhiana, Punjab" />
            </div>
            <div>
              <label className="label-field">Area (hectares) *</label>
              <input type="number" step="0.1" required name="area" value={form.area} onChange={handleChange} className="input-field" placeholder="3.2" />
            </div>
            <div>
              <label className="label-field">Soil type</label>
              <select name="soil_type" value={form.soil_type} onChange={handleChange} className="input-field">
                {SOIL_TYPES.map((s) => <option key={s} value={s}>{titleCase(s)}</option>)}
              </select>
            </div>
          </div>
        </div>

        <div>
          <h3 className="font-display font-semibold text-gray-800 mb-3">Soil & Environment</h3>
          <div className="grid sm:grid-cols-3 gap-4">
            <div>
              <label className="label-field">Soil pH</label>
              <input type="number" step="0.1" name="soil_ph" value={form.soil_ph} onChange={handleChange} className="input-field" placeholder="6.5" />
            </div>
            <div>
              <label className="label-field">Nitrogen (kg/ha)</label>
              <input type="number" step="0.1" name="nitrogen" value={form.nitrogen} onChange={handleChange} className="input-field" placeholder="60" />
            </div>
            <div>
              <label className="label-field">Phosphorus (kg/ha)</label>
              <input type="number" step="0.1" name="phosphorus" value={form.phosphorus} onChange={handleChange} className="input-field" placeholder="40" />
            </div>
            <div>
              <label className="label-field">Potassium (kg/ha)</label>
              <input type="number" step="0.1" name="potassium" value={form.potassium} onChange={handleChange} className="input-field" placeholder="40" />
            </div>
            <div>
              <label className="label-field">Moisture (%)</label>
              <input type="number" step="0.1" name="moisture" value={form.moisture} onChange={handleChange} className="input-field" placeholder="50" />
            </div>
            <div>
              <label className="label-field">Temperature (°C)</label>
              <input type="number" step="0.1" name="temperature" value={form.temperature} onChange={handleChange} className="input-field" placeholder="27" />
            </div>
            <div>
              <label className="label-field">Humidity (%)</label>
              <input type="number" step="0.1" name="humidity" value={form.humidity} onChange={handleChange} className="input-field" placeholder="65" />
            </div>
          </div>
        </div>

        <div>
          <h3 className="font-display font-semibold text-gray-800 mb-3">Current Crop</h3>
          <div className="grid sm:grid-cols-3 gap-4">
            <div>
              <label className="label-field">Crop</label>
              <select name="current_crop" value={form.current_crop} onChange={handleChange} className="input-field">
                <option value="">None</option>
                {CROPS.map((c) => <option key={c} value={c}>{titleCase(c)}</option>)}
              </select>
            </div>
            <div>
              <label className="label-field">Planting date</label>
              <input type="date" name="planting_date" value={form.planting_date} onChange={handleChange} className="input-field" />
            </div>
            <div>
              <label className="label-field">Expected harvest date</label>
              <input type="date" name="expected_harvest_date" value={form.expected_harvest_date} onChange={handleChange} className="input-field" />
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <button type="button" onClick={() => navigate(-1)} className="btn-secondary">Cancel</button>
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? <Loader2 className="animate-spin" size={18} /> : "Create Farm"}
          </button>
        </div>
      </form>
    </div>
  );
}
