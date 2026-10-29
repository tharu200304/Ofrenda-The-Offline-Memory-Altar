import pytest
import os
from fastapi.testclient import TestClient
from backend.rag_engine import OfrendaRAGEngine
from backend.app import app

client = TestClient(app)

def test_status_endpoint():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "is_fully_offline" in data
    assert data["is_fully_offline"] is True
    assert "total_memories" in data
    assert data["total_memories"] >= 3

def test_memories_endpoint():
    response = client.get("/api/memories")
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 3
    filenames = [item["filename"] for item in items]
    assert "abuela_elena.txt" in filenames
    assert "abuelo_mateo.txt" in filenames
    assert "tia_sofia.txt" in filenames

def test_rag_retrieval_accuracy():
    rag = OfrendaRAGEngine(db_path="./data/chroma_db")
    # Test pan de muerto recipe query
    results = rag.retrieve("How to make pan de muerto dough with orange blossom water", top_k=2)
    assert len(results) > 0
    assert "abuela_elena.txt" in results[0].document
    assert "Pan de Muerto" in results[0].section

def test_query_endpoint_non_streaming():
    payload = {
        "query": "Abuela Elena, tell me about your pan de muerto recipe.",
        "stream": False,
        "provider": "local_echo"
    }
    response = client.post("/api/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "orange blossom" in data["answer"].lower()
    assert len(data["sources"]) > 0
    assert data["is_grounded"] is True

def test_guardrail_unrecorded_memory():
    payload = {
        "query": "Did Uncle Carlos ever build a red sports car?",
        "stream": False,
        "provider": "local_echo"
    }
    response = client.post("/api/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Should politely acknowledge the lack of record
    assert any(w in data["answer"].lower() for w in ["quiet", "no mention", "silence", "unrecorded"])

def test_challenge_post_endpoint():
    response = client.get("/api/challenge-post")
    assert response.status_code == 200
    data = response.json()
    assert "Ghost in the Machine" in data["content"]
    assert "Why Our Ancestors Belong on Open Weights" in data["content"]

if __name__ == "__main__":
    import pytest
    pytest.main(["-v", __file__])
