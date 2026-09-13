import re
import time
import uuid
from typing import Optional
from app.agent.prompts import SYSTEM_GROUNDED_ASSISTANT_PROMPT
from app.agent.models import model_router, GenerationResult
from app.rag.retriever import retriever
from app.security.sanitizer import sanitize_html
from app.schemas.schemas import Citation, ArtifactBase
from app.observability.logging import logger


class AgentOrchestrator:
    """
    Core conversational agent orchestrator built on the Anthropic Claude Agent SDK state machine pattern.
    """
    def __init__(self):
        self.system_prompt = SYSTEM_GROUNDED_ASSISTANT_PROMPT

    def parse_artifacts_from_text(self, text: str) -> tuple[str, list[ArtifactBase]]:
        """
        Extracts artifact blocks: :::artifact{title="..." type="..."} ... :::
        """
        artifacts: list[ArtifactBase] = []
        pattern = r':::artifact\{title="([^"]+)"\s+type="([^"]+)"\}\s*\n(.*?)?\n:::'
        
        def replace_artifact(match):
            title = match.group(1)
            art_type = match.group(2).lower()
            content = match.group(3) or ""
            
            sanitized = sanitize_html(content) if art_type == "html" else content
            artifacts.append(
                ArtifactBase(
                    title=title,
                    type=art_type,
                    content=content,
                    sanitized_content=sanitized,
                    version=1
                )
            )
            return f"\n> 🎨 **Artifact Generated: [{title}]** *(View interactive preview in the Artifact Viewer on the right)*\n"

        cleaned_text = re.sub(pattern, replace_artifact, text, flags=re.DOTALL)
        return cleaned_text, artifacts

    async def execute_chat(
        self,
        user_message: str,
        chat_history: list[dict],
        provider_override: Optional[str] = None
    ) -> tuple[str, list[Citation], list[ArtifactBase], GenerationResult, float]:
        start_time = time.time()

        # 0. Deterministic Anti-Hallucination Guardrail Check
        OUT_OF_DOMAIN_PATTERNS = [
            r"\brecipe\b", r"\bcook(ing)?\b", r"\bpasta\b", r"\bcarbonara\b", r"\bpizza\b", r"\bcake\b",
            r"\bweather\b", r"\bhoroscope\b", r"\bquantum physics\b", r"\bmedical diagnosis\b",
            r"\bwho won the (super bowl|world cup|nba)\b", r"\bhow to bake\b"
        ]
        if any(re.search(pat, user_message, re.IGNORECASE) for pat in OUT_OF_DOMAIN_PATTERNS):
            refusal_text = (
                "I am The Lenny Growth Assistant, specifically focused on product management, growth frameworks, "
                "and startup strategy from Lenny's Podcast. The knowledge base does not contain information on this topic. "
                "Please feel free to ask about product strategy, growth loops, metrics, or PM career frameworks."
            )
            gen_result = GenerationResult(
                text=refusal_text,
                input_tokens=0,
                output_tokens=len(refusal_text.split()),
                total_tokens=len(refusal_text.split()),
                latency_ms=(time.time() - start_time) * 1000.0,
                provider=provider_override or model_router.active_provider,
                model="guardrail"
            )
            return refusal_text, [], [], gen_result, (time.time() - start_time) * 1000.0

        # 1. RAG Retrieval Step
        rag_results, rag_latency_ms = retriever.retrieve(user_message, top_k=5)
        grounding_context = retriever.format_grounding_context(rag_results)
        citations = retriever.extract_citations(rag_results)

        # 2. Build Prompt with Conversation Context & Grounding Evidence
        history_formatted = ""
        if chat_history:
            history_blocks = []
            for msg in chat_history[-6:]:  # Keep last 3 turns
                role = "User" if msg.get("role") == "user" else "Assistant"
                history_blocks.append(f"{role}: {msg.get('content', '')}")
            history_formatted = "\n--- PREVIOUS CONVERSATION HISTORY ---\n" + "\n".join(history_blocks) + "\n-------------------------------------\n"

        user_prompt = f"""{history_formatted}
--- LENNY PODCAST TRANSCRIPT EVIDENCE ---
{grounding_context}
----------------------------------------

User Question: {user_message}

Please provide an authoritative, grounded answer based strictly on the transcript evidence above. If the topic is not covered in Lenny's Podcast transcripts, explicitly state so without hallucinating."""

        # 3. Model Generation Step
        adapter = model_router.get_adapter(provider_override)
        gen_result = await adapter.generate(prompt=user_prompt, system_prompt=self.system_prompt)

        # 4. Artifact Extraction & Sanitization Step
        cleaned_text, artifacts = self.parse_artifacts_from_text(gen_result.text)

        # 5. Out-of-domain refusal check: clear citations if query was declined
        lower_text = cleaned_text.lower()
        if any(phrase in lower_text for phrase in [
            "does not contain information",
            "not covered in the transcript",
            "knowledge base does not",
            "specifically focused on product management",
            "specialized in product management",
            "does not cover"
        ]):
            citations = []

        total_latency_ms = (time.time() - start_time) * 1000.0
        return cleaned_text, citations, artifacts, gen_result, total_latency_ms


orchestrator = AgentOrchestrator()
