import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("agroeye_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("agroeye_token");
      localStorage.removeItem("agroeye_user");
      if (!window.location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

// Unwraps AgroEye's {success, message, data} envelope; throws a normalized
// Error with a `.message` and `.code` on failure so components can render
// a single consistent error state.
async function unwrap(promise) {
  try {
    const res = await promise;
    return res.data.data;
  } catch (err) {
    const body = err.response?.data;
    const message = body?.message || err.message || "Something went wrong";
    const code = body?.error || "UNKNOWN_ERROR";
    const wrapped = new Error(message);
    wrapped.code = code;
    wrapped.status = err.response?.status;
    throw wrapped;
  }
}

export const authApi = {
  register: (payload) => unwrap(api.post("/api/auth/register", payload)),
  login: (payload) => unwrap(api.post("/api/auth/login", payload)),
  logout: () => unwrap(api.post("/api/auth/logout")),
};

export const userApi = {
  me: () => unwrap(api.get("/api/users/me")),
  updateMe: (payload) => unwrap(api.put("/api/users/me", payload)),
};

export const farmApi = {
  list: () => unwrap(api.get("/api/farms")),
  get: (id) => unwrap(api.get(`/api/farms/${id}`)),
  create: (payload) => unwrap(api.post("/api/farms", payload)),
  update: (id, payload) => unwrap(api.put(`/api/farms/${id}`, payload)),
  remove: (id) => unwrap(api.delete(`/api/farms/${id}`)),
  insights: (id) => unwrap(api.get(`/api/farms/${id}/insights`)),
  refreshWeather: (id) => unwrap(api.post(`/api/farms/${id}/weather/refresh`)),
};

export const cropApi = {
  list: (farmId) => unwrap(api.get(`/api/crops/farm/${farmId}`)),
  add: (farmId, payload) => unwrap(api.post(`/api/crops/farm/${farmId}`, payload)),
  update: (cropId, payload) => unwrap(api.put(`/api/crops/${cropId}`, payload)),
  remove: (cropId) => unwrap(api.delete(`/api/crops/${cropId}`)),
};

export const mlApi = {
  recommendCrop: (payload) => unwrap(api.post("/api/recommendations/crop", payload)),
  predictYield: (payload) => unwrap(api.post("/api/yield/predict", payload)),
  recommendFertilizer: (payload) => unwrap(api.post("/api/fertilizer/recommend", payload)),
  predictDisease: (payload) => unwrap(api.post("/api/disease/predict", payload)),
  recommendIrrigation: (payload) => unwrap(api.post("/api/irrigation/recommend", payload)),
};

export const insightsApi = {
  all: () => unwrap(api.get("/api/insights")),
};

export const analyticsApi = {
  overview: () => unwrap(api.get("/api/analytics/overview")),
  farmHistory: (farmId) => unwrap(api.get(`/api/analytics/farms/${farmId}/history`)),
};

export const notificationApi = {
  list: () => unwrap(api.get("/api/notifications")),
  markRead: (id) => unwrap(api.put(`/api/notifications/${id}/read`)),
};

export default api;
