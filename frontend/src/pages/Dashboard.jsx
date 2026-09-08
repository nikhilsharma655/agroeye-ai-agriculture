import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Sprout, Wheat, Droplets, Leaf, AlertTriangle, ArrowRight, Lightbulb,
} from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts";
import { analyticsApi, insightsApi, farmApi } from "../services/api";
import { PageHeader, StatCard } from "../components/Common";
import { Loader, ErrorState, EmptyState, SeverityBadge } from "../components/Feedback";
import { titleCase } from "../utils/constants";

export default function Dashboard() {
  const [overview, setOverview] = useState(null);
  const [insights, setInsights] = useState([]);
  const [farms, setFarms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const [ov, ins, fl] = await Promise.all([
        analyticsApi.overview(),
        insightsApi.all(),
        farmApi.list(),
      ]);
      setOverview(ov);
      setInsights(ins.flatMap((i) => i.insights.map((x) => ({ ...x, farm_id: i.farm_id }))));
      setFarms(fl);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  if (loading) return <Loader label="Loading your dashboard..." />;
  if (error) return <ErrorState message={error} onRetry={load} />;

  if (!farms.length) {
    return (
      <EmptyState
        title="No farms yet"
        message="Add your first farm to start getting AI-powered crop, yield, and irrigation recommendations."
        action={<Link to="/farms/new" className="btn-primary mt-2">Add your first farm <ArrowRight size={16} /></Link>}
      />
    );
  }

  const yieldChartData = (overview?.recent_predictions || [])
    .filter((p) => p.type === "yield_prediction")
    .slice(0, 8)
    .reverse()
    .map((p, idx) => ({ name: `#${idx + 1}`, yield: p.output.yield_per_hectare }));

  const soilData = farms.map((f) => ({
    name: f.name.length > 10 ? f.name.slice(0, 10) + "…" : f.name,
    N: f.nitrogen || 0, P: f.phosphorus || 0, K: f.potassium || 0,
  }));

  return (
    <div>
      <PageHeader
        title="Farm Dashboard"
        subtitle="A quick overview of everything happening across your farms."
        action={<Link to="/farms/new" className="btn-primary">Add Farm</Link>}
      />

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard icon={Sprout} label="Total Farms" value={overview?.total_farms ?? 0} tone="agro" />
        <StatCard icon={Leaf} label="Current Crops" value={overview?.current_crops?.length || 0}
          sub={overview?.current_crops?.map(titleCase).join(", ") || "None set"} tone="sky" />
        <StatCard icon={Droplets} label="Avg. Soil Moisture" value={overview?.average_soil_moisture != null ? `${overview.average_soil_moisture}%` : "—"} tone="sky" />
        <StatCard icon={AlertTriangle} label="Open Alerts" value={overview?.open_alerts ?? 0} tone={overview?.open_alerts ? "red" : "agro"} />
      </div>

      <div className="grid lg:grid-cols-2 gap-5 mb-6">
        <div className="card">
          <h3 className="font-display font-semibold text-gray-800 mb-4">Recent Yield Predictions (t/ha)</h3>
          {yieldChartData.length ? (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={yieldChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5efdb" />
                <XAxis dataKey="name" fontSize={12} stroke="#9ca3af" />
                <YAxis fontSize={12} stroke="#9ca3af" />
                <Tooltip />
                <Line type="monotone" dataKey="yield" stroke="#487a29" strokeWidth={2.5} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-gray-400 py-12 text-center">Run a yield prediction to see history here.</p>
          )}
        </div>

        <div className="card">
          <h3 className="font-display font-semibold text-gray-800 mb-4">Soil Nutrient Levels (kg/ha)</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={soilData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5efdb" />
              <XAxis dataKey="name" fontSize={12} stroke="#9ca3af" />
              <YAxis fontSize={12} stroke="#9ca3af" />
              <Tooltip />
              <Bar dataKey="N" fill="#5e9a37" radius={[4, 4, 0, 0]} />
              <Bar dataKey="P" fill="#38b6ea" radius={[4, 4, 0, 0]} />
              <Bar dataKey="K" fill="#b8834f" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-display font-semibold text-gray-800 flex items-center gap-2">
            <Lightbulb size={18} className="text-amber-500" /> AI Insights
          </h3>
          <Link to="/insights" className="text-sm text-agro-700 font-medium hover:underline flex items-center gap-1">
            View all <ArrowRight size={14} />
          </Link>
        </div>
        <div className="space-y-3">
          {insights.slice(0, 4).map((insight, idx) => (
            <div key={idx} className="flex items-start gap-3 rounded-xl border border-agro-100 p-3.5">
              <SeverityBadge severity={insight.severity} />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-800">{insight.title}</p>
                <p className="text-sm text-gray-500 mt-0.5">{insight.explanation}</p>
              </div>
            </div>
          ))}
          {!insights.length && <p className="text-sm text-gray-400 text-center py-6">No insights yet.</p>}
        </div>
      </div>
    </div>
  );
}
