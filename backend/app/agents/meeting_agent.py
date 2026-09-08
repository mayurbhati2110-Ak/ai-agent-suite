import json

from openai import APIConnectionError, APIError, RateLimitError

from app.schemas.meeting import (
    MeetingAnalysis,
    MeetingResponse
)

from app.services.llm_service import LLMService


class MeetingAgent:

    def __init__(self):
        self.llm = LLMService()


    def analyze(self, transcript: str) -> MeetingResponse:

        messages = [
            {
                "role": "system",
                "content": """
You are an AI Meeting-to-Action Agent.

Analyze meeting transcripts and extract actionable information.

You must:
- Extract confirmed decisions.
- Extract tasks and action items.
- Assign a task owner only when the transcript explicitly and
  unambiguously assigns that person responsibility for the task.
- Do not assume that the speaker giving an instruction is
  automatically the owner of that task.
- If the owner cannot be clearly determined, use null.
- Identify deadlines only when explicitly mentioned.
- Identify unresolved questions.
- Identify follow-ups.
- Detect contradictory instructions or statements.
- Identify unclear instructions that require clarification.

IMPORTANT RULES:
- Do not invent information.
- Do not guess missing owners or deadlines.
- Use null when optional information is not explicitly available.
- Do not treat suggestions as confirmed decisions unless they were
  clearly agreed upon.
- Only include information supported by the transcript.
- Return only valid JSON with no markdown or additional text.
- A direct instruction or request to perform an action should be
  classified as a task or action item, even if the owner is unknown.
- Do not move an actionable instruction into follow_ups merely because
  the owner or deadline is missing.
- Use follow_ups only for explicitly stated future discussions, checks,
  meetings, or actions that need to happen later.
- A task may also appear in unclear_instructions when the task itself
  is actionable but contains ambiguity that requires clarification.
"""
            },
            {
                "role": "user",
                "content": f"""
Analyze the following meeting transcript:

--------------------
{transcript}
--------------------

Return JSON using EXACTLY this structure:

{{
  "decisions": [
    {{
      "decision": "string",
      "context": null
    }}
  ],

  "tasks": [
    {{
      "task": "string",
      "owner": null,
      "deadline": null,
      "status": "pending"
    }}
  ],

  "unresolved_questions": [
    {{
      "question": "string",
      "context": null
    }}
  ],

  "follow_ups": [
    {{
      "action": "string",
      "owner": null,
      "deadline": null
    }}
  ],

  "contradictions": [
    {{
      "topic": "string",
      "statement_1": "string",
      "statement_2": "string",
      "explanation": null
    }}
  ],

  "unclear_instructions": [
    {{
      "instruction": "string",
      "reason": "string"
    }}
  ]
}}

IMPORTANT:
- Every item inside every list must be an object.
- Never return plain strings inside a list.
- Use null only when optional information is not explicitly known.
- If a category has no relevant items, return an empty list.
- Detect contradictions only when two statements genuinely conflict.
- Identify unclear instructions only when they cannot reasonably be
  executed without clarification.
- Return only the JSON object.
"""
            }
        ]

        # Contact the AI service
        try:
            response = self.llm.chat(
                messages=messages,
                temperature=0.1
            )

        except APIConnectionError:
            raise ValueError(
                "Unable to connect to the AI service. "
                "Please make sure FreeLLMAPI is running."
            )

        except RateLimitError:
            raise ValueError(
                "The AI service is temporarily rate-limited. "
                "Please try again later."
            )

        except APIError as error:
            raise ValueError(
                f"AI service error: {error}"
            )

        except Exception as error:
            raise ValueError(
                f"Unexpected error while contacting the AI service: {error}"
            )

        # Convert AI response string into Python JSON
        try:
            response_data = json.loads(response)

        except json.JSONDecodeError:
            raise ValueError(
                "The AI returned an invalid JSON response."
            )

        # Validate AI response against our Pydantic schema
        try:
            analysis = MeetingAnalysis.model_validate(
                response_data
            )

        except Exception as error:
            raise ValueError(
                f"The AI response did not match the expected structure: {error}"
            )

        summary = self.generate_summary(analysis)

        return MeetingResponse(
            success=True,
            data=analysis,
            summary=summary
        )


    def generate_summary(
        self,
        analysis: MeetingAnalysis
    ) -> str:

        parts = []

        if analysis.decisions:
            parts.append(
                f"{len(analysis.decisions)} confirmed decision(s) were identified."
            )

        if analysis.tasks:
            parts.append(
                f"{len(analysis.tasks)} action item(s) were identified."
            )

        if analysis.unresolved_questions:
            parts.append(
                f"{len(analysis.unresolved_questions)} unresolved question(s) remain."
            )

        if analysis.follow_ups:
            parts.append(
                f"{len(analysis.follow_ups)} follow-up item(s) were identified."
            )

        if analysis.contradictions:
            parts.append(
                f"{len(analysis.contradictions)} contradiction(s) require clarification."
            )

        if analysis.unclear_instructions:
            parts.append(
                f"{len(analysis.unclear_instructions)} unclear instruction(s) require clarification."
            )

        if not parts:
            return (
                "The meeting was analyzed, but no clear actionable "
                "information was identified."
            )

        return " ".join(parts)