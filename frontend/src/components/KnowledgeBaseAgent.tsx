import { useState } from "react";
import "../index4.css";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  status?: "answered" | "insufficient_information" | "escalate";
}

interface KnowledgeSource {
  document: string;
  section: string | null;
}

interface KnowledgeBaseResponse {
  success: boolean;
  summary: string;
  data: {
    answer: string;
    sources: KnowledgeSource[];
    status: "answered" | "insufficient_information" | "escalate";
    context_used: boolean;
  };
}

const suggestedQuestions = [
  "How many annual leave days do employees get?",
  "Can I carry unused annual leave forward?",
  "How do I report an IT support issue?"
];

function KnowledgeBaseAgent() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const askQuestion = async () => {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) {
      return;
    }

    setError("");

    const userMessage: ChatMessage = {
      role: "user",
      content: trimmedQuestion
    };

    const updatedMessages = [
      ...messages,
      userMessage
    ];

    setMessages(updatedMessages);
    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/knowledge-base/answer",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            question: trimmedQuestion,
            conversation_history: messages
          })
        }
      );

      const result: KnowledgeBaseResponse =
        await response.json();

      if (!response.ok) {
        throw new Error(
          result?.summary ||
          "Failed to get an answer."
        );
      }

      const assistantMessage: ChatMessage = {
        role: "assistant",
        content:
          result.data.answer ||
          "The knowledge base does not contain enough information to answer this question.",
        status: result.data.status
      };

      setMessages([
        ...updatedMessages,
        assistantMessage
      ]);

    } catch (err) {
      console.error(err);

      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong while contacting the agent."
      );

      setMessages(messages);

    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (
    event: React.KeyboardEvent<HTMLTextAreaElement>
  ) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      askQuestion();
    }
  };

  const selectSuggestion = (
    suggestion: string
  ) => {
    setQuestion(suggestion);
  };

  return (
    <div className="kb-agent">

      {/* =========================
          HEADER
      ========================= */}

      <div className="kb-header">

        <div className="kb-header-icon">
          ✦
        </div>

        <div>
          <h1>Knowledge Base Support</h1>

          <p>
            Ask questions about NotRealOrg
          </p>
        </div>

      </div>

      {/* =========================
          CHAT AREA
      ========================= */}

      <div className="kb-chat">

        {messages.length === 0 && !loading && (
          <div className="kb-empty-state">

            <div className="kb-empty-icon">
              ?
            </div>

            <h2>
              How can I help you?
            </h2>

            <p>
              Ask me anything about NotRealOrg's
              policies, benefits, IT support,
              expenses, remote work and more.
            </p>

          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`kb-message ${
              message.role === "user"
                ? "kb-user-message"
                : "kb-assistant-message"
            }`}
          >

            <div className="kb-message-label">
              {message.role === "user"
                ? "You"
                : "NotRealOrg AI"}
            </div>

            <div className="kb-message-content">
              {message.content}
            </div>

            {/* Show KB note only for a successfully
                answered knowledge-base question */}

            {message.role === "assistant" &&
              index === messages.length - 1 &&
              message.status === "answered" && (
                <div className="kb-source-note">
                  Answer generated from the
                  NotRealOrg knowledge base
                </div>
              )}

          </div>
        ))}

        {loading && (
          <div className="kb-message kb-assistant-message">

            <div className="kb-message-label">
              NotRealOrg AI
            </div>

            <div className="kb-loading">
              <span></span>
              <span></span>
              <span></span>
            </div>

          </div>
        )}

        {error && (
          <div className="kb-error">
            {error}
          </div>
        )}

      </div>

      {/* =========================
          SUGGESTED QUESTIONS
      ========================= */}

      <div className="kb-suggestions">

        <span className="kb-suggestions-label">
          Try asking
        </span>

        <div className="kb-suggestion-list">

          {suggestedQuestions.map(
            (suggestion, index) => (
              <button
                key={index}
                type="button"
                className="kb-suggestion"
                onClick={() =>
                  selectSuggestion(suggestion)
                }
              >
                {suggestion}
              </button>
            )
          )}

        </div>

      </div>

      {/* =========================
          INPUT
      ========================= */}

      <div className="kb-input-area">

        <div className="kb-input-wrapper">

          <textarea
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about NotRealOrg..."
            rows={1}
            disabled={loading}
          />

          <button
            type="button"
            className="kb-send-button"
            onClick={askQuestion}
            disabled={
              loading ||
              !question.trim()
            }
            aria-label="Send question"
          >
            ➤
          </button>

        </div>

        <div className="kb-input-hint">
          Press Enter to send · Shift + Enter
          for a new line
        </div>

      </div>

    </div>
  );
}

export default KnowledgeBaseAgent;