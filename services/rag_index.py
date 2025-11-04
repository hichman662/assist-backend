# app/services/rag_index.py
import os
import glob
from typing import List
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Name of the embedding model (multilingual)
EMBED_MODEL_NAME = "sentence-transformers/distiluse-base-multilingual-cased-v2"

# Where to store the vector DB
PERSIST_DIR = os.getenv("RAG_STORE_DIR", "./rag_store")

# Collection name (must be 3–512 characters, alphanumeric start/end)
COLLECTION_NAME = "mosiot_kb"

class RagIndex:
    def __init__(self, persist_dir: str = PERSIST_DIR):
        os.makedirs(persist_dir, exist_ok=True)
        self.persist_dir = persist_dir

        # Create a persistent ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )

        # Create or get existing collection
        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)

        # Load embedding model
        print(f"Loading embedding model: {EMBED_MODEL_NAME}")
        self.embedder = SentenceTransformer(EMBED_MODEL_NAME)

    def _embed(self, texts: List[str]) -> List[List[float]]:
        """Convert text into vector embeddings"""
        return self.embedder.encode(texts, normalize_embeddings=True).tolist()

    def rebuild_from_folder(self, folder: str = "./knowledge_base"):
        """Read all Markdown files and rebuild the index"""
        files = sorted(glob.glob(os.path.join(folder, "*.md")))
        docs, ids, metas = [], [], []

        for i, f in enumerate(files):
            with open(f, "r", encoding="utf-8") as fh:
                txt = fh.read().strip()
            if not txt:
                continue
            docs.append(txt)
            ids.append(f"doc_{i}")
            metas.append({"path": os.path.basename(f)})

        if not docs:
            print(f" No documents found in {folder}")
            return

        # Delete old collection (if exists) and rebuild
        try:
            self.client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass

        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)
        embeddings = self._embed(docs)
        self.collection.add(
            documents=docs, embeddings=embeddings, ids=ids, metadatas=metas
        )
        print(f" Indexed {len(docs)} documents into {self.persist_dir}")

    def query(self, text: str, k: int = 3):
        """Find most similar pieces of text in the KB"""
        emb = self._embed([text])[0]
        res = self.collection.query(query_embeddings=[emb], n_results=k)
        results = []
        for doc, meta in zip(
            res.get("documents", [[]])[0], res.get("metadatas", [[]])[0]
        ):
            results.append({"text": doc.strip(), "meta": meta})
        return results


# Global instance for use in the app
rag_index = RagIndex()
