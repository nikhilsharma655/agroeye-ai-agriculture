import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { analyticsApi, farmApi } from "../services/api";
import { PageHeader } from "../components/Common";
import { Loader, ErrorState, EmptyState } from "../components/Feedback";
import { titleCase } from "../utils/constants";

export default function Analytics() {
  const [farms, setFarms] = useState([]);
  const [selectedFarm, setSelectedFarm] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadFarms = async () => {
    setLoading(true);
    setError("");
    try {
      const fl = await farmApi.list();
      setFarms(fl);
      if (fl.length) setSelectedFarm(fl[0].id);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadFarms(); }, []);

  useEffect(() => {
    if (!selectedFarm) return;
    analyticsApi.farmHistory(selectedFarm).then(setHistory).catch((err) => setError(err.message));
  }, [selectedFarm]);

  if (loading) return <Loader label="Loading analytics..." />;
  if (error) return <ErrorState message={error} onRetry={loadFarms} />;
  if (!farms.length) return <EmptyState title="No data yet" message="Add a farm and run a few predictions to see analytics here." />;

  const byType = (type) =>
    history
      .filter((h) => h.type === type)
      .map((h, idx) => ({ name: `#${idx + 1}`, ...h.output }));

  const yieldData = byType("yield_prediction").map((d) => ({ name: d.name, yield: d.yield_per_hectare }));
  const diseaseData = byType("disease_risk").map((d) => ({ name: d.name, risk: d.risk_percentage }));
  const cropData = byType("crop_recommendation").map((d) => ({ name: d.name, confidence: d.suitability_score }));

  return (
    <div>
      <PageHeader
        title="Analytics"
        subtitle="Historical predictions and trends for your farms."
        action={
          <select className="input-field w-56" value={selectedFarm} onChange={(e) => setSelectedFarm(e.target.value)}>
            {farms.map((f) => <option key={f.id} value={f.id}>{f.name}</option>)}
          </select>
        }
      />

      {!history.length ? (
        <EmptyState title="No prediction history yet" message="Run a crop, yield, or disease prediction linked to this farm to see trends here." />
      ) : (
        <div className="grid lg:grid-cols-2 gap-5">
          {yieldData.length > 0 && (
            <div className="card">
              <h3 className="font-display font-semibold text-gray-800 mb-4">Yield Prediction History (t/ha)</h3>
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={yieldData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5efdb" />
                  <XAxis dataKey="name" fontSize={12} />
                  <YAxis fontSize={12} />
                  <Tooltip />
                  <Line type="monotone" dataKey="yield" stroke="#487a29" strokeWidth={2.5} dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {diseaseData.length > 0 && (
            <div className="card">
              <h3 className="font-display font-semibold text-gray-800 mb-4">Disease Risk History (%)</h3>
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={diseaseData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#fde8e8" />
                  <XAxis dataKey="name" fontSize={12} />
                  <YAxis fontSize={12} />
                  <Tooltip />
                  <Line type="monotone" dataKey="risk" stroke="#dc2626" strokeWidth={2.5} dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {cropData.length > 0 && (
            <div className="card lg:col-span-2">
              <h3 className="font-display font-semibold text-gray-800 mb-4">Crop Suitability Confidence (%)</h3>
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={cropData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#eef7ff" />
                  <XAxis dataKey="name" fontSize={12} />
                  <YAxis fontSize={12} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="confidence" name="Confidence" stroke="#1a9bd6" strokeWidth={2.5} dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
