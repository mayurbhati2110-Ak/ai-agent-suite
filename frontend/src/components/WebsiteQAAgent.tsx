import { useEffect, useState } from "react";
import "../index2.css";


interface WebsiteQAAgentProps {
  onBack: () => void;
  initialUrl?: string;
}


interface QAIssue {
  severity: string;
  category: string;
  page?: string | null;
  issue: string;
  recommendation: string;
}


interface SEOReport {
  title?: string | null;
  meta_description?: string | null;
  h1_count?: number | null;
}


interface WebsiteQAResponse {
  success: boolean;
  url: string;
  summary: string;

  data: {
    confirmed_issues: QAIssue[];
    suspected_issues: QAIssue[];
    seo_report: SEOReport;
    priority_actions: string[];
  };
}


function WebsiteQAAgent({
  onBack,
  initialUrl = ""
}: WebsiteQAAgentProps) {

  const [url, setUrl] =
    useState(initialUrl);

  const [response, setResponse] =
    useState<WebsiteQAResponse | null>(
      null
    );

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  useEffect(() => {

    if (initialUrl) {

      setUrl(initialUrl);

      setResponse(null);

      setError(null);

    }

  }, [initialUrl]);


  const handleAnalyze = async () => {

    if (!url.trim() || loading) {
      return;
    }

    setLoading(true);

    setError(null);

    setResponse(null);

    try {

      const apiResponse = await fetch(
        "http://127.0.0.1:8000/api/website-qa/analyze",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json"
          },

          body: JSON.stringify({
            url: url.trim()
          })
        }
      );


      if (!apiResponse.ok) {

        let errorMessage =
          "Failed to analyze website.";

        try {

          const errorData =
            await apiResponse.json();

          errorMessage =
            errorData.detail ||
            errorMessage;

        } catch {
          // Keep default message
        }

        throw new Error(
          errorMessage
        );

      }


      const data: WebsiteQAResponse =
        await apiResponse.json();

      setResponse(data);

      setUrl(data.url);

    } catch (err) {

      const errorMessage =
        err instanceof Error
          ? err.message
          : "Something went wrong while analyzing the website.";

      setError(errorMessage);

    } finally {

      setLoading(false);

    }

  };


  const getSeverityClass = (
    severity: string
  ) => {

    return severity
      .toLowerCase()
      .replace(/\s+/g, "-");

  };


  return (

    <div className="website-qa-agent">


      {/* TOP BAR */}

      <div className="website-qa-topbar">

        <button
          className="website-qa-back-button"
          onClick={onBack}
        >
          ← BACK TO AGENT SUITE
        </button>


        <div className="website-qa-status">

          <span className="website-qa-status-dot"></span>

          AI WEBSITE QA AGENT

        </div>

      </div>


      {/* MAIN CONTENT */}

      <div className="website-qa-content">


        {/* HERO */}

        <section className="website-qa-hero">

          <div className="website-qa-icon">
            ◈
          </div>


          <div>

            <span className="website-qa-eyebrow">
              AGENT 03 / WEBSITE INTELLIGENCE
            </span>


            <h1>
              AI Website QA Agent
            </h1>


            <p>
              Inspect websites for broken links,
              missing images, SEO problems and
              potential content or usability issues.
            </p>

          </div>

        </section>


        {/* INPUT PANEL */}

        <section className="website-qa-input-panel">

          <div className="website-qa-panel-header">

            <span>
              ◈ WEBSITE TO INSPECT
            </span>


            <span className="website-qa-input-status">

              READY FOR ANALYSIS

            </span>

          </div>


          <div className="website-url-input-row">

            <input
              type="text"

              value={url}

              placeholder="example.com or https://example.com"

              onChange={(event) =>
                setUrl(
                  event.target.value
                )
              }

              onKeyDown={(event) => {

                if (event.key === "Enter") {

                  handleAnalyze();

                }

              }}

              disabled={loading}
            />

          </div>


          <div className="website-qa-panel-footer">

            <span className="website-qa-hint">

              ⓘ Enter a domain or full URL.
              The agent automatically handles
              common URL formats.

            </span>


            <button
              className="website-qa-analyze-button"

              onClick={handleAnalyze}

              disabled={
                !url.trim() ||
                loading
              }
            >

              {loading
                ? "INSPECTING..."
                : "✦ RUN WEBSITE QA →"
              }

            </button>

          </div>

        </section>


        {/* ERROR */}

        {error && (

          <div className="website-qa-error">

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

          <section className="website-qa-results">


            {/* RESULTS HEADER */}

            <div className="website-qa-results-header">

              <div>

                <span className="website-qa-results-label">
                  ✦ WEBSITE QUALITY REPORT
                </span>

                <h2>
                  Analysis Results
                </h2>

              </div>


              <span className="website-qa-complete-badge">
                COMPLETE
              </span>

            </div>


            {/* ANALYZED URL */}

            <div className="analyzed-url-card">

              <span>
                ANALYZED WEBSITE
              </span>

              <strong>
                {response.url}
              </strong>

            </div>


            {/* SUMMARY */}

            <div className="website-qa-summary">

              <span>
                QA SUMMARY
              </span>

              <p>
                {response.summary}
              </p>

            </div>


            {/* OVERVIEW */}

            <div className="website-qa-overview">

              <div className="qa-overview-card">

                <span>
                  CONFIRMED
                </span>

                <strong>
                  {response.data.confirmed_issues.length}
                </strong>

                <p>
                  Automated issues detected
                </p>

              </div>


              <div className="qa-overview-card">

                <span>
                  SUSPECTED
                </span>

                <strong>
                  {response.data.suspected_issues.length}
                </strong>

                <p>
                  Issues requiring review
                </p>

              </div>


              <div className="qa-overview-card">

                <span>
                  H1 HEADINGS
                </span>

                <strong>
                  {response.data.seo_report.h1_count ??
                    "—"}
                </strong>

                <p>
                  Primary headings detected
                </p>

              </div>

            </div>


            {/* CONFIRMED ISSUES */}

            <section className="qa-issues-section">

              <div className="qa-section-heading">

                <div>

                  <span>
                    CONFIRMED ISSUES
                  </span>

                  <p>
                    Issues detected through
                    automated website checks.
                  </p>

                </div>


                <span className="qa-count">
                  {response.data.confirmed_issues.length}
                </span>

              </div>


              {response.data.confirmed_issues.length === 0 ? (

                <div className="qa-empty-state">

                  ✓ No confirmed issues detected.

                </div>

              ) : (

                <div className="qa-issue-list">

                  {response.data.confirmed_issues.map(
                    (item, index) => (

                      <QAIssueCard
                        key={index}
                        issue={item}
                        getSeverityClass={
                          getSeverityClass
                        }
                      />

                    )
                  )}

                </div>

              )}

            </section>


            {/* SUSPECTED ISSUES */}

            <section className="qa-issues-section suspected-section">

              <div className="qa-section-heading">

                <div>

                  <span>
                    SUSPECTED ISSUES
                  </span>

                  <p>
                    AI observations that should
                    be reviewed before confirmation.
                  </p>

                </div>


                <span className="qa-count">
                  {response.data.suspected_issues.length}
                </span>

              </div>


              {response.data.suspected_issues.length === 0 ? (

                <div className="qa-empty-state">

                  ✓ No suspected issues identified.

                </div>

              ) : (

                <div className="qa-issue-list">

                  {response.data.suspected_issues.map(
                    (item, index) => (

                      <QAIssueCard
                        key={index}
                        issue={item}
                        getSeverityClass={
                          getSeverityClass
                        }
                      />

                    )
                  )}

                </div>

              )}

            </section>


            {/* SEO REPORT */}

            <section className="seo-report-section">

              <div className="seo-report-header">

                <span>
                  BASIC SEO REPORT
                </span>

              </div>


              <div className="seo-grid">

                <div className="seo-item">

                  <span>
                    PAGE TITLE
                  </span>

                  <p>
                    {response.data.seo_report.title ||
                      "Not detected"}
                  </p>

                </div>


                <div className="seo-item">

                  <span>
                    META DESCRIPTION
                  </span>

                  <p>
                    {response.data.seo_report.meta_description ||
                      "Not detected"}
                  </p>

                </div>


                <div className="seo-item">

                  <span>
                    H1 COUNT
                  </span>

                  <p>
                    {response.data.seo_report.h1_count ??
                      "Not detected"}
                  </p>

                </div>

              </div>

            </section>


            {/* PRIORITY ACTIONS */}

            <section className="priority-actions">

              <div className="priority-actions-header">

                <span>
                  ✦ PRIORITY ACTIONS
                </span>

              </div>


              {response.data.priority_actions.length === 0 ? (

                <div className="qa-empty-state">

                  No priority actions generated.

                </div>

              ) : (

                <ol>

                  {response.data.priority_actions.map(
                    (action, index) => (

                      <li key={index}>
                        {action}
                      </li>

                    )
                  )}

                </ol>

              )}

            </section>


          </section>

        )}

      </div>

    </div>

  );

}


interface QAIssueCardProps {
  issue: QAIssue;

  getSeverityClass: (
    severity: string
  ) => string;
}


function QAIssueCard({
  issue,
  getSeverityClass
}: QAIssueCardProps) {

  return (

    <article className="qa-issue-card">


      <div className="qa-issue-top">

        <span
          className={
            `severity-badge ${getSeverityClass(
              issue.severity
            )}`
          }
        >
          {issue.severity}
        </span>


        <span className="qa-category">

          {issue.category.replace(
            /_/g,
            " "
          )}

        </span>

      </div>


      <h3>
        {issue.issue}
      </h3>


      {issue.page && (

        <p className="qa-page">

          {issue.page}

        </p>

      )}


      <div className="qa-recommendation">

        <span>
          RECOMMENDATION
        </span>

        <p>
          {issue.recommendation}
        </p>

      </div>

    </article>

  );

}


export default WebsiteQAAgent;