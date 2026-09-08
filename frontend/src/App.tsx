import { useState } from "react";
import "./index.css";
import MeetingAgent from "./components/MeetingAgent";

type Agent = {
  id: number;
  name: string;
  status: "available" | "coming-soon";
  description: string;
};

const agents: Agent[] = [
  {
    id: 1,
    name: "AI Meeting Agent",
    status: "available",
    description: "Analyze meetings and generate structured insights.",
  },
  {
    id: 2,
    name: "Agent 02",
    status: "coming-soon",
    description: "Coming soon",
  },
  {
    id: 3,
    name: "Agent 03",
    status: "coming-soon",
    description: "Coming soon",
  },
  {
    id: 4,
    name: "Agent 04",
    status: "coming-soon",
    description: "Coming soon",
  },
  {
    id: 5,
    name: "Agent 05",
    status: "coming-soon",
    description: "Coming soon",
  },
];

function App() {
  const [selectedAgent, setSelectedAgent] = useState<number | null>(null);

  const handleAgentClick = (agent: Agent) => {
    if (agent.status === "available") {
      setSelectedAgent(agent.id);
    }
  };

  const goBack = () => {
    setSelectedAgent(null);
  };

  return (
    <div className="app-shell">
      {/* Left File Panel */}
      <aside className="file-sidebar">
        <div className="sidebar-header">
          <div className="logo-mark">AI</div>
          <span>WORKSPACE</span>
        </div>

        <div className="file-section">
          <div className="section-title">
            <span>FILES</span>
            <button className="add-file-btn">+</button>
          </div>

          <div className="empty-files">
            <span className="file-icon">📁</span>
            <p>No files yet</p>
            <small>File support coming soon</small>
          </div>
        </div>
      </aside>

      {/* Main Workspace */}
      <main className="workspace">
        {selectedAgent === null ? (
          <>
            <div className="workspace-header">
              <div>
                <span className="eyebrow">AI WORKSPACE</span>
                <h1>AI Agent Suite</h1>
                <p>Select an agent to begin.</p>
              </div>

              <div className="system-status">
                <span className="status-dot"></span>
                SYSTEM ONLINE
              </div>
            </div>

            {/* Floating Agent Selection */}
            <div className="agent-selection">
              <div className="agent-row row-two">
                {agents.slice(0, 2).map((agent) => (
                  <button
                    key={agent.id}
                    className={`agent-card ${agent.status}`}
                    onClick={() => handleAgentClick(agent)}
                  >
                    <span className="agent-number">
                      0{agent.id}
                    </span>

                    <div className="agent-info">
                      <h3>{agent.name}</h3>
                      <p>{agent.description}</p>
                    </div>

                    <span className="agent-arrow">→</span>
                  </button>
                ))}
              </div>

              <div className="agent-row row-three">
                {agents.slice(2, 5).map((agent) => (
                  <button
                    key={agent.id}
                    className={`agent-card ${agent.status}`}
                    onClick={() => handleAgentClick(agent)}
                  >
                    <span className="agent-number">
                      0{agent.id}
                    </span>

                    <div className="agent-info">
                      <h3>{agent.name}</h3>
                      <p>{agent.description}</p>
                    </div>

                    <span className="agent-arrow">→</span>
                  </button>
                ))}
              </div>
            </div>
          </>
        ) : (
            <MeetingAgent onBack={goBack} />
        )}
      </main>
    </div>
  );
}

export default App;