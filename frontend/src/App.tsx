import { useState } from "react";
import "./index.css";

import MeetingAgent from "./components/MeetingAgent";
import CompetitorAgent from "./components/CompetitorAgent";

import { sampleMeetingTranscript } from "./data/sampleTranscript";

import WebsiteQAAgent from "./components/WebsiteQAAgent";

import LeadQualificationAgent from "./components/LeadQualificationAgent";

import KnowledgeBaseAgent from "./components/KnowledgeBaseAgent";

import {
  sampleLeadCSV,
  sampleICP,
} from "./data/sampleLeads";


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
    name: "AI Competitor Watch Agent",
    status: "available",
    description:
      "Monitor competitors and discover meaningful recent updates.",
  },

  {
  id: 3,
  name: "AI Website QA Agent",
  status: "available",
  description:
    "Inspect websites for technical, content and SEO issues.",
  },

  {
  id: 4,
  name: "AI Lead Qualification Agent",
  status: "available",
  description:
    "Research and rank prospects against your ideal customer profile.",
  },

  {
  id: 5,
  name: "AI Knowledge-Base Support Agent",
  status: "available",
  description:
    "Answer questions using the NotRealOrg knowledge base with verified sources.",
  },
];


function App() {

  const [selectedAgent, setSelectedAgent] =
    useState<number | null>(null);

  const [initialTranscript, setInitialTranscript] =
    useState("");

  const [initialCompanies, setInitialCompanies] = useState<string[]>([]);

  const [initialWebsiteUrl, setInitialWebsiteUrl] =
  useState("");

  const [initialLeadCSV, setInitialLeadCSV] =
  useState("");

  const [initialLeadICP, setInitialLeadICP] =
  useState(sampleICP);

  const handleAgentClick = (agent: Agent) => {

    if (agent.status === "available") {
      setSelectedAgent(agent.id);
    }

  };


  const goBack = () => {

    setSelectedAgent(null);
    setInitialTranscript("");
    setInitialCompanies([]);
    setInitialWebsiteUrl("");
    setInitialLeadCSV("");
    setInitialLeadICP(sampleICP);
  };


  const loadSampleTranscript = () => {

    setInitialTranscript(sampleMeetingTranscript);
    setSelectedAgent(1);

  };


  const loadCompetitorExample = () => {
  setInitialCompanies([
    "OpenAI",
    "Anthropic",
    "Google",
  ]);

  setSelectedAgent(2);
  };

  const loadWebsiteQAExample = () => {

  setInitialWebsiteUrl(
    "example.com"
  );

  setSelectedAgent(3);

  };

  const loadLeadQualificationExample = () => {

  setInitialLeadCSV(sampleLeadCSV);

  setInitialLeadICP(sampleICP);

  setSelectedAgent(4);

  };


  return (

    <div className="app-shell">


      {/* Left File Panel */}

      <aside className="file-sidebar">


        <div className="sidebar-header">

          <div className="logo-mark">
            AI
          </div>

          <span>
            WORKSPACE
          </span>

        </div>


        <div className="file-section">


          <div className="section-title">

            <span>
              FILES
            </span>

            <button className="add-file-btn">
              +
            </button>

          </div>


          {/* Meeting Agent Example */}

          {selectedAgent === 1 && (

            <div className="sample-files">

              <button
                className="sample-file"
                onClick={loadSampleTranscript}
              >

                <div className="sample-file-icon">
                  TXT
                </div>


                <div className="sample-file-info">

                  <span className="sample-file-name">
                    q4_website_redesign_meeting.txt
                  </span>

                  <span className="sample-file-meta">
                    Sample meeting transcript
                  </span>

                </div>

              </button>


              <div className="sample-file-footer">

                Click the file to load it into
                the AI Meeting Agent.

              </div>

            </div>

          )}


          {/* Competitor Agent Example */}

          {selectedAgent === 2 && (

            <div className="sample-files">

              <button
                className="sample-file"
                onClick={loadCompetitorExample}
              >

                <div className="sample-file-icon">
                  DEMO
                </div>


                <div className="sample-file-info">

                  <span className="sample-file-name">
                    ai_competitors_example
                  </span>

                  <span className="sample-file-meta">
                    OpenAI · Anthropic · Google
                  </span>

                </div>

              </button>


              <div className="sample-file-footer">

                Example companies for competitor
                intelligence monitoring.

              </div>

            </div>

          )}

          {selectedAgent === 3 && (

  <div className="sample-files">

    <button
      className="sample-file"
      onClick={loadWebsiteQAExample}
    >

      <div className="sample-file-icon">
        URL
      </div>


      <div className="sample-file-info">

        <span className="sample-file-name">
          example.com
        </span>

        <span className="sample-file-meta">
          Sample website for QA inspection
        </span>

      </div>

    </button>


    <div className="sample-file-footer">

      Click the example to load a website
      into the AI Website QA Agent.

    </div>

  </div>

)}

          {/* Lead Qualification Agent Example */}

{selectedAgent === 4 && (

  <div className="sample-files">

    <button
      className="sample-file"
      onClick={loadLeadQualificationExample}
    >

      <div className="sample-file-icon">
        CSV
      </div>

      <div className="sample-file-info">

        <span className="sample-file-name">
          lead_qualification_example.csv
        </span>

        <span className="sample-file-meta">
          10 synthetic leads + ICP
        </span>

      </div>

    </button>

    <div className="sample-file-footer">

      Example dataset with 10 companies,
      contact data and qualification criteria.

    </div>

  </div>

)}


          {/* No Agent Selected */}

          {selectedAgent === null && (

            <div className="sample-file-footer">

              Select an agent to view
              its example files.

            </div>

          )}


        </div>


      </aside>


      {/* Main Workspace */}

      <main className="workspace">


        {selectedAgent === null ? (

          <>


            <div className="workspace-header">

              <div>

                <span className="eyebrow">
                  AI WORKSPACE
                </span>

                <h1>
                  AI Agent Suite
                </h1>

                <p>
                  Select an agent to begin.
                </p>

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

                      <h3>
                        {agent.name}
                      </h3>

                      <p>
                        {agent.description}
                      </p>

                    </div>


                    <span className="agent-arrow">
                      →
                    </span>

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

                      <h3>
                        {agent.name}
                      </h3>

                      <p>
                        {agent.description}
                      </p>

                    </div>


                    <span className="agent-arrow">
                      →
                    </span>

                  </button>

                ))}

              </div>


            </div>


          </>


        ) : selectedAgent === 1 ? (

          <MeetingAgent
            onBack={goBack}
            initialTranscript={initialTranscript}
          />


        ) : selectedAgent === 2 ? (

          <CompetitorAgent
            onBack={goBack}
            initialCompanies={initialCompanies}
          />

        ) : selectedAgent === 3 ? (

          <WebsiteQAAgent
            onBack={goBack}
            initialUrl={initialWebsiteUrl}
          />

        ) : selectedAgent === 4 ? (

          <LeadQualificationAgent
            onBack={goBack}
            initialCSV={initialLeadCSV}
            initialICP={initialLeadICP}
          />
        ) : selectedAgent === 5 ? (

          <KnowledgeBaseAgent />


        ) : null}

        


      </main>


    </div>

  );

}


export default App;

