import { Loader2, AlertTriangle, Inbox } from "lucide-react";

export function Loader({ label = "Loading..." }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-agro-600">
      <Loader2 className="animate-spin" size={32} />
      <p className="text-sm text-gray-500">{label}</p>
    </div>
  );
}

export function ErrorState({ message = "Something went wrong.", onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
      <AlertTriangle className="text-red-500" size={32} />
      <p className="text-sm text-gray-600 max-w-sm">{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="btn-secondary mt-2">
          Try again
        </button>
      )}
    </div>
  );
}

export function EmptyState({ title = "Nothing here yet", message, action }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
      <div className="rounded-full bg-agro-50 p-4 text-agro-400">
        <Inbox size={28} />
      </div>
      <h3 className="font-display font-semibold text-gray-800">{title}</h3>
      {message && <p className="text-sm text-gray-500 max-w-sm">{message}</p>}
      {action}
    </div>
  );
}

export function SeverityBadge({ severity }) {
  const map = {
    low: "badge-low",
    medium: "badge-medium",
    high: "badge-high",
    info: "badge-info",
  };
  return <span className={`badge ${map[severity] || "badge-info"}`}>{severity}</span>;
}
