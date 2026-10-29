from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SourceCitation(BaseModel):
    document: str
    section: str
    snippet: str
    score: float
    line_start: Optional[int] = None
    line_end: Optional[int] = None

class QueryRequest(BaseModel):
    query: str
    stream: bool = True
    provider: Optional[str] = None  # "ollama", "openai_compatible", "local_echo"
    model: Optional[str] = None
    temperature: float = 0.3
    candle_lit: bool = True

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceCitation]
    grounding_score: float  # 0.0 to 1.0 (anchoring confidence)
    provider_used: str
    model_used: str
    is_grounded: bool

class MemoryItem(BaseModel):
    id: str
    filename: str
    title: str
    preview: str
    chunk_count: int
    char_count: int
    updated_at: str

class MemoryUploadRequest(BaseModel):
    filename: str
    content: str

class ProviderConfig(BaseModel):
    provider: str = "ollama"  # "ollama", "openai_compatible", "local_echo"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b-instruct-q4_K_M"
    openai_compatible_url: str = "http://localhost:1234/v1"
    openai_compatible_model: str = "local-model"
    openai_api_key: str = "local"

class SystemStatus(BaseModel):
    active_provider: str
    active_model: str
    ollama_online: bool
    ollama_models: List[str]
    openai_compatible_online: bool
    total_memories: int
    total_chunks: int
    is_fully_offline: bool
    device_info: str
