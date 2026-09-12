import time
from typing import Optional
from app.agent.prompts import SYSTEM_SHIP30_PROMPT
from app.agent.models import model_router, GenerationResult
from app.rag.retriever import retriever
from app.schemas.schemas import Citation, TokenUsage
from app.observability.logging import logger


class Ship30Skill:
    """
    Dedicated skill encoding the Ship 30 for 30 digital writing methodology grounded in Lenny's Podcast transcripts.
    """
    def __init__(self):
        self.system_prompt = SYSTEM_SHIP30_PROMPT

    async def generate_essay(
        self,
        topic: str,
        target_audience: str = "Product Managers & Growth Leaders",
        core_takeaway: Optional[str] = None,
        guest_focus: Optional[str] = None,
        provider_override: Optional[str] = None
    ) -> tuple[str, list[Citation], GenerationResult]:
        start_time = time.time()

        # 1. Retrieve high-signal podcast insights for topic and guest focus
        search_query = f"{topic} {guest_focus or ''}".strip()
        results, rag_latency = retriever.retrieve(search_query, top_k=6)
        grounding_context = retriever.format_grounding_context(results)
        citations = retriever.extract_citations(results)

        # 2. Build structured user prompt enforcing the ~1,250 words atomic essay structure
        default_guest_focus = "Synthesize top insights from Lenny's guests (Shreyas Doshi, Elena Verna, Brian Balfour, Julie Zhuo, Gokul Rajaram, Sean Ellis)"
        user_prompt = f"""Write an atomic Ship 30 for 30 essay on the following topic:
Topic: "{topic}"
Target Audience: {target_audience}
Core Takeaway to Drive: {core_takeaway or 'A practical, non-obvious framework to execute immediately'}
Guest Influence Focus: {guest_focus or default_guest_focus}

--- LENNY PODCAST TRANSCRIPT EVIDENCE ---
{grounding_context}
----------------------------------------

ESSAY STRUCTURAL BLUEPRINT:
1. TITLE: Catchy, contrarian headline following Ship 30 headline formulas (e.g., "The [Common Belief] Trap: Why [Outcome] and How to [Solution]").
2. HOOK: 1-2 sentence hook opening with a high-stakes question or contrarian statement.
3. THE 2-YEAR TEST: Address the reader's painful reality 2 years ago.
4. THE 1-3-1 EXPANSION: 3 distinct core pillars/frameworks using 1-3-1 sentence cadence. Each section must cite relevant Lenny transcript sources like [[Guest - Title | Topic]](source_id).
5. SKIMMABLE CADENCE: Bold the single most important concept in each paragraph. Use clean bullet points.
6. THE 3-STEP ACTION CHECKLIST: Conclude with an immediate, executable 3-step action plan.
7. TARGET LENGTH: Comprehensive and detailed, aiming for approximately 1,250 words.

Begin the essay now:"""

        adapter = model_router.get_adapter(provider_override)
        gen_result = await adapter.generate(prompt=user_prompt, system_prompt=self.system_prompt)

        return gen_result.text, citations, gen_result


ship30_skill = Ship30Skill()
