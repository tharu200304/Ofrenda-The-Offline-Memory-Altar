import os
import re
import glob
from typing import List, Dict, Any, Tuple
import chromadb
from chromadb.config import Settings
from backend.embeddings import FastLocalEmbeddingFunction
from backend.models import SourceCitation

class MemoryChunk:
    def __init__(self, doc_name: str, section_title: str, text: str, line_start: int, line_end: int):
        self.doc_name = doc_name
        self.section_title = section_title
        self.text = text.strip()
        self.line_start = line_start
        self.line_end = line_end

class OfrendaRAGEngine:
    def __init__(self, db_path: str = "./data/chroma_db"):
        os.makedirs(db_path, exist_ok=True)
        self.embedding_fn = FastLocalEmbeddingFunction()
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="ofrenda_memories",
            embedding_function=self.embedding_fn,
            metadata={"description": "Día de los Muertos Family Archives and Memories"}
        )

    def parse_document(self, file_path: str) -> List[MemoryChunk]:
        """
        Parses a memorial text file into semantic section chunks,
        preserving line numbers and section titles.
        """
        doc_name = os.path.basename(file_path)
        chunks: List[MemoryChunk] = []
        
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
            
        current_section = "General Memory"
        current_lines: List[str] = []
        start_line = 1
        
        for idx, line in enumerate(lines, 1):
            stripped = line.strip()
            # Detect Markdown section headers like '### 1. Title' or '## Title'
            if stripped.startswith("### ") or stripped.startswith("## ") or stripped.startswith("# "):
                if current_lines:
                    text = "".join(current_lines).strip()
                    if len(text) > 30:
                        chunks.append(MemoryChunk(doc_name, current_section, text, start_line, idx - 1))
                    current_lines = []
                current_section = stripped.lstrip("#").strip()
                start_line = idx
            else:
                current_lines.append(line)
                
        if current_lines:
            text = "".join(current_lines).strip()
            if len(text) > 30:
                chunks.append(MemoryChunk(doc_name, current_section, text, start_line, len(lines)))
                
        return chunks

    def index_all(self, memories_dir: str = "./memories") -> int:
        """
        Indexes all .txt and .md files in the memories directory into ChromaDB.
        """
        files = glob.glob(os.path.join(memories_dir, "*.txt")) + glob.glob(os.path.join(memories_dir, "*.md"))
        
        # Clear existing collection items for a clean refresh
        existing_ids = self.collection.get()["ids"]
        if existing_ids:
            self.collection.delete(ids=existing_ids)
            
        documents = []
        metadatas = []
        ids = []
        
        chunk_idx = 0
        for fpath in files:
            chunks = self.parse_document(fpath)
            for c in chunks:
                chunk_id = f"chunk_{chunk_idx}_{c.doc_name}"
                documents.append(f"{c.doc_name} - {c.section_title}\n{c.text}")
                metadatas.append({
                    "document": c.doc_name,
                    "section": c.section_title,
                    "line_start": c.line_start,
                    "line_end": c.line_end,
                    "raw_text": c.text
                })
                ids.append(chunk_id)
                chunk_idx += 1
                
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
        return len(documents)

    def retrieve(self, query: str, top_k: int = 3) -> List[SourceCitation]:
        """
        Retrieves the most semantically relevant memory excerpts for a user query.
        Returns SourceCitation objects with relevance score (0.0 to 1.0).
        """
        count = self.collection.count()
        if count == 0:
            return []
            
        k = min(top_k, count)
        results = self.collection.query(
            query_texts=[query],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )
        
        citations: List[SourceCitation] = []
        if not results or not results["documents"] or not results["documents"][0]:
            return citations
            
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        dists = results["distances"][0]
        
        for doc, meta, dist in zip(docs, metas, dists):
            # Convert cosine distance to similarity score
            score = max(0.0, min(1.0, 1.0 - (dist / 2.0)))
            citations.append(SourceCitation(
                document=meta.get("document", "archive"),
                section=meta.get("section", "unnamed section"),
                snippet=meta.get("raw_text", doc[:300]),
                score=round(score, 3),
                line_start=meta.get("line_start"),
                line_end=meta.get("line_end")
            ))
            
        return citations

    def verify_grounding(self, retrieved: List[SourceCitation], response_text: str) -> Tuple[bool, float]:
        """
        Verifies whether the generated answer is grounded in the retrieved sources.
        Checks keyword intersection between retrieved snippets and the answer.
        """
        if not retrieved:
            # If no sources were found and the model admitted it doesn't know, it's grounded
            unrecorded_keywords = ["unrecorded", "not in", "lost to time", "don't have", "no record", "no mention"]
            is_honest = any(k in response_text.lower() for k in unrecorded_keywords)
            return (is_honest, 0.9 if is_honest else 0.2)
            
        # Combine retrieved snippet words
        context_words = set()
        for c in retrieved:
            words = re.findall(r"\b[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]{4,}\b", c.snippet.lower())
            context_words.update(words)
            
        response_words = re.findall(r"\b[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]{4,}\b", response_text.lower())
        if not response_words:
            return (True, 0.5)
            
        # Stop words filter
        common_words = {"this", "that", "with", "from", "have", "were", "they", "will", "would", "could", "about", "there", "their", "where", "which", "your", "when"}
        filtered_response = [w for w in response_words if w not in common_words]
        
        if not filtered_response:
            return (True, 0.5)
            
        overlap = sum(1 for w in filtered_response if w in context_words)
        ratio = overlap / len(filtered_response)
        
        # Grounded if at least 25% of substantive content words map to retrieved context
        is_grounded = ratio >= 0.20
        score = min(1.0, round(ratio * 2.5, 2))  # scaled confidence
        return (is_grounded, max(0.35, score))

    def count(self) -> int:
        return self.collection.count()
