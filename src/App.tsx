import { useEffect } from "react";
import { useAppStore } from "./store";
import { ConfigPage } from "./pages/ConfigPage";
import { CommitGraphPage } from "./pages/CommitGraphPage";
import "./App.css";

function App() {
  const { currentPage, setCurrentPage, loadConfig, config } = useAppStore();

  useEffect(() => {
    loadConfig();
  }, []);

  // Auto-switch to graph page if repo is configured
  useEffect(() => {
    if (config.repo_path) {
      setCurrentPage("graph");
    }
  }, [config.repo_path]);

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <nav className="sidebar">
        <div className="sidebar-header">
          <h1 className="sidebar-title">GGSM</h1>
          <span className="sidebar-subtitle">Game Save Manager</span>
        </div>

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
