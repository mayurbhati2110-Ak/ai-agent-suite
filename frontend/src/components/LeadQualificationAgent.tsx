import { useEffect, useMemo, useRef, useState } from "react";
import "../index3.css";

interface LeadQualificationAgentProps {
  onBack: () => void;
  initialCSV?: string;
  initialICP?: ICP;
}

interface ICP {
  target_industries: string[];
  company_size_min: number | null;
  company_size_max: number | null;
  target_locations: string[];
  required_technologies: string[];
  target_business_models: string[];
  additional_criteria: string[];
}

interface QualificationReason {
  criterion: string;
  status: "match" | "partial" | "not_match" | "unknown";
  explanation: string;
}

interface QualifiedLead {
  company: string;
  website?: string | null;
  score: number;
  fit: "high" | "medium" | "low";
  reasons: QualificationReason[];
  known_information: Record<string, unknown>;
  unknown_information: string[];
  research_sources: string[];
}

interface LeadQualificationResponse {
  success: boolean;
  summary: string;
  data: {
    total_leads: number;
    qualified_leads: number;
    leads: QualifiedLead[];
    top_prospects: QualifiedLead[];
  };
}

const defaultICP: ICP = {
  target_industries: ["SaaS", "FinTech"],
  company_size_min: 100,
  company_size_max: 10000,
  target_locations: ["USA", "UK"],
  required_technologies: ["Python", "AWS"],
  target_business_models: ["B2B"],
  additional_criteria: [],
};

function LeadQualificationAgent({
  onBack,
  initialCSV = "",
  initialICP = defaultICP,
}: LeadQualificationAgentProps) {
  const [csvText, setCsvText] = useState(initialCSV);

  const [icp, setIcp] = useState<ICP>(
    initialICP || defaultICP
  );

  const [response, setResponse] =
    useState<LeadQualificationResponse | null>(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const fileInputRef =
    useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (initialCSV) {
      setCsvText(initialCSV);
      setResponse(null);
      setError(null);
    }

    if (initialICP) {
      setIcp(initialICP);
    }
  }, [initialCSV, initialICP]);

  const leadCount = useMemo(() => {
    if (!csvText.trim()) {
      return 0;
    }

    const lines = csvText
      .trim()
      .split("\n")
      .filter(Boolean);

    return Math.max(lines.length - 1, 0);
  }, [csvText]);

  const updateICPList = (
    field:
      | "target_industries"
      | "target_locations"
      | "required_technologies"
      | "target_business_models"
      | "additional_criteria",
    value: string
  ) => {
    setIcp((previous) => ({
      ...previous,
      [field]: value
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
    }));
  };

  const handleFileUpload = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    if (!file.name.toLowerCase().endsWith(".csv")) {
      setError("Please select a CSV file.");
      return;
    }

    const reader = new FileReader();

    reader.onload = () => {
      setCsvText(
        typeof reader.result === "string"
          ? reader.result
          : ""
      );

      setResponse(null);
      setError(null);
    };

    reader.readAsText(file);
  };

  const handleAnalyze = async () => {
    if (!csvText.trim()) {
      setError("Please upload or load a CSV file.");
      return;
    }

    if (loading) {
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const csvFile = new File(
        [csvText],
        "leads.csv",
        {
          type: "text/csv",
        }
      );

      const formData = new FormData();

      formData.append(
        "file",
        csvFile
      );

      formData.append(
        "icp",
        JSON.stringify(icp)
      );

      const apiResponse = await fetch(
        "http://127.0.0.1:8000/api/lead-qualification/analyze",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await apiResponse.json();

      if (!apiResponse.ok) {
        throw new Error(
          data.detail ||
          "Lead qualification failed."
        );
      }

      setResponse(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to analyze leads."
      );
    } finally {
      setLoading(false);
    }
  };

  const clearResults = () => {
    setResponse(null);
    setError(null);
  };

  const getStatusClass = (
    status: QualificationReason["status"]
  ) => {
    return `lead-status lead-status-${status}`;
  };

  const getFitClass = (
    fit: QualifiedLead["fit"]
  ) => {
    return `lead-fit lead-fit-${fit}`;
  };

  return (
    <div className="lead-agent">

      {/* TOP BAR */}

      <div className="lead-topbar">

        <button
          className="lead-back-button"
          onClick={onBack}
        >
          ← BACK TO AGENTS
        </button>

        <div className="lead-status-indicator">
          <span className="lead-status-dot" />
          LEAD QUALIFICATION ONLINE
        </div>

      </div>


      <div className="lead-agent-content">

        {/* HERO */}

        <section className="lead-hero">

          <div className="lead-icon">
            ◈
          </div>

          <div>

            <span className="lead-eyebrow">
              AGENT 04 · PROSPECT INTELLIGENCE
            </span>

            <h1>
              AI Lead Qualification Agent
            </h1>

            <p>
              Upload a lead dataset, define your Ideal
              Customer Profile, and identify the prospects
              that best match your business requirements.
            </p>

          </div>

        </section>


        {/* INPUT GRID */}

        <div className="lead-input-grid">

          {/* CSV PANEL */}

          <section className="lead-panel">

            <div className="lead-panel-header">

              <div>
                <span>
                  LEAD DATASET
                </span>

                <small>
                  {leadCount} leads detected
                </small>
              </div>

              <button
                className="lead-upload-button"
                onClick={() =>
                  fileInputRef.current?.click()
                }
              >
                UPLOAD CSV
              </button>

              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                hidden
                onChange={handleFileUpload}
              />

            </div>


            <textarea
              className="lead-csv-editor"
              value={csvText}
              onChange={(event) =>
                setCsvText(event.target.value)
              }
              placeholder="Upload a CSV file or load the example..."
              spellCheck={false}
            />

            <div className="lead-panel-footer">
              Expected columns: company, website, industry,
              employees, location, contact_name, contact_email
            </div>

          </section>


          {/* ICP PANEL */}

          <section className="lead-panel">

            <div className="lead-panel-header">

              <div>
                <span>
                  IDEAL CUSTOMER PROFILE
                </span>

                <small>
                  Qualification criteria
                </small>
              </div>

            </div>


            <div className="lead-icp-form">

              <label>
                Target industries
                <input
                  value={icp.target_industries.join(", ")}
                  onChange={(event) =>
                    updateICPList(
                      "target_industries",
                      event.target.value
                    )
                  }
                  placeholder="SaaS, FinTech"
                />
              </label>


              <div className="lead-two-inputs">

                <label>
                  Min employees
                  <input
                    type="number"
                    value={
                      icp.company_size_min ?? ""
                    }
                    onChange={(event) =>
                      setIcp((previous) => ({
                        ...previous,
                        company_size_min:
                          event.target.value
                            ? Number(event.target.value)
                            : null,
                      }))
                    }
                  />
                </label>

                <label>
                  Max employees
                  <input
                    type="number"
                    value={
                      icp.company_size_max ?? ""
                    }
                    onChange={(event) =>
                      setIcp((previous) => ({
                        ...previous,
                        company_size_max:
                          event.target.value
                            ? Number(event.target.value)
                            : null,
                      }))
                    }
                  />
                </label>

              </div>


              <label>
                Target locations
                <input
                  value={icp.target_locations.join(", ")}
                  onChange={(event) =>
                    updateICPList(
                      "target_locations",
                      event.target.value
                    )
                  }
                  placeholder="USA, UK"
                />
              </label>


              <label>
                Required technologies
                <input
                  value={
                    icp.required_technologies.join(", ")
                  }
                  onChange={(event) =>
                    updateICPList(
                      "required_technologies",
                      event.target.value
                    )
                  }
                  placeholder="Python, AWS"
                />
              </label>


              <label>
                Business models
                <input
                  value={
                    icp.target_business_models.join(", ")
                  }
                  onChange={(event) =>
                    updateICPList(
                      "target_business_models",
                      event.target.value
                    )
                  }
                  placeholder="B2B"
                />
              </label>


              <label>
                Additional criteria
                <input
                  value={
                    icp.additional_criteria.join("; ")
                  }
                  onChange={(event) =>
                    setIcp((previous) => ({
                      ...previous,
                      additional_criteria:
                        event.target.value
                          .split(";")
                          .map((item) =>
                            item.trim()
                          )
                          .filter(Boolean),
                    }))
                  }
                  placeholder="Optional requirements"
                />
              </label>

            </div>

          </section>

        </div>


        {/* ACTION BAR */}

        <div className="lead-action-bar">

          <div>

            <span className="lead-action-title">
              Ready to qualify
            </span>

            <span className="lead-action-description">
              Research and score {leadCount} leads against
              the current ICP.
            </span>

          </div>

          <div className="lead-action-buttons">

            {response && (
              <button
                className="lead-clear-button"
                onClick={clearResults}
              >
                CLEAR RESULTS
              </button>
            )}

            <button
              className="lead-analyze-button"
              onClick={handleAnalyze}
              disabled={loading || leadCount === 0}
            >
              {loading
                ? "QUALIFYING..."
                : "QUALIFY LEADS →"}
            </button>

          </div>

        </div>


        {/* ERROR */}

        {error && (
          <div className="lead-error">
            <strong>Analysis failed</strong>
            <span>{error}</span>
          </div>
        )}


        {/* LOADING */}

        {loading && (
          <div className="lead-loading">

            <div className="lead-loading-spinner" />

            <div>
              <strong>
                Researching and qualifying leads
              </strong>

              <span>
                The agent is evaluating available evidence
                against your ICP.
              </span>
            </div>

          </div>
        )}


        {/* RESULTS */}

        {response && !loading && (

          <section className="lead-results">

            {/* SUMMARY */}

            <div className="lead-result-heading">

              <div>
                <span className="lead-eyebrow">
                  QUALIFICATION REPORT
                </span>

                <h2>
                  Lead Intelligence
                </h2>

                <p>
                  {response.summary}
                </p>
              </div>

            </div>


            {/* STAT CARDS */}

            <div className="lead-stat-grid">

              <div className="lead-stat-card">
                <span>
                  TOTAL LEADS
                </span>
                <strong>
                  {response.data.total_leads}
                </strong>
              </div>

              <div className="lead-stat-card">
                <span>
                  QUALIFIED
                </span>
                <strong>
                  {response.data.qualified_leads}
                </strong>
              </div>

              <div className="lead-stat-card">
                <span>
                  HIGH FIT
                </span>
                <strong>
                  {
                    response.data.leads.filter(
                      (lead) =>
                        lead.fit === "high"
                    ).length
                  }
                </strong>
              </div>

              <div className="lead-stat-card">
                <span>
                  AVG SCORE
                </span>
                <strong>
                  {Math.round(
                    response.data.leads.reduce(
                      (sum, lead) =>
                        sum + lead.score,
                      0
                    ) /
                    Math.max(
                      response.data.leads.length,
                      1
                    )
                  )}
                </strong>
              </div>

            </div>


            {/* TOP PROSPECTS */}

            <div className="lead-section-heading">

              <div>
                <span>
                  TOP PROSPECTS
                </span>

                <small>
                  Highest scoring leads
                </small>
              </div>

            </div>


            <div className="lead-prospect-grid">

              {response.data.top_prospects.map(
                (lead) => (

                  <div
                    className="lead-prospect-card"
                    key={lead.company}
                  >

                    <div className="lead-prospect-top">

                      <div>
                        <span className="lead-company-mark">
                          {lead.company
                            .charAt(0)
                            .toUpperCase()}
                        </span>

                        <div>
                          <strong>
                            {lead.company}
                          </strong>

                          <span>
                            {lead.website ||
                              "Website unavailable"}
                          </span>
                        </div>
                      </div>

                      <div className="lead-score">
                        <strong>
                          {lead.score}
                        </strong>
                        <span>
                          /100
                        </span>
                      </div>

                    </div>


                    <div className="lead-prospect-meta">

                      <span
                        className={getFitClass(
                          lead.fit
                        )}
                      >
                        {lead.fit.toUpperCase()} FIT
                      </span>

                      <span>
                        {lead.reasons.filter(
                          (reason) =>
                            reason.status ===
                            "match"
                        ).length}{" "}
                        criteria matched
                      </span>

                    </div>


                    <div className="lead-reason-list">

                      {lead.reasons
                        .filter(
                          (reason) =>
                            reason.status !==
                            "unknown"
                        )
                        .slice(0, 3)
                        .map(
                          (reason, index) => (

                            <div
                              className="lead-reason"
                              key={`${lead.company}-${index}`}
                            >

                              <span
                                className={getStatusClass(
                                  reason.status
                                )}
                              >
                                {reason.status ===
                                "match"
                                  ? "✓"
                                  : reason.status ===
                                    "partial"
                                  ? "~"
                                  : "×"}
                              </span>

                              <div>
                                <strong>
                                  {reason.criterion}
                                </strong>

                                <p>
                                  {reason.explanation}
                                </p>
                              </div>

                            </div>

                          )
                        )}

                    </div>

                  </div>

                )
              )}

            </div>


            {/* ALL LEADS */}

            <div className="lead-section-heading lead-all-heading">

              <div>
                <span>
                  ALL QUALIFIED LEADS
                </span>

                <small>
                  Ranked by deterministic ICP score
                </small>
              </div>

            </div>


            <div className="lead-table-wrapper">

              <table className="lead-table">

                <thead>
                  <tr>
                    <th>RANK</th>
                    <th>COMPANY</th>
                    <th>SCORE</th>
                    <th>FIT</th>
                    <th>MATCHED</th>
                    <th>UNKNOWN</th>
                  </tr>
                </thead>

                <tbody>

                  {response.data.leads.map(
                    (lead, index) => {

                      const matched =
                        lead.reasons.filter(
                          (reason) =>
                            reason.status ===
                            "match"
                        ).length;

                      const unknown =
                        lead.reasons.filter(
                          (reason) =>
                            reason.status ===
                            "unknown"
                        ).length;

                      return (
                        <tr key={lead.company}>

                          <td className="lead-rank">
                            #{index + 1}
                          </td>

                          <td>
                            <div className="lead-table-company">
                              <strong>
                                {lead.company}
                              </strong>

                              <span>
                                {lead.known_information
                                  .industry
                                  ? String(
                                      lead
                                        .known_information
                                        .industry
                                    )
                                  : "Industry unknown"}
                              </span>
                            </div>
                          </td>

                          <td>
                            <strong className="lead-table-score">
                              {lead.score}
                            </strong>
                          </td>

                          <td>
                            <span
                              className={getFitClass(
                                lead.fit
                              )}
                            >
                              {lead.fit}
                            </span>
                          </td>

                          <td>
                            {matched}
                          </td>

                          <td>
                            <span className="lead-unknown-count">
                              {unknown}
                            </span>
                          </td>

                        </tr>
                      );
                    }
                  )}

                </tbody>

              </table>

            </div>


            {/* DETAILED REASONS */}

            <div className="lead-section-heading lead-all-heading">

              <div>
                <span>
                  EVIDENCE BREAKDOWN
                </span>

                <small>
                  Why each lead received its score
                </small>
              </div>

            </div>


            <div className="lead-evidence-list">

              {response.data.leads.map(
                (lead) => (

                  <details
                    className="lead-evidence-card"
                    key={`evidence-${lead.company}`}
                  >

                    <summary>

                      <div>
                        <strong>
                          {lead.company}
                        </strong>

                        <span>
                          {lead.score}/100 ·{" "}
                          {lead.fit} fit
                        </span>
                      </div>

                      <span>
                        VIEW EVIDENCE +
                      </span>

                    </summary>


                    <div className="lead-evidence-content">

                      {lead.reasons.map(
                        (reason, index) => (

                          <div
                            className="lead-evidence-row"
                            key={index}
                          >

                            <span
                              className={getStatusClass(
                                reason.status
                              )}
                            >
                              {reason.status}
                            </span>

                            <div>

                              <strong>
                                {reason.criterion}
                              </strong>

                              <p>
                                {reason.explanation}
                              </p>

                            </div>

                          </div>

                        )
                      )}


                      {lead.unknown_information.length >
                        0 && (

                        <div className="lead-unknown-box">

                          <strong>
                            UNKNOWN INFORMATION
                          </strong>

                          <ul>

                            {lead.unknown_information.map(
                              (item, index) => (
                                <li key={index}>
                                  {item}
                                </li>
                              )
                            )}

                          </ul>

                        </div>

                      )}

                    </div>

                  </details>

                )
              )}

            </div>

          </section>

        )}

      </div>

    </div>
  );
}

export default LeadQualificationAgent;