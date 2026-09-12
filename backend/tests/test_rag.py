import pytest
from app.rag.loader import load_all_transcripts
from app.rag.chunker import chunk_all_documents
from app.rag.indexer import get_hybrid_index
from app.rag.retriever import retriever, compute_rrf_score
from app.rag.manifest import load_manifest


def test_transcript_loading_and_chunking():
    docs = load_all_transcripts()
    assert len(docs) >= 6, "Expected at least 6 curated Lenny podcast episodes"
    
    shreyas_doc = next((d for d in docs if "Shreyas Doshi" in d.guest), None)
    assert shreyas_doc is not None
    assert len(shreyas_doc.sections) >= 2

    chunks = chunk_all_documents(docs)
    assert len(chunks) >= 12
    assert all(c.source_id for c in chunks)
    assert all(c.guest for c in chunks)
    assert any("High Agency" in c.content for c in chunks)


def test_rrf_mathematical_calculation():
    """
    Verify RRF mathematical calculation:
    RRF(d) = sum(1 / (k + rank_m(d)))
    For k=60, BM25 rank=1, Dense rank=3:
    RRF = 1/61 + 1/63 ≈ 0.01639344 + 0.01587302 ≈ 0.03226646
    """
    k = 60
    bm25_rank = 1
    dense_rank = 3
    expected_score = (1.0 / (60 + 1)) + (1.0 / (60 + 3))

    calculated_score = compute_rrf_score(bm25_rank, dense_rank, k=k)
    assert pytest.approx(calculated_score, rel=1e-5) == expected_score
    assert pytest.approx(calculated_score, rel=1e-4) == 0.032266


def test_hybrid_retrieval_and_citations():
    # 1. Test Shreyas Doshi High Agency query
    results, latency_ms = retriever.retrieve("high agency product manager", top_k=3)
    assert len(results) > 0
    assert latency_ms < 500  # Latency under 500ms
    assert any("Shreyas Doshi" in r.chunk.guest for r in results)

    # Citations extraction
    citations = retriever.extract_citations(results)
    assert len(citations) > 0
    assert citations[0].source_id.startswith("src_")
    assert citations[0].guest != ""

    # 2. Test Elena Verna PLG query
    plg_results, _ = retriever.retrieve("Product-Led Growth viral loops B2B", top_k=3)
    assert len(plg_results) > 0
    assert any("Elena Verna" in r.chunk.guest for r in plg_results)


def test_manifest_metadata_and_provenance():
    manifest = load_manifest()
    assert len(manifest) >= 6
    for item in manifest:
        assert "source_id" in item
        assert "episode_id" in item
        assert "guest" in item
        assert "source_hash" in item
        assert "transcript_version" in item
