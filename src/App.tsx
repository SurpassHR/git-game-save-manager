import { useEffect } from "react";
import { useAppStore } from "./store";
import { ConfigPage } from "./pages/ConfigPage";
import { CommitGraphPage } from "./pages/CommitGraphPage";
import "./App.css";

function App() {
  const {
    currentPage,
    setCurrentPage,
    loadConfig,
    config,
    activeProfile,
    switchProfile,
    setTheme,
  } = useAppStore();

  // Load config on mount + apply theme
  useEffect(() => {
    loadConfig();
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = config.theme;
  }, [config.theme]);

  // Auto-switch to graph page if there's an active profile
  useEffect(() => {
    if (activeProfile) {
      setCurrentPage("graph");
    }
  }, [activeProfile?.id]);

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <nav className="sidebar">
        <div className="sidebar-header">
          <h1 className="sidebar-title">GGSM</h1>
          <span className="sidebar-subtitle">Game Save Manager</span>
        </div>

        {/* Game Profile Selector */}
        {config.profiles.length > 0 && (
          <div className="sidebar-profile-selector">
            <select
              className="profile-select"
              value={config.active_profile_id}
              onChange={(e) => switchProfile(e.target.value)}
            >
              {config.profiles.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.icon} {p.name}
                </option>
              ))}
            </select>
          </div>
        )}

        <div className="sidebar-nav">
          <button
            className={`nav-item ${currentPage === "graph" ? "active" : ""}`}
            onClick={() => setCurrentPage("graph")}
          >
            <span className="nav-icon">📊</span>
            <span className="nav-label">存档视图</span>
          </button>
          <button
            className={`nav-item ${currentPage === "config" ? "active" : ""}`}
            onClick={() => setCurrentPage("config")}
          >
            <span className="nav-icon">⚙️</span>
            <span className="nav-label">配置管理</span>
          </button>
        </div>

        {/* Theme Toggle */}
        <div className="sidebar-actions">
          <button
            className="nav-item theme-toggle"
            onClick={() =>
              setTheme(config.theme === "dark" ? "light" : "dark")
            }
          >
            <span className="nav-icon">
              {config.theme === "dark" ? "🌙" : "☀️"}
            </span>
            <span className="nav-label">
              {config.theme === "dark" ? "深色" : "浅色"}
            </span>
          </button>
        </div>

        <div className="sidebar-footer">
          <span className="version-tag">v2.0.0</span>
        </div>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        {currentPage === "config" && <ConfigPage />}
        {currentPage === "graph" && <CommitGraphPage />}
      </main>
    </div>
  );
}

export default App;
