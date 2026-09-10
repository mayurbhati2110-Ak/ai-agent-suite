from pathlib import Path
from typing import List, Dict


class KnowledgeBaseService:

    def __init__(self):

        # backend/knowledge_base
        self.knowledge_base_path = (
            Path(__file__).resolve().parents[2]
            / "knowledge_base"
        )

        self.documents = self._load_documents()

    # =========================
    # LOAD DOCUMENTS
    # =========================

    def _load_documents(self) -> List[Dict]:

        documents = []

        if not self.knowledge_base_path.exists():

            raise FileNotFoundError(
                f"Knowledge base directory not found: "
                f"{self.knowledge_base_path}"
            )

        for file_path in sorted(
            self.knowledge_base_path.glob("*.md")
        ):

            # README is documentation about the
            # dataset, not actual KB content.
            if file_path.name.lower() == "readme.md":
                continue

            content = file_path.read_text(
                encoding="utf-8"
            )

            sections = self._split_sections(
                content
            )

            for section in sections:

                documents.append({
                    "document": file_path.name,
                    "section": section["section"],
                    "content": section["content"]
                })

        return documents

    # =========================
    # SPLIT MARKDOWN SECTIONS
    # =========================

    def _split_sections(
        self,
        content: str
    ) -> List[Dict]:

        sections = []

        current_section = None
        current_content = []

        for line in content.splitlines():

            line = line.strip()

            if line.startswith("## "):

                # Save previous section
                if (
                    current_section
                    and current_content
                ):

                    sections.append({
                        "section": current_section,
                        "content": "\n".join(
                            current_content
                        ).strip()
                    })

                current_section = line[3:].strip()
                current_content = []

            elif current_section:

                if line:
                    current_content.append(line)

        # Save final section
        if (
            current_section
            and current_content
        ):

            sections.append({
                "section": current_section,
                "content": "\n".join(
                    current_content
                ).strip()
            })

        return sections

    # =========================
    # SEARCH KNOWLEDGE BASE
    # =========================

    def search(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict]:

        query_words = self._tokenize(query)

        if not query_words:
            return []

        scored_results = []

        for document in self.documents:

            section_text = document["section"]
            content_text = document["content"]

            full_content = (
                section_text
                + " "
                + content_text
            )

            content_words = self._tokenize(
                full_content
            )

            if not content_words:
                continue

            # Words appearing in both the
            # question and KB section.
            matched_words = (
                query_words & content_words
            )

            if not matched_words:
                continue

            # -------------------------
            # Require meaningful overlap
            # -------------------------

            # A single generic/common word should
            # not retrieve an unrelated section.
            if len(matched_words) < 2:
                continue

            # -------------------------
            # Relevance score
            # -------------------------

            score = len(matched_words)

            # Section heading is more important
            # than ordinary document content.
            section_words = self._tokenize(
                section_text
            )

            heading_matches = (
                query_words & section_words
            )

            score += (
                len(heading_matches) * 2
            )

            # Exact question phrase gets
            # a strong boost.
            query_lower = query.lower()
            content_lower = full_content.lower()

            if query_lower in content_lower:
                score += 5

            scored_results.append({
                **document,
                "score": score,
                "matched_words": matched_words
            })

        # -------------------------
        # Sort by relevance
        # -------------------------

        scored_results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        if not scored_results:
            return []

        # -------------------------
        # Relevance threshold
        # -------------------------

        best_score = (
            scored_results[0]["score"]
        )

        # Require at least two meaningful
        # matching words.
        if best_score < 2:
            return []

        return scored_results[:top_k]

    # =========================
    # TOKENIZATION
    # =========================

    @staticmethod
    def _tokenize(text: str) -> set:

        words = text.lower()

        # Keep only alphanumeric characters.
        cleaned = "".join(
            char if char.isalnum() else " "
            for char in words
        )

        stop_words = {
            "the",
            "is",
            "a",
            "an",
            "are",
            "to",
            "of",
            "in",
            "on",
            "for",
            "and",
            "or",
            "can",
            "do",
            "does",
            "did",
            "what",
            "how",
            "who",
            "when",
            "where",
            "why",
            "which",
            "i",
            "my",
            "me",
            "we",
            "they",
            "it",
            "this",
            "that",
            "those",
            "these",
            "you",
            "your",
            "our",
            "their"
        }

        return {
            word
            for word in cleaned.split()
            if len(word) > 2
            and word not in stop_words
        }

    # =========================
    # KNOWLEDGE BASE INFO
    # =========================

    def get_document_count(self) -> int:

        return len(
            {
                item["document"]
                for item in self.documents
            }
        )

    def get_section_count(self) -> int:

        return len(self.documents)