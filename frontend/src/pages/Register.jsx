import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Leaf, Loader2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";

const LANGUAGES = [
  { value: "en", label: "English" },
  { value: "hi", label: "Hindi" },
  { value: "es", label: "Spanish" },
  { value: "fr", label: "French" },
  { value: "pt", label: "Portuguese" },
];

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "", email: "", password: "", phone: "", location: "",
    farm_size: "", preferred_language: "en",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register({
        ...form,
        farm_size: form.farm_size ? Number(form.farm_size) : null,
      });
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f7faf5] flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-lg">
        <div className="flex items-center justify-center gap-2 mb-8">
          <div className="rounded-xl bg-agro-600 p-2 text-white">
            <Leaf size={20} />
          </div>
          <span className="font-display text-xl font-bold text-agro-900">AgroEye</span>
        </div>

        <div className="card">
          <h1 className="font-display text-2xl font-bold text-gray-900 mb-1">Create your account</h1>
          <p className="text-sm text-gray-500 mb-6">Start getting AI-powered recommendations for your farm.</p>

          {error && (
            <div className="mb-4 rounded-xl bg-red-50 border border-red-100 px-4 py-2.5 text-sm text-red-700">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <label className="label-field">Full name</label>
                <input name="name" required value={form.name} onChange={handleChange} className="input-field" placeholder="Ramesh Kumar" />
              </div>
              <div>
                <label className="label-field">Phone</label>
                <input name="phone" value={form.phone} onChange={handleChange} className="input-field" placeholder="9876543210" />
              </div>
            </div>

            <div>
              <label className="label-field">Email</label>
              <input type="email" name="email" required value={form.email} onChange={handleChange} className="input-field" placeholder="you@example.com" />
            </div>

            <div>
              <label className="label-field">Password</label>
              <input type="password" name="password" required minLength={8} value={form.password} onChange={handleChange} className="input-field" placeholder="At least 8 characters" />
            </div>

            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <label className="label-field">Location</label>
                <input name="location" value={form.location} onChange={handleChange} className="input-field" placeholder="Punjab, India" />
              </div>
              <div>
                <label className="label-field">Farm size (ha)</label>
                <input type="number" step="0.1" name="farm_size" value={form.farm_size} onChange={handleChange} className="input-field" placeholder="5.0" />
              </div>
            </div>

            <div>
              <label className="label-field">Preferred language</label>
              <select name="preferred_language" value={form.preferred_language} onChange={handleChange} className="input-field">
                {LANGUAGES.map((l) => (
                  <option key={l.value} value={l.value}>{l.label}</option>
                ))}
              </select>
            </div>

            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? <Loader2 className="animate-spin" size={18} /> : "Create account"}
            </button>
          </form>

          <p className="text-sm text-gray-500 text-center mt-6">
            Already have an account?{" "}
            <Link to="/login" className="text-agro-700 font-medium hover:underline">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
