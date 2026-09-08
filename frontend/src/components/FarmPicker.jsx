import { useEffect, useState } from "react";
import { farmApi } from "../services/api";

/**
 * Optional farm selector for ML tool pages — lets the user link a
 * prediction/recommendation to one of their farms so it's saved to history,
 * or leave it as an ad-hoc "what-if" calculation with no farm_id.
 */
export default function FarmPicker({ value, onChange }) {
  const [farms, setFarms] = useState([]);

  useEffect(() => {
    farmApi.list().then(setFarms).catch(() => {});
  }, []);

  if (!farms.length) return null;

  return (
    <div>
      <label className="label-field">Link to a farm (optional)</label>
      <select className="input-field" value={value || ""} onChange={(e) => onChange(e.target.value || null)}>
        <option value="">Ad-hoc calculation (not saved to a farm)</option>
        {farms.map((f) => (
          <option key={f.id} value={f.id}>{f.name}</option>
        ))}
      </select>
    </div>
  );
}
