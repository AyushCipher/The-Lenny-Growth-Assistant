import re
from typing import Optional
import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.rag.loader import load_all_transcripts
from app.rag.chunker import chunk_all_documents, TranscriptChunk
from app.observability.logging import logger


def tokenize_text(text: str) -> list[str]:
    # Lowercase and extract alphanumeric tokens
    return re.findall(r"\b\w+\b", text.lower())


class HybridSearchIndex:
    def __init__(self):
        self.chunks: list[TranscriptChunk] = []
        self.bm25: Optional[BM25Okapi] = None
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.dense_matrix: Optional[np.ndarray] = None
        self.version: str = "1.0.0"

    def build_index(self):
        docs = load_all_transcripts()
        self.chunks = chunk_all_documents(docs)

        if not self.chunks:
            logger.warning("No transcript chunks found to index")
            return

        corpus_texts = [chunk.full_searchable_text for chunk in self.chunks]
        tokenized_corpus = [tokenize_text(text) for text in corpus_texts]

        # 1. Build BM25 sparse index
        self.bm25 = BM25Okapi(tokenized_corpus)

        # 2. Build Dense semantic TF-IDF feature matrix with sublinear tf scaling and character n-grams
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            token_pattern=r"(?u)\b\w+\b",
            stop_words="english"
        )
        self.dense_matrix = self.vectorizer.fit_transform(corpus_texts)

        logger.info(f"Hybrid index successfully built with {len(self.chunks)} chunks across {len(docs)} episodes")

    def search_bm25(self, query: str, top_k: int = 10) -> list[tuple[int, float]]:
        if not self.bm25 or not self.chunks:
            return []
        query_tokens = tokenize_text(query)
        if not query_tokens:
            return []
        scores = self.bm25.get_scores(query_tokens)
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [(int(idx), float(scores[idx])) for idx in top_indices if scores[idx] > 0]

    def search_dense(self, query: str, top_k: int = 10) -> list[tuple[int, float]]:
        if not self.vectorizer or self.dense_matrix is None or not self.chunks:
            return []
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.dense_matrix)[0]
        top_indices = np.argsort(similarities)[::-1][:top_k]
        return [(int(idx), float(similarities[idx])) for idx in top_indices if similarities[idx] > 0]


# Global singleton hybrid index instance
hybrid_index = HybridSearchIndex()


def get_hybrid_index() -> HybridSearchIndex:
    global hybrid_index
    if not hybrid_index.chunks:
        hybrid_index.build_index()
    return hybrid_index
