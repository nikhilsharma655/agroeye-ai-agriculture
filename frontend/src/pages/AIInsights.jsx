import { useEffect, useState } from "react";
import { Lightbulb, Sprout, Droplets, Wheat, ShieldAlert, FlaskConical, Leaf } from "lucide-react";
import { insightsApi, farmApi } from "../services/api";
import { PageHeader } from "../components/Common";
import { Loader, ErrorState, EmptyState, SeverityBadge } from "../components/Feedback";

const CATEGORY_ICON = {
  soil: Sprout, crop: Leaf, irrigation: Droplets, yield: Wheat, disease: ShieldAlert, fertilizer: FlaskConical,
};
const CATEGORIES = ["all", "soil", "crop", "irrigation", "yield", "disease", "fertilizer"];

export default function AIInsights() {
  const [groups, setGroups] = useState([]);
  const [farmNames, setFarmNames] = useState({});
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const [data, farms] = await Promise.all([insightsApi.all(), farmApi.list()]);
      setGroups(data);
      setFarmNames(Object.fromEntries(farms.map((f) => [f.id, f.name])));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  if (loading) return <Loader label="Generating insights..." />;
  if (error) return <ErrorState message={error} onRetry={load} />;

  const allInsights = groups.flatMap((g) => g.insights.map((i) => ({ ...i, farm_id: g.farm_id })));
  const filtered = filter === "all" ? allInsights : allInsights.filter((i) => i.category === filter);

  return (
    <div>
      <PageHeader title="AI Insights" subtitle="A summary of what your farm data means, generated across soil, crop, irrigation, yield, disease, and fertilizer." />

      <div className="flex flex-wrap gap-2 mb-6">
        {CATEGORIES.map((c) => (
          <button
            key={c}
            onClick={() => setFilter(c)}
            className={`rounded-full px-4 py-1.5 text-sm font-medium transition-colors capitalize ${
              filter === c ? "bg-agro-600 text-white" : "bg-white border border-agro-200 text-gray-600 hover:bg-agro-50"
            }`}
          >
            {c}
          </button>
        ))}
      </div>

      {!filtered.length ? (
        <EmptyState title="No insights to show" message="Add a farm with soil and crop data to generate AI insights." />
      ) : (
        <div className="grid sm:grid-cols-2 gap-4">
          {filtered.map((insight, idx) => {
            const Icon = CATEGORY_ICON[insight.category] || Lightbulb;
            return (
              <div key={idx} className="card">
                <div className="flex items-start justify-between mb-3">
                  <div className="h-10 w-10 rounded-xl bg-agro-100 text-agro-700 flex items-center justify-center">
                    <Icon size={19} />
                  </div>
                  <SeverityBadge severity={insight.severity} />
                </div>
                <p className="text-xs text-gray-400 mb-0.5">{farmNames[insight.farm_id] || "Farm"} • {insight.category}</p>
                <h3 className="font-display font-semibold text-gray-900">{insight.title}</h3>
                <p className="text-sm text-gray-500 mt-1.5">{insight.explanation}</p>
                <div className="mt-3 pt-3 border-t border-agro-50">
                  <p className="text-xs font-semibold text-agro-700">Recommended action</p>
                  <p className="text-sm text-gray-600 mt-0.5">{insight.recommended_action}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
