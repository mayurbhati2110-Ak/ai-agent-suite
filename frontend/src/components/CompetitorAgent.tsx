import { useState, useEffect } from "react";
import "../index2.css";


interface CompetitorAgentProps {
  onBack: () => void;
  initialCompanies?: string[];
}


interface CompetitorUpdate {
  title: string;
  category: string;
  summary: string;
  why_it_matters: string;
  source: string;
  date: string | null;
}


interface CompanyIntelligence {
  company: string;
  updates: CompetitorUpdate[];
}


interface CompetitorResponse {
  companies: CompanyIntelligence[];
  intelligence_brief: string;
}


function CompetitorAgent({
  onBack,
  initialCompanies = []
}: CompetitorAgentProps) {

  const [companyInput, setCompanyInput] =
    useState("");

   const [companies, setCompanies] =
    useState<string[]>(initialCompanies);

    useEffect(() => {

  if (initialCompanies.length > 0) {

    setCompanies(initialCompanies);

    setResponse(null);

    setError(null);

  }

}, [initialCompanies]);

  const [response, setResponse] =
    useState<CompetitorResponse | null>(
      null
    );

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  const addCompany = () => {

    const company = companyInput.trim();

    if (!company) {
      return;
    }

    if (companies.includes(company)) {
      return;
    }

    if (companies.length >= 10) {
      return;
    }

    setCompanies([
      ...companies,
      company
    ]);

    setCompanyInput("");

  };


  const removeCompany = (
    companyToRemove: string
  ) => {

    setCompanies(
      companies.filter(
        (company) =>
          company !== companyToRemove
      )
    );

  };


  const handleKeyDown = (
    event: React.KeyboardEvent<HTMLInputElement>
  ) => {

    if (event.key === "Enter") {

      event.preventDefault();

      addCompany();

    }

  };


  const handleAnalyze = async () => {

    if (
      companies.length === 0 ||
      loading
    ) {
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);

    try {

      const apiResponse = await fetch(
        "http://127.0.0.1:8000/api/competitor/analyze",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            companies: companies
          })
        }
      );


      if (!apiResponse.ok) {

        let errorMessage =
          "Failed to analyze competitor updates.";

        try {

          const errorData =
            await apiResponse.json();

          errorMessage =
            errorData.detail ||
            errorMessage;

        } catch {
          // Keep default error message
        }

        throw new Error(
          errorMessage
        );

      }


      const data: CompetitorResponse =
        await apiResponse.json();

      setResponse(data);

    } catch (err) {

      const errorMessage =
        err instanceof Error
          ? err.message
          : "Something went wrong while analyzing competitors.";

      setError(
        errorMessage
      );

    } finally {

      setLoading(false);

    }

  };


  return (

    <div className="competitor-agent">


      {/* TOP BAR */}

      <div className="competitor-topbar">

        <button
          className="competitor-back-button"
          onClick={onBack}
        >
          ← BACK TO AGENT SUITE
        </button>


        <div className="competitor-status">

          <span className="competitor-status-dot"></span>

          AI COMPETITOR WATCH AGENT

        </div>

      </div>


      {/* MAIN CONTENT */}

      <div className="competitor-agent-content">


        {/* HERO */}

        <section className="competitor-hero">

          <div className="competitor-icon">
            ◉
          </div>


          <div className="competitor-hero-text">

            <span className="competitor-eyebrow">
              AGENT 02 / COMPETITOR INTELLIGENCE
            </span>


            <h1>
              AI Competitor Watch Agent
            </h1>


            <p>
              Monitor competitors, discover meaningful
              recent updates, remove noise, categorize
              developments, and generate concise
              intelligence.
            </p>

          </div>

        </section>


        {/* COMPANY INPUT */}

        <section className="competitor-input-panel">


          <div className="competitor-panel-header">

            <span>
              ◉ MONITORED COMPANIES
            </span>


            <span className="competitor-count">

              {companies.length}/10 COMPANIES

            </span>

          </div>


          <div className="competitor-input-row">

            <input
              type="text"
              value={companyInput}
              placeholder="Enter a company or product name..."

              onChange={(event) =>
                setCompanyInput(
                  event.target.value
                )
              }

              onKeyDown={handleKeyDown}

              disabled={loading}
            />


            <button
              className="add-company-button"

              onClick={addCompany}

              disabled={
                loading ||
                !companyInput.trim() ||
                companies.length >= 10
              }
            >
              + ADD
            </button>

          </div>


          {/* COMPANY TAGS */}

          <div className="company-tags-container">

            {companies.length === 0 ? (

              <p className="no-companies-message">

                Add between 1 and 10 competitors
                to begin monitoring.

              </p>

            ) : (

              companies.map(
                (company) => (

                  <div
                    className="company-tag"
                    key={company}
                  >

                    <span>
                      {company}
                    </span>


                    <button
                      onClick={() =>
                        removeCompany(company)
                      }

                      disabled={loading}

                      aria-label={
                        `Remove ${company}`
                      }
                    >
                      ×
                    </button>

                  </div>

                )
              )

            )}

          </div>


          {/* PANEL FOOTER */}

          <div className="competitor-panel-footer">

            <span className="competitor-hint">

              ⓘ The agent searches recent updates
              and generates competitor intelligence.

            </span>


            <button
              className="competitor-analyze-button"

              onClick={handleAnalyze}

              disabled={
                companies.length === 0 ||
                loading
              }
            >

              {loading
                ? "ANALYZING..."
                : "✦ WATCH COMPETITORS →"
              }

            </button>

          </div>

        </section>


        {/* ERROR STATE */}

        {error && (

          <div className="competitor-error">

            <strong>
              ANALYSIS FAILED
            </strong>

            <p>
              {error}
            </p>

          </div>

        )}


        {/* RESULTS */}

        {response && (

          <section className="competitor-results-section">


            {/* RESULTS HEADER */}

            <div className="competitor-results-header">

              <div>

                <span className="competitor-results-label">
                  ✦ COMPETITOR INTELLIGENCE
                </span>

                <h2>
                  Analysis Results
                </h2>

              </div>


              <span className="competitor-complete-badge">

                COMPLETE

              </span>

            </div>


            {/* INTELLIGENCE BRIEF */}

            <div className="intelligence-brief">

              <span className="intelligence-label">

                INTELLIGENCE BRIEF

              </span>


              <p>

                {response.intelligence_brief}

              </p>

            </div>


            {/* COMPANY RESULTS */}

            <div className="company-results-list">

              {response.companies.map(
                (company) => (

                  <article
                    className="company-result-card"
                    key={company.company}
                  >


                    {/* COMPANY HEADER */}

                    <div className="company-result-header">

                      <div>

                        <span className="company-result-label">
                          COMPETITOR
                        </span>


                        <h3>

                          {company.company}

                        </h3>

                      </div>


                      <span className="update-count">

                        {company.updates.length} UPDATES

                      </span>

                    </div>


                    {/* NO UPDATES */}

                    {company.updates.length === 0 ? (

                      <div className="no-updates">

                        No meaningful recent updates
                        were identified.

                      </div>

                    ) : (

                      <div className="updates-list">

                        {company.updates.map(
                          (update, index) => (

                            <article
                              className="competitor-update-card"

                              key={`${update.title}-${index}`}
                            >


                              <div className="update-meta">

                                <span
                                  className={
                                    `update-category category-${update.category}`
                                  }
                                >

                                  {update.category}

                                </span>


                                {update.date && (

                                  <span className="update-date">

                                    {update.date}

                                  </span>

                                )}

                              </div>


                              <h4>

                                {update.title}

                              </h4>


                              <p className="update-summary">

                                {update.summary}

                              </p>


                              <div className="why-it-matters">

                                <span>

                                  WHY IT MATTERS

                                </span>


                                <p>

                                  {update.why_it_matters}

                                </p>

                              </div>


                              {update.source && (

                                <a
                                  href={update.source}

                                  target="_blank"

                                  rel="noopener noreferrer"

                                  className="competitor-source-link"
                                >

                                  VIEW SOURCE ↗

                                </a>

                              )}

                            </article>

                          )
                        )}

                      </div>

                    )}

                  </article>

                )
              )}

            </div>

          </section>

        )}


      </div>

    </div>

  );

}


export default CompetitorAgent;