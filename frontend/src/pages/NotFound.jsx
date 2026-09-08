import { Link } from "react-router-dom";
import { Leaf } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-[#f7faf5] flex flex-col items-center justify-center text-center px-4">
      <div className="rounded-2xl bg-agro-100 text-agro-700 p-4 mb-4">
        <Leaf size={32} />
      </div>
      <h1 className="font-display text-3xl font-bold text-gray-900">Page not found</h1>
      <p className="text-gray-500 mt-2 max-w-sm">The page you're looking for doesn't exist or may have moved.</p>
      <Link to="/" className="btn-primary mt-6">Back to Home</Link>
    </div>
  );
}
