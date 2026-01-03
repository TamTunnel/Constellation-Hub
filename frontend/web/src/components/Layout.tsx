import { ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  Home,
  Satellite,
  Radio,
  Calendar,
  Bot,
  Settings,
  Globe,
  Database,
} from "lucide-react";

interface LayoutProps {
  children: ReactNode;
}

const navItems = [
  { path: "/", label: "Dashboard", icon: Home },
  { path: "/satellites", label: "Satellites", icon: Satellite },
  { path: "/ground-stations", label: "Ground Stations", icon: Radio },
  { path: "/scheduling", label: "Scheduling", icon: Calendar },
  { path: "/ops-copilot", label: "Ops Co-Pilot", icon: Bot },
  { path: "/tle-admin", label: "TLE Feeds", icon: Database },
];

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-64 bg-space-800 border-r border-white/10 flex flex-col">
        {/* Logo */}
        <div className="p-4 border-b border-white/10">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-cosmic-500 to-nebula-500 rounded-lg flex items-center justify-center">
              <Globe className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-lg">Constellation</h1>
              <p className="text-xs text-white/60">Hub v1.0</p>
            </div>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              const Icon = item.icon;

              return (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    className={`
                      flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200
                      ${
                        isActive
                          ? "bg-cosmic-500/20 text-cosmic-400 border border-cosmic-500/30"
                          : "text-white/70 hover:bg-white/5 hover:text-white"
                      }
                    `}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* User / Login */}
        <div className="p-4 border-t border-white/10">
          {localStorage.getItem("token") ? (
            <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-white/5 border border-white/10 w-full">
              <div className="w-8 h-8 rounded-full bg-cosmic-500/20 flex items-center justify-center border border-cosmic-500/30">
                <span className="text-xs font-bold text-cosmic-400">
                  {localStorage
                    .getItem("user_role")
                    ?.substring(0, 2)
                    .toUpperCase() || "US"}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  {localStorage.getItem("user_role")?.toUpperCase() || "User"}
                </p>
              </div>
              <button
                onClick={() => {
                  localStorage.removeItem("token");
                  localStorage.removeItem("user_role");
                  window.location.reload();
                }}
                className="text-white/40 hover:text-white transition-colors"
              >
                <Settings className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <Link
              to="/login"
              className="flex items-center gap-3 px-3 py-2 rounded-lg text-white/70 hover:bg-white/5 hover:text-white transition-all duration-200 w-full border border-white/10"
            >
              <div className="w-5 h-5 flex items-center justify-center">
                <Settings className="w-5 h-5" />
              </div>
              <span className="font-medium">Sign In</span>
            </Link>
          )}
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 bg-space-900 overflow-auto">{children}</main>
    </div>
  );
}
