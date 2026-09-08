import { useEffect, useState } from "react";
import { Bell, CheckCircle2, AlertTriangle, Lightbulb, Info } from "lucide-react";
import { notificationApi } from "../services/api";
import { PageHeader } from "../components/Common";
import { Loader, ErrorState, EmptyState } from "../components/Feedback";

const TYPE_ICON = { alert: AlertTriangle, recommendation: Lightbulb, system: Info, general: Bell };
const TYPE_TONE = { alert: "bg-red-100 text-red-600", recommendation: "bg-amber-100 text-amber-600", system: "bg-sky-100 text-sky-600", general: "bg-agro-100 text-agro-600" };

export default function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      setNotifications(await notificationApi.list());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleMarkRead = async (id) => {
    try {
      await notificationApi.markRead(id);
      setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
    } catch (err) {
      alert(err.message);
    }
  };

  if (loading) return <Loader label="Loading notifications..." />;
  if (error) return <ErrorState message={error} onRetry={load} />;

  return (
    <div>
      <PageHeader title="Notifications" subtitle="Alerts and updates from AgroEye and connected automations (n8n)." />

      {!notifications.length ? (
        <EmptyState title="You're all caught up" message="New alerts about disease risk, irrigation, and daily summaries will show up here." />
      ) : (
        <div className="space-y-3">
          {notifications.map((n) => {
            const Icon = TYPE_ICON[n.type] || Bell;
            return (
              <div key={n.id} className={`card flex items-start gap-4 ${n.is_read ? "opacity-70" : ""}`}>
                <div className={`h-10 w-10 rounded-xl flex items-center justify-center shrink-0 ${TYPE_TONE[n.type] || TYPE_TONE.general}`}>
                  <Icon size={19} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <p className="font-semibold text-gray-800">{n.title}</p>
                    {n.source === "n8n" && <span className="badge badge-info">via n8n</span>}
                  </div>
                  <p className="text-sm text-gray-500 mt-0.5">{n.message}</p>
                  <p className="text-xs text-gray-400 mt-1">{new Date(n.created_at).toLocaleString()}</p>
                </div>
                {!n.is_read && (
                  <button onClick={() => handleMarkRead(n.id)} className="text-agro-600 hover:text-agro-800 shrink-0" title="Mark as read">
                    <CheckCircle2 size={20} />
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
