import { useEffect, useState } from "react";

interface MeetingAgentProps {
  onBack: () => void;
  initialTranscript?: string;
}

interface Decision {
  decision: string;
  context: string | null;
}

interface Task {
  task: string;
  owner: string | null;
  deadline: string | null;
  status: string;
}

interface UnresolvedQuestion {
  question: string;
  context: string | null;
}

interface FollowUp {
  action: string;
  owner: string | null;
  deadline: string | null;
}

interface Contradiction {
  topic: string;
  statement_1: string;
  statement_2: string;
  explanation: string | null;
}

interface UnclearInstruction {
  instruction: string;
  reason: string;
}

interface MeetingAnalysis {
  decisions: Decision[];
  tasks: Task[];
  unresolved_questions: UnresolvedQuestion[];
  follow_ups: FollowUp[];
  contradictions: Contradiction[];
  unclear_instructions: UnclearInstruction[];
}

interface MeetingResponse {
  success: boolean;
  data: MeetingAnalysis;
  summary: string;
}

function MeetingAgent({
  onBack,
  initialTranscript = "",
}: MeetingAgentProps) {
  const [transcript, setTranscript] = useState(initialTranscript);

  useEffect(() => {
  if (initialTranscript) {
    setTranscript(initialTranscript);
    setResponse(null);
    setError(null);
  }
}, [initialTranscript]);

  const [response, setResponse] =
    useState<MeetingResponse | null>(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!transcript.trim()) return;

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const apiResponse = await fetch(
        "http://127.0.0.1:8000/api/meeting/analyze",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            transcript,
          }),
        }
      );

      if (!apiResponse.ok) {
        const errorData = await apiResponse.json();

        throw new Error(
          errorData.detail ||
            "Failed to analyze the meeting."
        );
      }

      const data: MeetingResponse =
        await apiResponse.json();

      setResponse(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong while analyzing the meeting."
      );
    } finally {
      setLoading(false);
    }
  };

  const analysis = response?.data;

  return (
    <div className="meeting-agent">

      {/* TOP BAR */}

      <div className="meeting-topbar">
        <button
          className="back-button"
          onClick={onBack}
        >
          ← BACK TO AGENT SUITE
        </button>

        <div className="agent-status">
          <span className="status-dot"></span>
          AI MEETING AGENT
        </div>
      </div>

      <div className="meeting-agent-content">

        {/* TITLE */}

        <div className="meeting-hero">
          <div className="meeting-icon">
            🎙
          </div>

          <div>
            <span className="eyebrow">
              AGENT 01 / MEETING ANALYSIS
            </span>

            <h1>AI Meeting Agent</h1>

            <p>
              Paste a meeting transcript and let the agent
              analyze, structure, and extract meaningful
              insights.
            </p>
          </div>
        </div>

        {/* TRANSCRIPT INPUT */}

        <div className="transcript-panel">

          <div className="panel-header">
            <span>▣ MEETING TRANSCRIPT</span>

            <span className="character-count">
              {transcript.length} CHARACTERS
            </span>
          </div>

          <textarea
            value={transcript}
            onChange={(e) =>
              setTranscript(e.target.value)
            }
            placeholder="Paste your meeting transcript here..."
            disabled={loading}
          />

          <div className="panel-footer">

            <span className="input-hint">
              ⓘ Your transcript will be processed by the
              AI Meeting Agent.
            </span>

            <button
              className="analyze-button"
              onClick={handleAnalyze}
              disabled={
                !transcript.trim() || loading
              }
            >
              {loading
                ? "ANALYZING..."
                : "✦ ANALYZE MEETING →"}
            </button>

          </div>
        </div>

        {/* ERROR */}

        {error && (
          <div className="error-panel">
            <strong>ANALYSIS FAILED</strong>
            <p>{error}</p>
          </div>
        )}

        {/* AI ANALYSIS */}

        {analysis && (
          <section className="ai-analysis">

            {/* ANALYSIS HEADER */}

            <div className="analysis-header">

              <div className="analysis-title">
                <span className="analysis-sparkle">
                  ✦
                </span>

                <span>AI ANALYSIS</span>
              </div>

              <div className="analysis-meta">

                <span className="complete-badge">
                  COMPLETE
                </span>

                <span className="analysis-time">
                  ◷ DONE
                </span>

              </div>

            </div>

            {/* SUMMARY */}

            <div className="summary-card">

              <div className="summary-icon">
                ▤
              </div>

              <div>

                <span className="summary-label">
                  SUMMARY
                </span>

                <p>
                  {response?.summary ||
                    "Meeting analysis completed successfully."}
                </p>

              </div>

            </div>

            {/* ANALYSIS CARDS */}

            <div className="analysis-grid">

              {/* DECISIONS */}

              <section className="analysis-card decisions-card">

                <CardHeader
                  icon="✓"
                  title="DECISIONS"
                  count={analysis.decisions.length}
                />

                {analysis.decisions.length === 0 ? (
                  <EmptyState
                    icon="◈"
                    text="No decisions were made during this meeting."
                  />
                ) : (
                  analysis.decisions.map(
                    (item, index) => (
                      <div
                        className="simple-item"
                        key={index}
                      >
                        <strong>
                          {item.decision}
                        </strong>

                        {item.context && (
                          <p>
                            {item.context}
                          </p>
                        )}
                      </div>
                    )
                  )
                )}

              </section>

              {/* TASKS */}

              <section className="analysis-card tasks-card">

                <CardHeader
                  icon="☷"
                  title="TASKS"
                  count={analysis.tasks.length}
                />

                <div className="task-list">

                  {analysis.tasks.length === 0 ? (
                    <EmptyState
                      icon="◌"
                      text="No tasks were identified."
                    />
                  ) : (
                    analysis.tasks.map(
                      (task, index) => (
                        <div
                          className="task-item"
                          key={index}
                        >

                          <span className="task-dot"></span>

                          <div className="task-main">

                            <strong>
                              {task.task}
                            </strong>

                            <p>
                              Owner:{" "}
                              {task.owner ||
                                "Not assigned"}

                              <span>│</span>

                              Deadline:{" "}
                              {task.deadline ||
                                "Not set"}
                            </p>

                          </div>

                          <span className="task-status">
                            {task.status}
                          </span>

                        </div>
                      )
                    )
                  )}

                </div>

              </section>

              {/* UNRESOLVED QUESTIONS */}

              <section className="analysis-card questions-card">

                <CardHeader
                  icon="?"
                  title="UNRESOLVED QUESTIONS"
                  count={
                    analysis.unresolved_questions.length
                  }
                />

                {analysis.unresolved_questions.length ===
                0 ? (
                  <EmptyState
                    icon="?"
                    text="No unresolved questions."
                  />
                ) : (
                  analysis.unresolved_questions.map(
                    (item, index) => (
                      <div
                        className="question-item"
                        key={index}
                      >

                        <span className="question-dot"></span>

                        <div>

                          <strong>
                            {item.question}
                          </strong>

                          {item.context && (
                            <p>
                              Context: {item.context}
                            </p>
                          )}

                        </div>

                      </div>
                    )
                  )
                )}

              </section>

              {/* CONTRADICTIONS */}

              <section className="analysis-card contradictions-card">

                <CardHeader
                  icon="△"
                  title="CONTRADICTIONS"
                  count={
                    analysis.contradictions.length
                  }
                />

                {analysis.contradictions.length === 0 ? (
                  <EmptyState
                    icon="△"
                    text="No contradictions detected."
                  />
                ) : (
                  analysis.contradictions.map(
                    (item, index) => (
                      <div
                        className="contradiction-item"
                        key={index}
                      >

                        <strong>
                          {item.topic}
                        </strong>

                        <div className="statement first">
                          {item.statement_1}
                        </div>

                        <span className="vs">
                          VS
                        </span>

                        <div className="statement second">
                          {item.statement_2}
                        </div>

                        {item.explanation && (
                          <p>
                            {item.explanation}
                          </p>
                        )}

                      </div>
                    )
                  )
                )}

              </section>

              {/* FOLLOW UPS */}

              <section className="analysis-card followups-card">

                <CardHeader
                  icon="◷"
                  title="FOLLOW UPS"
                  count={analysis.follow_ups.length}
                />

                {analysis.follow_ups.length === 0 ? (
                  <EmptyState
                    icon="□"
                    text="No follow-ups were mentioned during this meeting."
                  />
                ) : (
                  analysis.follow_ups.map(
                    (item, index) => (
                      <div
                        className="simple-item"
                        key={index}
                      >

                        <strong>
                          {item.action}
                        </strong>

                        <p>
                          Owner:{" "}
                          {item.owner ||
                            "Not assigned"}

                          <br />

                          Deadline:{" "}
                          {item.deadline ||
                            "Not set"}
                        </p>

                      </div>
                    )
                  )
                )}

              </section>

              {/* UNCLEAR INSTRUCTIONS */}

              <section className="analysis-card unclear-card">

                <CardHeader
                  icon="!"
                  title="UNCLEAR INSTRUCTIONS"
                  count={
                    analysis.unclear_instructions.length
                  }
                />

                {analysis.unclear_instructions.length ===
                0 ? (
                  <EmptyState
                    icon="!"
                    text="No unclear instructions."
                  />
                ) : (
                  analysis.unclear_instructions.map(
                    (item, index) => (
                      <div
                        className="unclear-item"
                        key={index}
                      >

                        <span className="unclear-dot"></span>

                        <div>

                          <strong>
                            {item.instruction}
                          </strong>

                          <p>
                            Reason: {item.reason}
                          </p>

                        </div>

                      </div>
                    )
                  )
                )}

              </section>

            </div>

          </section>
        )}

      </div>
    </div>
  );
}


/* =========================================
   REUSABLE CARD HEADER
========================================= */

interface CardHeaderProps {
  icon: string;
  title: string;
  count: number;
}

function CardHeader({
  icon,
  title,
  count,
}: CardHeaderProps) {
  return (
    <div className="analysis-card-header">

      <div className="card-title">

        <span className="card-icon">
          {icon}
        </span>

        <span>{title}</span>

      </div>

      <span className="count-badge">
        {count}
      </span>

    </div>
  );
}


/* =========================================
   EMPTY STATE
========================================= */

interface EmptyStateProps {
  icon: string;
  text: string;
}

function EmptyState({
  icon,
  text,
}: EmptyStateProps) {
  return (
    <div className="empty-state">

      <span>{icon}</span>

      <p>{text}</p>

    </div>
  );
}

export default MeetingAgent;