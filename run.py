#!/usr/bin/env python3
"""
OFRENDA: The Offline Memory Altar
Quick Launcher Script
"""

import os
import sys
import time
import webbrowser
import uvicorn

# Configure UTF-8 output encoding for Windows terminal compatibility
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def main():
    print("=" * 70)
    print("  🕯️  OFRENDA: The Offline Memory Altar  (Día de los Muertos)")
    print("  💀  Local-First AI Companion Built on Open-Source Foundations")
    print("=" * 70)
    
    # 1. Environment check
    print("\n[1/3] Checking environment & local folders...")
    os.makedirs("./memories", exist_ok=True)
    os.makedirs("./data/chroma_db", exist_ok=True)
    
    # Check memories count
    txt_files = [f for f in os.listdir("./memories") if f.endswith(".txt") or f.endswith(".md")]
    print(f"      Found {len(txt_files)} archived family documents in ./memories/")

    # 2. Local vector database check
    print("\n[2/3] Initializing local ChromaDB vector index...")
    try:
        from backend.rag_engine import OfrendaRAGEngine
        engine = OfrendaRAGEngine()
        count = engine.index_all("./memories")
        print(f"      Successfully indexed {count} semantic memory chunks.")
    except Exception as e:
        print(f"      Notice during index: {e}")

    # 3. Launching web server
    host = "127.0.0.1"
    port = 8000
    url = f"http://{host}:{port}"
    print(f"\n[3/3] Starting Ofrenda Memorial Server at: {url}")
    print("      * 100% On-Device & Air-Gapped")
    print("      * Open weights ready (Ollama / Qwen2.5-7B or built-in Local Echo)")
    print("      * Press Ctrl+C in this terminal to blow out the vigil and stop.\n")

    # Open browser automatically after a short delay
    def open_browser():
        time.sleep(1.2)
        print(f"      Opening {url} in your default browser...")
        webbrowser.open(url)

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Run Uvicorn server
    uvicorn.run("backend.app:app", host=host, port=port, log_level="info")

if __name__ == "__main__":
    main()
