import axios, { InternalAxiosRequestConfig } from "axios";

const coreOrbitsApi = axios.create({
  baseURL: import.meta.env.VITE_CORE_ORBITS_URL || "http://localhost:8001",
});

const routingApi = axios.create({
  baseURL: import.meta.env.VITE_ROUTING_URL || "http://localhost:8002",
});

const schedulerApi = axios.create({
  baseURL: import.meta.env.VITE_GROUND_SCHEDULER_URL || "http://localhost:8003",
});

const aiAgentsApi = axios.create({
  baseURL: import.meta.env.VITE_AI_AGENTS_URL || "http://localhost:8004",
});

// Add auth token to requests
const addAuthToken = (config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
};

[coreOrbitsApi, routingApi, schedulerApi, aiAgentsApi].forEach((api) => {
  api.interceptors.request.use(addAuthToken);
});

export const api = {
  // Core Orbits
  getConstellations: () => coreOrbitsApi.get("/constellations"),
  getSatellites: () => coreOrbitsApi.get("/satellites"),
  getSatellitePosition: (id: number, time?: string) =>
    coreOrbitsApi.get(
      `/satellites/${id}/position${time ? `?time=${time}` : ""}`,
    ),

  // Ground Scheduler
  getGroundStations: () => schedulerApi.get("/ground-stations"),
  getPasses: () => schedulerApi.get("/passes"),
  getSchedule: () => schedulerApi.get("/schedule"),

  // AI Agents
  optimizeSchedule: (data: Record<string, unknown>) =>
    aiAgentsApi.post("/ai/pass-scheduler/optimize", data),
  analyzeEvents: (data: Record<string, unknown>) =>
    aiAgentsApi.post("/ai/ops-copilot/analyze", data),

  // Auth & Demo
  login: (data: FormData) => coreOrbitsApi.post("/auth/login", data),
  seedDemo: () => coreOrbitsApi.post("/demo/seed"),
};

export { coreOrbitsApi, routingApi, schedulerApi, aiAgentsApi };

// Alias for backward compatibility
export const coreOrbitsClient = coreOrbitsApi;
