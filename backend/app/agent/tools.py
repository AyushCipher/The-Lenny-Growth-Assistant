from typing import Any
from app.rag.retriever import retriever
from app.observability.logging import logger


class AgentToolRegistry:
    """
    Standardized Tool Registry aligned with the Anthropic Claude Agent SDK tool-calling protocol.
    """
    @staticmethod
    def get_tool_definitions() -> list[dict[str, Any]]:
        return [
            {
                "name": "search_transcripts",
                "description": "Searches Lenny's Podcast transcripts using Hybrid RRF (BM25 + Dense Semantic search) for product and growth strategy wisdom.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query, framework name (e.g. SPADE, PMF 40% rule, PLG), or guest name (e.g. Shreyas Doshi, Elena Verna)."
                        },
                        "top_k": {
                            "type": "integer",
                            "default": 5,
                            "description": "Number of high-signal transcript chunks to retrieve."
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "format_ship30_essay",
                "description": "Formats grounded Lenny podcast insights into an atomic ~1,250-word Ship 30 for 30 essay with hook, 1-3-1 cadence, bolding, and action checklist.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Core strategic topic"},
                        "target_audience": {"type": "string", "default": "Product Managers & Growth Leaders"},
                        "core_takeaway": {"type": "string", "description": "Key implementation action"}
                    },
                    "required": ["topic"]
                }
            },
            {
                "name": "create_artifact",
                "description": "Creates an interactive HTML/CSS tool, calculator, PM framework, or Markdown document rendered natively in the split-pane Artifact Viewer.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Descriptive artifact title"},
                        "type": {"type": "string", "enum": ["html", "markdown"], "description": "Artifact markup type"},
                        "content": {"type": "string", "description": "Complete HTML/CSS or Markdown code"}
                    },
                    "required": ["title", "type", "content"]
                }
            }
        ]

    @staticmethod
    def execute_search_transcripts(query: str, top_k: int = 5):
        results, latency_ms = retriever.retrieve(query, top_k=top_k)
        context = retriever.format_grounding_context(results)
        citations = retriever.extract_citations(results)
        return {
            "results_count": len(results),
            "latency_ms": latency_ms,
            "context": context,
            "citations": [c.dict() for c in citations]
        }
