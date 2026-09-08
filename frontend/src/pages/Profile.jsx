import { useState } from "react";
import { Loader2, User } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { userApi } from "../services/api";
import { PageHeader } from "../components/Common";

const LANGUAGES = [
  { value: "en", label: "English" }, { value: "hi", label: "Hindi" },
  { value: "es", label: "Spanish" }, { value: "fr", label: "French" }, { value: "pt", label: "Portuguese" },
];

export default function Profile() {
  const { user, updateUser } = useAuth();
  const [form, setForm] = useState({
    name: user?.name || "", phone: user?.phone || "", location: user?.location || "",
    farm_size: user?.farm_size ?? "", preferred_language: user?.preferred_language || "en",
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setError("");
    setLoading(true);
    try {
      const updated = await userApi.updateMe({
        ...form,
        farm_size: form.farm_size === "" ? null : Number(form.farm_size),
      });
      updateUser(updated);
      setMessage("Profile updated successfully.");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl">
      <PageHeader title="Profile" subtitle="Manage your personal and farm contact details." />

      <div className="card">
        <div className="flex items-center gap-4 mb-6">
          <div className="h-16 w-16 rounded-full bg-agro-200 flex items-center justify-center font-display text-2xl font-bold text-agro-800">
            {user?.name?.charAt(0)?.toUpperCase() || <User />}
          </div>
          <div>
            <p className="font-display font-semibold text-lg text-gray-900">{user?.name}</p>
            <p className="text-sm text-gray-500">{user?.email}</p>
          </div>
        </div>

        {message && <div className="mb-4 rounded-xl bg-agro-50 border border-agro-100 px-4 py-2.5 text-sm text-agro-800">{message}</div>}
        {error && <div className="mb-4 rounded-xl bg-red-50 border border-red-100 px-4 py-2.5 text-sm text-red-700">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="label-field">Full name</label>
              <input className="input-field" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            </div>
            <div>
              <label className="label-field">Phone</label>
              <input className="input-field" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
            </div>
            <div>
              <label className="label-field">Location</label>
              <input className="input-field" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} />
            </div>
            <div>
              <label className="label-field">Total farm size (ha)</label>
              <input type="number" step="0.1" className="input-field" value={form.farm_size} onChange={(e) => setForm({ ...form, farm_size: e.target.value })} />
            </div>
            <div>
              <label className="label-field">Preferred language</label>
              <select className="input-field" value={form.preferred_language} onChange={(e) => setForm({ ...form, preferred_language: e.target.value })}>
                {LANGUAGES.map((l) => <option key={l.value} value={l.value}>{l.label}</option>)}
              </select>
            </div>
          </div>
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? <Loader2 className="animate-spin" size={18} /> : "Save Changes"}
          </button>
        </form>
      </div>
    </div>
  );
}
