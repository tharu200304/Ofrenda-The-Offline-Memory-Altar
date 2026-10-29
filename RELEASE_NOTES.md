# Release v1.0.0 — Ghost in the Machine Hackathon Edition

**Tag:** `v1.0.0`  
**Repository:** [https://github.com/tharu200304/Ofrenda-The-Offline-Memory-Altar](https://github.com/tharu200304/Ofrenda-The-Offline-Memory-Altar)  

---

## 🕯️ Overview

**Ofrenda: The Offline Memory Altar** is a local-first conversational remembrance companion for **Día de los Muertos**, created for the **Ghost in the Machine** Hackathon Challenge. It transforms private family letters, recipes, and recorded memoirs into an interactive oral history altar powered by open-source AI.

---

## ✨ Key Features in v1.0.0

- **100% Local & Air-Gapped:** Zero external network calls. All personal archives and vector embeddings live strictly on local disk.
- **Open-Weight Model Ready:** Configured for `Qwen2.5-7B-Instruct-Q4_K_M` via local **Ollama** (`http://localhost:11434`).
- **Immediate Out-of-the-Box Fallback:** Includes a built-in `LocalEchoProvider` ensuring the system works instantly without waiting to download multi-gigabyte models.
- **Offline Subword Semantic Embeddings:** Custom 384-dimensional dense feature projection vectorizer running locally inside **ChromaDB** with zero HuggingFace or AWS dependencies.
- **Factual Grounding & Hallucination Guardrails:** Validates model answers against archival sources and displays confidence scores and citations.
- **Atmospheric Altar Frontend:**
  - Dynamic SVG candle stand with interactive flame toggle that alters the page's ambient illumination.
  - Lightweight canvas simulation with floating cempasúchil marigold petals.
  - Slide-over Memory Archives drawer for inspecting and uploading new family documents.
  - One-click session keepsake exporter (Markdown).
- **Curated Starter Archives:** Pre-packaged authentic memoirs for **Abuela Elena**, **Abuelo Mateo**, and **Tía Sofía**.
- **Automated Test Suite:** 100% passing test coverage (`pytest tests/test_rag.py`).
- **Challenge Post:** Full "Why Open Innovation Matters" essay included.

---

## 📦 Quickstart

```bash
git clone https://github.com/tharu200304/Ofrenda-The-Offline-Memory-Altar.git
cd Ofrenda-The-Offline-Memory-Altar
pip install -r requirements.txt
python run.py
```

Then visit [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.
