import os
import json
import asyncio
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from backend.models import QueryRequest, QueryResponse, MemoryUploadRequest, ProviderConfig, SystemStatus
from backend.rag_engine import OfrendaRAGEngine
from backend.llm_provider import LLMManager
from backend.memory_manager import MemoryManager

from contextlib import asynccontextmanager

# Core singletons
rag_engine = OfrendaRAGEngine(db_path="./data/chroma_db")
memory_manager = MemoryManager(memories_dir="./memories")
llm_manager = LLMManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    indexed = rag_engine.index_all("./memories")
    print(f"[Ofrenda] Startup: Indexed {indexed} memory chunks into ChromaDB.")
    yield

app = FastAPI(
    title="Ofrenda: The Offline Memory Altar",
    description="Local-first conversational memory altar for Día de los Muertos powered by open-source AI",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/status")
async def get_status():
    status = await llm_manager.get_status()
    total_memories = len(memory_manager.list_memories())
    total_chunks = rag_engine.count()
    
    return {
        **status,
        "total_memories": total_memories,
        "total_chunks": total_chunks,
        "device_info": "Local Hardware (NVIDIA RTX / CPU)"
    }

@app.post("/api/query")
async def query_altar(req: QueryRequest):
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    # 1. Retrieve top relevant memory citations from local ChromaDB
    citations = rag_engine.retrieve(query, top_k=3)
    
    # 2. If client requests SSE streaming
    if req.stream:
        async def event_generator():
            full_response = []
            # First send citations event
            init_payload = {
                "type": "citations",
                "citations": [c.model_dump() for c in citations]
            }
            yield f"data: {json.dumps(init_payload)}\n\n"
            
            # Stream text chunks from local provider
            async for token in llm_manager.stream_query(query, citations, provider=req.provider, model=req.model):
                full_response.append(token)
                yield f"data: {json.dumps({'type': 'token', 'text': token})}\n\n"
                
            complete_text = "".join(full_response)
            is_grounded, grounding_score = rag_engine.verify_grounding(citations, complete_text)
            
            final_payload = {
                "type": "done",
                "is_grounded": is_grounded,
                "grounding_score": grounding_score,
                "provider": req.provider or llm_manager.config.provider,
                "model": req.model or llm_manager.config.ollama_model
            }
            yield f"data: {json.dumps(final_payload)}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    
    # Non-streaming fallback
    full_text_chunks = []
    async for token in llm_manager.stream_query(query, citations, provider=req.provider, model=req.model):
        full_text_chunks.append(token)
    answer = "".join(full_text_chunks)
    is_grounded, score = rag_engine.verify_grounding(citations, answer)
    
    return QueryResponse(
        answer=answer,
        sources=citations,
        grounding_score=score,
        provider_used=req.provider or llm_manager.config.provider,
        model_used=req.model or llm_manager.config.ollama_model,
        is_grounded=is_grounded
    )

@app.get("/api/memories")
async def list_memories():
    return memory_manager.list_memories()

@app.get("/api/memories/{filename}")
async def get_memory_file(filename: str):
    content = memory_manager.get_memory_content(filename)
    if content is None:
        raise HTTPException(status_code=404, detail="Memory file not found.")
    return {"filename": filename, "content": content}

@app.post("/api/memories/upload")
async def upload_memory(req: MemoryUploadRequest):
    saved_name = memory_manager.save_memory(req.filename, req.content)
    # Re-index
    total = rag_engine.index_all("./memories")
    return {"message": "Memory archived and indexed successfully.", "filename": saved_name, "total_chunks": total}

@app.delete("/api/memories/{filename}")
async def delete_memory_file(filename: str):
    deleted = memory_manager.delete_memory(filename)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory file not found.")
    rag_engine.index_all("./memories")
    return {"message": f"Memory {filename} deleted and index refreshed."}

@app.post("/api/settings")
async def update_settings(cfg: ProviderConfig):
    llm_manager.config = cfg
    llm_manager.ollama = llm_manager.ollama.__class__(base_url=cfg.ollama_url, default_model=cfg.ollama_model)
    return {"message": "Settings updated successfully.", "active_provider": cfg.provider}

@app.post("/api/reindex")
async def reindex_memories():
    count = rag_engine.index_all("./memories")
    return {"message": f"Successfully reindexed {count} memory chunks."}

@app.get("/api/challenge-post")
async def get_challenge_post():
    post_path = "./CHALLENGE_POST.md"
    if os.path.exists(post_path):
        with open(post_path, "r", encoding="utf-8") as f:
            return {"content": f.read()}
    return {"content": "# Challenge post not yet created."}

# Mount static frontend
frontend_dir = os.path.abspath("./frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
