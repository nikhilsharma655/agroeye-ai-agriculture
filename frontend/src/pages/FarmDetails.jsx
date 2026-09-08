import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { MapPin, Pencil, Trash2, Plus, Lightbulb, Leaf, CloudSun, Loader2 } from "lucide-react";
import { farmApi, cropApi } from "../services/api";
import { Loader, ErrorState, SeverityBadge, EmptyState } from "../components/Feedback";
import { PageHeader } from "../components/Common";
import { titleCase, formatDate, CROPS, GROWTH_STAGES } from "../utils/constants";

export default function FarmDetails() {
  const { farmId } = useParams();
  const navigate = useNavigate();
  const [farm, setFarm] = useState(null);
  const [crops, setCrops] = useState([]);
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState({});
  const [showAddCrop, setShowAddCrop] = useState(false);
  const [cropForm, setCropForm] = useState({ name: "rice", variety: "", growth_stage: "seedling" });
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [weatherError, setWeatherError] = useState("");
  const [weatherResult, setWeatherResult] = useState(null);

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const [f, c, ins] = await Promise.all([
        farmApi.get(farmId), cropApi.list(farmId), farmApi.insights(farmId),
      ]);
      setFarm(f);
      setEditForm(f);
      setCrops(c);
      setInsights(ins.insights);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [farmId]);

  const handleSaveEdit = async () => {
    try {
      const updated = await farmApi.update(farmId, {
        ...editForm,
        area: Number(editForm.area),
        soil_ph: editForm.soil_ph ? Number(editForm.soil_ph) : null,
        nitrogen: editForm.nitrogen ? Number(editForm.nitrogen) : null,
        phosphorus: editForm.phosphorus ? Number(editForm.phosphorus) : null,
        potassium: editForm.potassium ? Number(editForm.potassium) : null,
        moisture: editForm.moisture ? Number(editForm.moisture) : null,
      });
      setFarm(updated);
      setEditing(false);
      load();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleDeleteFarm = async () => {
    if (!window.confirm("Delete this farm permanently?")) return;
    await farmApi.remove(farmId);
    navigate("/farms");
  };

  const handleAddCrop = async (e) => {
    e.preventDefault();
    try {
      await cropApi.add(farmId, cropForm);
      setShowAddCrop(false);
      setCropForm({ name: "rice", variety: "", growth_stage: "seedling" });
      load();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleDeleteCrop = async (cropId) => {
    if (!window.confirm("Remove this crop entry?")) return;
    await cropApi.remove(cropId);
    load();
  };

  const handleRefreshWeather = async () => {
    setWeatherLoading(true);
    setWeatherError("");
    setWeatherResult(null);
    try {
      const result = await farmApi.refreshWeather(farmId);
      setWeatherResult(result);
      load();
    } catch (err) {
      setWeatherError(err.message);
    } finally {
      setWeatherLoading(false);
    }
  };

  if (loading) return <Loader label="Loading farm details..." />;
  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!farm) return null;

  const fields = [
    ["soil_type", "Soil Type"], ["soil_ph", "Soil pH"], ["nitrogen", "Nitrogen"],
    ["phosphorus", "Phosphorus"], ["potassium", "Potassium"], ["moisture", "Moisture"],
    ["temperature", "Temperature"], ["humidity", "Humidity"],
  ];

  return (
    <div>
      <PageHeader
        title={farm.name}
        subtitle={farm.location ? (
          <span className="flex items-center gap-1"><MapPin size={13} /> {farm.location}</span>
        ) : null}
        action={
          <div className="flex gap-2">
            <button onClick={() => setEditing((v) => !v)} className="btn-secondary">
              <Pencil size={16} /> {editing ? "Cancel Edit" : "Edit Farm"}
            </button>
            <button onClick={handleDeleteFarm} className="btn-secondary text-red-600 hover:bg-red-50">
              <Trash2 size={16} /> Delete
            </button>
          </div>
        }
      />

      <div className="grid lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2 space-y-5">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-display font-semibold text-gray-800 flex items-center gap-2">
                <CloudSun size={18} className="text-sky-600" /> Live Weather
              </h3>
              <button onClick={handleRefreshWeather} disabled={weatherLoading} className="btn-secondary text-sm py-1.5 px-3">
                {weatherLoading ? <Loader2 className="animate-spin" size={14} /> : "Refresh from location"}
              </button>
            </div>
            {weatherError && (
              <div className="rounded-xl bg-red-50 border border-red-100 px-4 py-2.5 text-sm text-red-700">{weatherError}</div>
            )}
            {weatherResult && (
              <div className="grid grid-cols-3 gap-3 text-center">
                <div className="rounded-xl bg-sky-50 p-3">
                  <p className="text-xs text-sky-700">Temperature</p>
                  <p className="font-display text-xl font-bold text-sky-800">{weatherResult.temperature}°C</p>
                </div>
                <div className="rounded-xl bg-sky-50 p-3">
                  <p className="text-xs text-sky-700">Humidity</p>
                  <p className="font-display text-xl font-bold text-sky-800">{weatherResult.humidity}%</p>
                </div>
                <div className="rounded-xl bg-sky-50 p-3">
                  <p className="text-xs text-sky-700">Rainfall</p>
                  <p className="font-display text-xl font-bold text-sky-800">{weatherResult.rainfall}mm</p>
                </div>
                <p className="col-span-3 text-xs text-gray-400 mt-1">
                  {weatherResult.resolved_location} • farm temperature & humidity updated
                </p>
              </div>
            )}
            {!weatherResult && !weatherError && (
              <p className="text-sm text-gray-400">
                Pull live temperature, humidity, and rainfall for this farm's location instead of entering it manually.
              </p>
            )}
          </div>

          <div className="card">
            <h3 className="font-display font-semibold text-gray-800 mb-4">Soil & Environment</h3>
            {editing ? (
              <div className="grid sm:grid-cols-2 gap-4">
                {fields.map(([key, label]) => (
                  <div key={key}>
                    <label className="label-field">{label}</label>
                    <input
                      className="input-field"
                      value={editForm[key] ?? ""}
                      onChange={(e) => setEditForm({ ...editForm, [key]: e.target.value })}
                    />
                  </div>
                ))}
                <div className="sm:col-span-2 flex justify-end gap-2 pt-2">
                  <button onClick={handleSaveEdit} className="btn-primary">Save Changes</button>
                </div>
              </div>
            ) : (
              <div className="grid sm:grid-cols-4 gap-4">
                {fields.map(([key, label]) => (
                  <div key={key}>
                    <p className="text-xs text-gray-500">{label}</p>
                    <p className="font-semibold text-gray-800">
                      {farm[key] != null && farm[key] !== "" ? (key === "soil_type" ? titleCase(farm[key]) : farm[key]) : "—"}
                    </p>
                  </div>
                ))}
                <div>
                  <p className="text-xs text-gray-500">Area</p>
                  <p className="font-semibold text-gray-800">{farm.area} ha</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Current Crop</p>
                  <p className="font-semibold text-gray-800">{farm.current_crop ? titleCase(farm.current_crop) : "—"}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Planted</p>
                  <p className="font-semibold text-gray-800">{formatDate(farm.planting_date)}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Expected Harvest</p>
                  <p className="font-semibold text-gray-800">{formatDate(farm.expected_harvest_date)}</p>
                </div>
              </div>
            )}
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-display font-semibold text-gray-800 flex items-center gap-2">
                <Leaf size={18} className="text-agro-600" /> Crops
              </h3>
              <button onClick={() => setShowAddCrop((v) => !v)} className="btn-secondary text-sm py-1.5 px-3">
                <Plus size={14} /> Add Crop
              </button>
            </div>

            {showAddCrop && (
              <form onSubmit={handleAddCrop} className="mb-4 rounded-xl border border-agro-100 p-4 grid sm:grid-cols-3 gap-3">
                <select className="input-field" value={cropForm.name} onChange={(e) => setCropForm({ ...cropForm, name: e.target.value })}>
                  {CROPS.map((c) => <option key={c} value={c}>{titleCase(c)}</option>)}
                </select>
                <input className="input-field" placeholder="Variety (optional)" value={cropForm.variety}
                  onChange={(e) => setCropForm({ ...cropForm, variety: e.target.value })} />
                <select className="input-field" value={cropForm.growth_stage}
                  onChange={(e) => setCropForm({ ...cropForm, growth_stage: e.target.value })}>
                  {GROWTH_STAGES.map((s) => <option key={s} value={s}>{titleCase(s)}</option>)}
                </select>
                <button type="submit" className="btn-primary sm:col-span-3">Save Crop</button>
              </form>
            )}

            {crops.length ? (
              <div className="divide-y divide-agro-50">
                {crops.map((crop) => (
                  <div key={crop.id} className="flex items-center justify-between py-3">
                    <div>
                      <p className="font-medium text-gray-800">{titleCase(crop.name)} {crop.variety && `(${crop.variety})`}</p>
                      <p className="text-xs text-gray-500">Stage: {titleCase(crop.growth_stage)} • Status: {titleCase(crop.status)}</p>
                    </div>
                    <button onClick={() => handleDeleteCrop(crop.id)} className="text-gray-300 hover:text-red-500">
                      <Trash2 size={16} />
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-400 text-center py-6">No crops recorded yet.</p>
            )}
          </div>
        </div>

        <div className="card h-fit">
          <h3 className="font-display font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Lightbulb size={18} className="text-amber-500" /> Insights
          </h3>
          {insights.length ? (
            <div className="space-y-3">
              {insights.map((insight, idx) => (
                <div key={idx} className="rounded-xl border border-agro-100 p-3.5">
                  <div className="flex items-center gap-2 mb-1.5">
                    <SeverityBadge severity={insight.severity} />
                    <span className="text-xs text-gray-400 uppercase tracking-wide">{insight.category}</span>
                  </div>
                  <p className="text-sm font-semibold text-gray-800">{insight.title}</p>
                  <p className="text-xs text-gray-500 mt-1">{insight.explanation}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-400 text-center py-6">No insights available.</p>
          )}
        </div>
      </div>
    </div>
  );
}
