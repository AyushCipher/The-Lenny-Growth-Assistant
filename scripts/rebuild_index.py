import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.rag.indexer import get_hybrid_index


def main():
    print("Forcing full rebuild of Lenny's Podcast hybrid index...")
    index = get_hybrid_index()
    index.build_index()
    print(f"Index built successfully! Total chunks: {len(index.chunks)}")


if __name__ == "__main__":
    main()
