import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import {
  Rocket,
  Shield,
  Eye,
  Settings,
  PlayCircle,
  Loader2,
} from "lucide-react";

export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [seedLoading, setSeedLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleLogin = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("username", username);
      formData.append("password", password);

      const response = await api.login(formData);
      const { access_token } = response.data;

      localStorage.setItem("token", access_token);
      localStorage.setItem(
        "user_role",
        username.includes("admin")
          ? "admin"
          : username.includes("ops")
            ? "operator"
            : "viewer",
      );

      navigate("/");
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = (role: "viewer" | "ops" | "admin") => {
    if (role === "viewer") {
      setUsername("demo_viewer");
      setPassword("viewer123");
    } else if (role === "ops") {
      setUsername("demo_ops");
      setPassword("operator123");
    } else if (role === "admin") {
      setUsername("demo_admin");
      setPassword("admin123");
    }
    // We can't auto-submit immediately because state updates are async,
    // but the user can click login. Or we could use a ref/effect.
    // For simplicity, let's just fill the form.
  };

  const handleSeedDemo = async () => {
    setSeedLoading(true);
    setError("");
    setSuccess("");

    try {
      await api.seedDemo();
      setSuccess("Demo data initialized successfully!");
    } catch (err: any) {
      console.error(err);
      setError("Failed to seed demo data. Is the backend running?");
    } finally {
      setSeedLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full grid grid-cols-1 md:grid-cols-2 gap-8 bg-slate-900/50 rounded-2xl border border-slate-800 backdrop-blur-sm overflow-hidden shadow-2xl">
        {/* Left Side: Brand & Info */}
        <div className="p-8 md:p-12 flex flex-col justify-between bg-gradient-to-br from-slate-900 to-indigo-950/30">
          <div>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center border border-blue-500/20">
                <Rocket className="w-6 h-6 text-blue-400" />
              </div>
              <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-cyan-300">
                Constellation Hub
              </h1>
            </div>

            <p className="text-slate-400 mb-8 leading-relaxed">
              Unified control plane for modern satellite fleets. Visualize
              orbits, optimized schedules, and intelligent operations.
            </p>

            <div className="space-y-4">
              <div className="flex items-center gap-3 text-slate-300 text-sm">
                <div className="p-2 rounded bg-slate-800/50 border border-slate-700/50">
                  <PlayCircle className="w-4 h-4 text-emerald-400" />
                </div>
                <span>Interactive 3D Demo Mode</span>
              </div>
              <div className="flex items-center gap-3 text-slate-300 text-sm">
                <div className="p-2 rounded bg-slate-800/50 border border-slate-700/50">
                  <Shield className="w-4 h-4 text-indigo-400" />
                </div>
                <span>Role-Based Access Control</span>
              </div>
            </div>
          </div>

          <div className="mt-12 pt-6 border-t border-slate-800/50">
            <p className="text-xs text-slate-500">
              v1.0.0-MVP • Demo Environment
            </p>
          </div>
        </div>

        {/* Right Side: Login Form */}
        <div className="p-8 md:p-12 bg-slate-900/80">
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-white mb-2">
              Welcome Back
            </h2>
            <p className="text-slate-400 text-sm">
              Sign in to access the control plane
            </p>
          </div>

          {error && (
            <div className="mb-6 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
              {error}
            </div>
          )}

          {success && (
            <div className="mb-6 p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-emerald-400 text-sm">
              {success}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1 uppercase tracking-wider">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all placeholder-slate-600"
                placeholder="Enter username"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1 uppercase tracking-wider">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all placeholder-slate-600"
                placeholder="Enter password"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium py-2.5 rounded-lg transition-all flex items-center justify-center gap-2 hover:shadow-lg hover:shadow-blue-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                "Sign In"
              )}
            </button>
          </form>

          {/* Demo Controls */}
          <div className="mt-8 pt-8 border-t border-slate-800">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                Quick Demo Access
              </span>
              <button
                onClick={handleSeedDemo}
                disabled={seedLoading}
                className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1.5 transition-colors disabled:opacity-50"
              >
                {seedLoading ? (
                  <Loader2 className="w-3 h-3 animate-spin" />
                ) : (
                  <PlayCircle className="w-3 h-3" />
                )}
                {seedLoading ? "Initializing..." : "Initialize Demo Data"}
              </button>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <button
                onClick={() => handleDemoLogin("viewer")}
                className="bg-slate-800/50 hover:bg-slate-800 border border-slate-700/50 hover:border-slate-600 rounded-lg p-3 text-center transition-all group"
              >
                <Eye className="w-4 h-4 text-slate-400 group-hover:text-blue-400 mx-auto mb-1.5 transition-colors" />
                <span className="block text-[10px] text-slate-400 font-medium">
                  Viewer
                </span>
              </button>

              <button
                onClick={() => handleDemoLogin("ops")}
                className="bg-slate-800/50 hover:bg-slate-800 border border-slate-700/50 hover:border-slate-600 rounded-lg p-3 text-center transition-all group"
              >
                <Settings className="w-4 h-4 text-slate-400 group-hover:text-emerald-400 mx-auto mb-1.5 transition-colors" />
                <span className="block text-[10px] text-slate-400 font-medium">
                  Operator
                </span>
              </button>

              <button
                onClick={() => handleDemoLogin("admin")}
                className="bg-slate-800/50 hover:bg-slate-800 border border-slate-700/50 hover:border-slate-600 rounded-lg p-3 text-center transition-all group"
              >
                <Shield className="w-4 h-4 text-slate-400 group-hover:text-indigo-400 mx-auto mb-1.5 transition-colors" />
                <span className="block text-[10px] text-slate-400 font-medium">
                  Admin
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
