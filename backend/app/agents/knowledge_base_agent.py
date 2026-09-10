import json

from openai import (
    APIConnectionError,
    APIError,
    RateLimitError
)

from app.schemas.knowledge_base import (
    KnowledgeBaseData,
    KnowledgeBaseResponse,
    ChatMessage
)

from app.services.knowledge_base_service import (
    KnowledgeBaseService
)

from app.services.llm_service import (
    LLMService
)


class KnowledgeBaseAgent:

    def __init__(self):

        self.knowledge_base_service = (
            KnowledgeBaseService()
        )

        self.llm_service = LLMService()

    # =========================
    # ANSWER QUESTION
    # =========================

    def answer(
        self,
        question: str,
        conversation_history: list[ChatMessage]
    ) -> KnowledgeBaseResponse:

        # -------------------------
        # Build retrieval query
        # -------------------------

        retrieval_query = question

        if conversation_history:

            previous_context = " ".join(
                message.content
                for message in conversation_history[-4:]
            )

            retrieval_query = (
                previous_context
                + " "
                + question
            )

        # -------------------------
        # Search knowledge base
        # -------------------------

        relevant_sections = (
            self.knowledge_base_service.search(
                retrieval_query,
                top_k=5
            )
        )

        context_used = bool(
            conversation_history
        )

        # -------------------------
        # No relevant information
        # -------------------------

        if not relevant_sections:

            return KnowledgeBaseResponse(
                success=True,
                summary=(
                    "The knowledge base does not contain "
                    "enough information to answer this question."
                ),
                data=KnowledgeBaseData(
                    answer=(
                        "I couldn't find this information in "
                        "the NotRealOrg knowledge base."
                    ),
                    sources=[],
                    status="insufficient_information",
                    context_used=context_used
                )
            )

        # -------------------------
        # Prepare KB context
        # -------------------------

        knowledge_context = []

        for index, section in enumerate(
            relevant_sections,
            start=1
        ):

            knowledge_context.append(
                f"""
SOURCE {index}

Document: {section["document"]}

Section: {section["section"]}

Content:
{section["content"]}
"""
            )

        knowledge_context = "\n".join(
            knowledge_context
        )

        # -------------------------
        # Conversation context
        # -------------------------

        conversation_context = ""

        if conversation_history:

            history_lines = []

            for message in conversation_history[-6:]:

                history_lines.append(
                    f"{message.role.upper()}: "
                    f"{message.content}"
                )

            conversation_context = "\n".join(
                history_lines
            )

        # -------------------------
        # Simple system prompt
        # -------------------------

        system_prompt = """
You are the NotRealOrg Knowledge-Base Support Agent.

Answer ONLY from the knowledge-base text provided.

Rules:

1. Never use outside knowledge.

2. Never invent, guess, assume, or add information.

3. If the answer is not explicitly present in the
   knowledge base, return status "insufficient_information".

4. Conversation history is only for understanding
   follow-up questions. It is NOT a source of facts.

5. Preserve numbers, dates, quantities, limits,
   and policy details exactly as written.

6. Use only document and section names that appear
   in the provided knowledge base.

7. Keep answers concise.

8. Return ONLY valid JSON.

JSON format:

{
    "answer": "string",
    "sources": [
        {
            "document": "string",
            "section": "string"
        }
    ],
    "status": "answered | insufficient_information | escalate",
    "context_used": true
}
"""

        # -------------------------
        # User prompt
        # -------------------------

        user_prompt = f"""
KNOWLEDGE BASE:

{knowledge_context}


CONVERSATION HISTORY:

{
    conversation_context
    if conversation_context
    else "None"
}


CURRENT QUESTION:

{question}


Answer the current question using ONLY the
knowledge-base text above.

If the requested information is not explicitly
contained in the knowledge base, return:

"status": "insufficient_information"

Do not add information from your own knowledge.

Return JSON only.
"""

        # -------------------------
        # Call LLM
        # -------------------------

        try:

            response = self.llm_service.chat(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                temperature=0.0
            )

        except APIConnectionError:

            raise RuntimeError(
                "Unable to connect to the LLM service."
            )

        except RateLimitError:

            raise RuntimeError(
                "LLM rate limit exceeded. "
                "Please try again later."
            )

        except APIError:

            raise RuntimeError(
                "The LLM service returned an error."
            )

        # -------------------------
        # Parse LLM response
        # -------------------------

        cleaned_response = response.strip()

        try:

            parsed_response = json.loads(
                cleaned_response
            )

            # Handle double-encoded JSON

            if isinstance(
                parsed_response,
                str
            ):

                parsed_response = json.loads(
                    parsed_response
                )

        except (
            json.JSONDecodeError,
            TypeError
        ):

            print(
                "LLM returned non-standard response."
            )

            answer_text = cleaned_response

            # Remove Markdown code fences

            if answer_text.startswith("```"):

                lines = (
                    answer_text.splitlines()
                )

                if (
                    lines
                    and
                    lines[0].strip().startswith("```")
                ):

                    lines = lines[1:]

                if (
                    lines
                    and
                    lines[-1].strip() == "```"
                ):

                    lines = lines[:-1]

                answer_text = (
                    "\n".join(lines).strip()
                )

            # Try JSON again

            try:

                parsed_response = json.loads(
                    answer_text
                )

                if isinstance(
                    parsed_response,
                    str
                ):

                    parsed_response = json.loads(
                        parsed_response
                    )

            except json.JSONDecodeError:

                # -------------------------
                # Fallback structured response
                # -------------------------

                valid_sources = []

                for section in relevant_sections:

                    valid_sources.append({
                        "document": (
                            section["document"]
                        ),
                        "section": (
                            section["section"]
                        )
                    })

                parsed_response = {
                    "answer": answer_text,
                    "sources": valid_sources[:1],
                    "status": "answered",
                    "context_used": context_used
                }

        # -------------------------
        # Validate response
        # -------------------------

        data = KnowledgeBaseData(
            **parsed_response
        )

        # Never trust LLM for context_used

        data.context_used = context_used

        # -------------------------
        # Validate citations
        # -------------------------

        valid_sources = []

        for source in data.sources:

            for section in relevant_sections:

                if (
                    source.document
                    == section["document"]
                    and
                    source.section
                    == section["section"]
                ):

                    valid_sources.append(
                        source
                    )

                    break

        data.sources = valid_sources

        # -------------------------
        # Final citation check
        # -------------------------

        if (
            data.status == "answered"
            and not data.sources
        ):

            data.status = (
                "insufficient_information"
            )

            data.answer = (
                "I couldn't verify this answer "
                "against the available NotRealOrg "
                "knowledge-base sources."
            )

        # -------------------------
        # Summary
        # -------------------------

        if data.status == "answered":

            summary = (
                "Question answered using the "
                "NotRealOrg knowledge base."
            )

        elif data.status == "escalate":

            summary = (
                "The question requires assistance "
                "beyond the available documentation."
            )

        else:

            summary = (
                "The knowledge base does not contain "
                "enough information to answer this question."
            )

        # -------------------------
        # Final response
        # -------------------------

        return KnowledgeBaseResponse(
            success=True,
            summary=summary,
            data=data
        )