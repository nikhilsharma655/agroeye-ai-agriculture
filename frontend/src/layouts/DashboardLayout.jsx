import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  LayoutDashboard, Sprout, Wheat, FlaskConical, Droplets, ShieldAlert,
  Lightbulb, BarChart3, Bell, User, Settings, LogOut, Menu, X, Leaf,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/farms", label: "My Farms", icon: Sprout },
  { to: "/crop-recommendation", label: "Crop Recommendation", icon: Leaf },
  { to: "/yield-prediction", label: "Yield Prediction", icon: Wheat },
  { to: "/fertilizer", label: "Fertilizer", icon: FlaskConical },
  { to: "/disease-risk", label: "Disease Risk", icon: ShieldAlert },
  { to: "/irrigation", label: "Irrigation", icon: Droplets },
  { to: "/insights", label: "AI Insights", icon: Lightbulb },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/notifications", label: "Notifications", icon: Bell },
];

export default function DashboardLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-[#f7faf5] flex">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/30 z-30 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:sticky top-0 h-screen z-40 w-72 bg-agro-900 text-agro-50 flex flex-col
        transition-transform duration-200 ${sidebarOpen ? "translate-x-0" : "-translate-x-full"} lg:translate-x-0`}
      >
        <div className="flex items-center gap-2 px-6 py-5 border-b border-white/10">
          <div className="rounded-xl bg-agro-500 p-2">
            <Leaf size={22} />
          </div>
          <span className="font-display text-xl font-bold tracking-tight">AgroEye</span>
          <button className="ml-auto lg:hidden text-agro-200" onClick={() => setSidebarOpen(false)}>
            <X size={20} />
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors ${
                  isActive ? "bg-agro-600 text-white" : "text-agro-100/80 hover:bg-white/5 hover:text-white"
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-white/10 p-3 space-y-1">
          <NavLink
            to="/profile"
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium ${
                isActive ? "bg-agro-600 text-white" : "text-agro-100/80 hover:bg-white/5 hover:text-white"
              }`
            }
          >
            <User size={18} /> Profile
          </NavLink>
          <NavLink
            to="/settings"
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium ${
                isActive ? "bg-agro-600 text-white" : "text-agro-100/80 hover:bg-white/5 hover:text-white"
              }`
            }
          >
            <Settings size={18} /> Settings
          </NavLink>
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-red-200 hover:bg-red-900/40"
          >
            <LogOut size={18} /> Logout
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 min-w-0 flex flex-col">
        <header className="sticky top-0 z-20 flex items-center gap-3 bg-white/80 backdrop-blur border-b border-agro-100 px-4 lg:px-8 py-4">
          <button className="lg:hidden text-agro-700" onClick={() => setSidebarOpen(true)}>
            <Menu size={22} />
          </button>
          <div className="flex-1" />
          <div className="text-right hidden sm:block">
            <p className="text-sm font-semibold text-gray-800">{user?.name}</p>
            <p className="text-xs text-gray-500">{user?.location || "Farmer"}</p>
          </div>
          <div className="h-9 w-9 rounded-full bg-agro-200 flex items-center justify-center font-display font-semibold text-agro-800">
            {user?.name?.charAt(0)?.toUpperCase() || "U"}
          </div>
        </header>

        <main className="flex-1 p-4 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
