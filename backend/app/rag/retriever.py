import time
from dataclasses import dataclass
from typing import Optional
from app.config import settings
from app.rag.indexer import get_hybrid_index, TranscriptChunk
from app.schemas.schemas import Citation
from app.observability.logging import logger


@dataclass
class RetrievalResult:
    chunk: TranscriptChunk
    rrf_score: float
    bm25_rank: Optional[int]
    dense_rank: Optional[int]


def compute_rrf_score(bm25_rank: Optional[int], dense_rank: Optional[int], k: int = 60) -> float:
    """
    Standard Reciprocal Rank Fusion (RRF):
    RRF(d) = sum(1 / (k + rank_m(d)))
    """
    score = 0.0
    if bm25_rank is not None:
        score += 1.0 / (k + bm25_rank)
    if dense_rank is not None:
        score += 1.0 / (k + dense_rank)
    return score


class HybridRetriever:
    def __init__(self, k: int = 60):
        self.k = k

    def retrieve(self, query: str, top_k: int = 5) -> tuple[list[RetrievalResult], float]:
        start_time = time.time()
        index = get_hybrid_index()

        if not index.chunks:
            return [], (time.time() - start_time) * 1000.0

        # Retrieve top candidates from both systems
        bm25_results = index.search_bm25(query, top_k=top_k * 3)
        dense_results = index.search_dense(query, top_k=top_k * 3)

        # Track ranks (1-indexed)
        bm25_ranks: dict[int, int] = {idx: rank + 1 for rank, (idx, _) in enumerate(bm25_results)}
        dense_ranks: dict[int, int] = {idx: rank + 1 for rank, (idx, _) in enumerate(dense_results)}

        all_candidate_indices = set(bm25_ranks.keys()).union(set(dense_ranks.keys()))
        if not all_candidate_indices:
            latency_ms = (time.time() - start_time) * 1000.0
            return [], latency_ms

        scored_candidates: list[RetrievalResult] = []
        for idx in all_candidate_indices:
            b_rank = bm25_ranks.get(idx)
            d_rank = dense_ranks.get(idx)
            rrf = compute_rrf_score(b_rank, d_rank, k=self.k)
            scored_candidates.append(
                RetrievalResult(
                    chunk=index.chunks[idx],
                    rrf_score=rrf,
                    bm25_rank=b_rank,
                    dense_rank=d_rank,
                )
            )

        # Sort by RRF score descending
        scored_candidates.sort(key=lambda x: x.rrf_score, reverse=True)
        final_results = scored_candidates[:top_k]

        latency_ms = (time.time() - start_time) * 1000.0
        logger.info(f"Retrieved {len(final_results)} chunks for query '{query[:40]}...' in {latency_ms:.2f}ms")
        return final_results, latency_ms

    def format_grounding_context(self, results: list[RetrievalResult]) -> str:
        if not results:
            return "No relevant Lenny Podcast transcript chunks found."

        context_blocks = []
        for idx, res in enumerate(results, 1):
            c = res.chunk
            header = (
                f"--- SOURCE CHUNK [{idx}] ---\n"
                f"Source ID: {c.source_id}\n"
                f"Reference: {c.source_reference}\n"
                f"Episode: {c.episode_title} (ID: {c.episode_id})\n"
                f"Guest: {c.guest}\n"
                f"Topic: {c.topic}\n"
                f"Timestamp: {c.timestamp_str or 'N/A'}\n"
                f"Content:\n{c.content}\n"
            )
            context_blocks.append(header)

        return "\n".join(context_blocks)

    def extract_citations(self, results: list[RetrievalResult]) -> list[Citation]:
        citations = []
        seen_source_ids = set()
        for res in results:
            c = res.chunk
            if c.source_id not in seen_source_ids:
                seen_source_ids.add(c.source_id)
                citations.append(
                    Citation(
                        source_id=c.source_id,
                        source_reference=c.source_reference,
                        episode_id=c.episode_id,
                        episode_title=c.episode_title,
                        guest=c.guest,
                        topic=c.topic,
                        timestamp_str=c.timestamp_str,
                        snippet=c.content[:200] + "..." if len(c.content) > 200 else c.content
                    )
                )
        return citations


retriever = HybridRetriever(k=settings.RRF_K)
