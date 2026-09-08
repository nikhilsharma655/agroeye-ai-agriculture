import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Plus, MapPin, Sprout, Trash2, ArrowRight } from "lucide-react";
import { farmApi } from "../services/api";
import { PageHeader } from "../components/Common";
import { Loader, ErrorState, EmptyState } from "../components/Feedback";
import { titleCase } from "../utils/constants";

export default function MyFarms() {
  const [farms, setFarms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      setFarms(await farmApi.list());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm("Delete this farm? This cannot be undone.")) return;
    try {
      await farmApi.remove(id);
      setFarms((prev) => prev.filter((f) => f.id !== id));
    } catch (err) {
      alert(err.message);
    }
  };

  if (loading) return <Loader label="Loading your farms..." />;
  if (error) return <ErrorState message={error} onRetry={load} />;

  return (
    <div>
      <PageHeader
        title="My Farms"
        subtitle={`${farms.length} farm${farms.length === 1 ? "" : "s"} under management`}
        action={<Link to="/farms/new" className="btn-primary"><Plus size={16} /> Add Farm</Link>}
      />

      {!farms.length ? (
        <EmptyState
          title="No farms added yet"
          message="Add a farm to start tracking soil health, crops, and AI recommendations."
          action={<Link to="/farms/new" className="btn-primary mt-2">Add your first farm <ArrowRight size={16} /></Link>}
        />
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {farms.map((farm) => (
            <div
              key={farm.id}
              onClick={() => navigate(`/farms/${farm.id}`)}
              className="card hover:shadow-cardHover transition-shadow cursor-pointer group"
            >
              <div className="flex items-start justify-between">
                <div className="h-11 w-11 rounded-xl bg-agro-100 text-agro-700 flex items-center justify-center">
                  <Sprout size={22} />
                </div>
                <button
                  onClick={(e) => handleDelete(e, farm.id)}
                  className="text-gray-300 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100"
                >
                  <Trash2 size={18} />
                </button>
              </div>
              <h3 className="font-display font-semibold text-lg text-gray-900 mt-3">{farm.name}</h3>
              {farm.location && (
                <p className="text-sm text-gray-500 flex items-center gap-1 mt-0.5">
                  <MapPin size={13} /> {farm.location}
                </p>
              )}
              <div className="flex items-center gap-2 mt-4 flex-wrap">
                <span className="badge badge-info">{farm.area} ha</span>
                {farm.soil_type && <span className="badge badge-low">{titleCase(farm.soil_type)} soil</span>}
                {farm.current_crop && <span className="badge badge-medium">{titleCase(farm.current_crop)}</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
