import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import DashboardLayout from "./layouts/DashboardLayout";

import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import MyFarms from "./pages/MyFarms";
import FarmDetails from "./pages/FarmDetails";
import AddFarm from "./pages/AddFarm";
import CropRecommendation from "./pages/CropRecommendation";
import YieldPrediction from "./pages/YieldPrediction";
import FertilizerRecommendation from "./pages/FertilizerRecommendation";
import DiseaseRisk from "./pages/DiseaseRisk";
import Irrigation from "./pages/Irrigation";
import AIInsights from "./pages/AIInsights";
import Analytics from "./pages/Analytics";
import Notifications from "./pages/Notifications";
import Profile from "./pages/Profile";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/farms" element={<MyFarms />} />
            <Route path="/farms/new" element={<AddFarm />} />
            <Route path="/farms/:farmId" element={<FarmDetails />} />
            <Route path="/crop-recommendation" element={<CropRecommendation />} />
            <Route path="/yield-prediction" element={<YieldPrediction />} />
            <Route path="/fertilizer" element={<FertilizerRecommendation />} />
            <Route path="/disease-risk" element={<DiseaseRisk />} />
            <Route path="/irrigation" element={<Irrigation />} />
            <Route path="/insights" element={<AIInsights />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/notifications" element={<Notifications />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/settings" element={<Settings />} />
          </Route>

          <Route path="*" element={<NotFound />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
