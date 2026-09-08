import { useState } from "react";
import { LogOut, Trash2, Bell, Globe } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { PageHeader } from "../components/Common";

export default function Settings() {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [prefs, setPrefs] = useState({
    emailAlerts: true, diseaseAlerts: true, irrigationAlerts: true, dailySummary: true,
  });

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const toggle = (key) => setPrefs((p) => ({ ...p, [key]: !p[key] }));

  return (
    <div className="max-w-2xl space-y-5">
      <PageHeader title="Settings" subtitle="Notification preferences and account actions." />

      <div className="card">
        <h3 className="font-display font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <Bell size={18} className="text-agro-600" /> Notification Preferences
        </h3>
        <div className="space-y-3">
          {[
            ["emailAlerts", "Email notifications"],
            ["diseaseAlerts", "Disease risk alerts (via n8n)"],
            ["irrigationAlerts", "Irrigation alerts (via n8n)"],
            ["dailySummary", "Daily farm summary email"],
          ].map(([key, label]) => (
            <label key={key} className="flex items-center justify-between py-1">
              <span className="text-sm text-gray-700">{label}</span>
              <button
                type="button"
                onClick={() => toggle(key)}
                className={`w-11 h-6 rounded-full transition-colors relative ${prefs[key] ? "bg-agro-600" : "bg-gray-200"}`}
              >
                <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition-transform ${prefs[key] ? "translate-x-5" : "translate-x-0.5"}`} />
              </button>
            </label>
          ))}
        </div>
        <p className="text-xs text-gray-400 mt-4">
          These preferences control which n8n-powered automations notify you. Changes are saved locally in this demo.
        </p>
      </div>

      <div className="card">
        <h3 className="font-display font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <Globe size={18} className="text-agro-600" /> Region & Units
        </h3>
        <p className="text-sm text-gray-500">Units are currently fixed to hectares, °C, and mm rainfall across AgroEye.</p>
      </div>

      <div className="card border-red-100">
        <h3 className="font-display font-semibold text-red-700 mb-3">Account</h3>
        <div className="flex flex-wrap gap-3">
          <button onClick={handleLogout} className="btn-secondary">
            <LogOut size={16} /> Logout
          </button>
          <button
            onClick={() => alert("Please contact support to permanently delete your account.")}
            className="btn-secondary text-red-600 hover:bg-red-50"
          >
            <Trash2 size={16} /> Delete Account
          </button>
        </div>
      </div>
    </div>
  );
}
