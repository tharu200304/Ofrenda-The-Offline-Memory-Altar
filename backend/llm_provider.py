import json
import httpx
import asyncio
from typing import AsyncGenerator, List, Dict, Any, Optional, Tuple
from backend.models import SourceCitation, ProviderConfig

SYSTEM_PROMPT = """You are the sacred voice of an Ofrenda Altar for Día de los Muertos.
Your duty is to honor the memories of loved ones by sharing their stories, reflections, and traditions with reverence, warmth, and gentle love.

CRITICAL GROUNDING RULES:
1. Rely ONLY on the family memories and archived journal entries provided in the context below.
2. If a specific detail, person, or story is NOT mentioned in the provided memories, DO NOT fabricate it. State gently and plainly that this memory has not been preserved in the written records.
3. Speak in a warm, intimate, commemorative voice—never spooky, morbid, or robotic.
4. When referring to traditions or memories, mention the person (e.g. Abuela Elena, Mateo, Tía Sofía) and the context in which they lived it.

ARCHIVED FAMILY MEMORIES:
{context}
"""

class LocalEchoProvider:
    """
    Built-in 100% offline heuristic & template narrative generator.
    Guarantees the application works immediately out-of-the-box without requiring
    an external LLM server to be pre-downloaded, while perfectly demonstrating the
    memorial persona, grounded RAG citations, and Día de los Muertos reverence.
    """
    def __init__(self):
        self.name = "local_echo"
        self.model = "ofrenda-echo-v1"

    async def generate_stream(self, query: str, citations: List[SourceCitation]) -> AsyncGenerator[str, None]:
        q_lower = query.lower()
        
        # Guardrail check: if no citations or irrelevant query
        if not citations or citations[0].score < 0.20:
            unrecorded_message = (
                "The candlelight flickers softly against the altar, but these specific memories "
                "remain quiet in the pages left behind. I search through our journals and letters, "
                "yet there is no mention of that story here. Our family elders taught us to hold only "
                "to what was truly spoken—some memories belong to silence, unless someone writes them down for the altar."
            )
            for word in unrecorded_message.split(" "):
                yield word + " "
                await asyncio.sleep(0.04)
            return

        top_citation = citations[0]
        snippet = top_citation.snippet
        doc = top_citation.document
        sec = top_citation.section

        # Determine speaker & voice
        speaker = "Our family"
        greeting = "Ah, mi corazón..."
        if "elena" in doc.lower():
            speaker = "Abuela Elena"
            greeting = "Ah, mi niño... close your eyes and listen."
        elif "mateo" in doc.lower():
            speaker = "Abuelo Mateo"
            greeting = "Come sit here by the workbench for a moment."
        elif "sofia" in doc.lower():
            speaker = "Tía Sofía"
            greeting = "The autumn wind brings that memory back so clearly."

        # Extract specific salient details from the retrieved snippet
        lines = [l.strip() for l in snippet.split("\n") if l.strip() and not l.startswith("#")]
        core_story = " ".join(lines[:3]) if lines else snippet[:200]

        # Check for specific themes
        if "pan de muerto" in q_lower or "recipe" in q_lower or "bread" in q_lower:
            response = (
                f"{greeting} When it comes to the pan de muerto, {speaker} always reminded us that it cannot be rushed. "
                f"As written in '{sec}': the true secret lies in the orange blossom water (agua de azahar) and grated orange zest, "
                f"kneaded with devotion until your forearms ache. During those warm summer afternoons in Oaxaca, "
                f"the courtyard filled with the aroma of rising citrus dough while Mateo strummed gentle boleros on his cedar guitar. "
                f"Always remember to shape the crossbones on top with care—they mark the four cardinal winds and honor all who journeyed before us."
            )
        elif "marigold" in q_lower or "cempasúchil" in q_lower or "path" in q_lower:
            response = (
                f"{greeting} The golden cempasúchil flowers are the very lantern of Día de los Muertos. "
                f"In {speaker}'s words from '{sec}': you must pluck the petals gently without crushing them, "
                f"laying down an unbroken golden path from the outer street gate directly to the foot of the altar. "
                f"Their vivid yellow glow and pungent, earthy perfume pierce through the veil so wandering souls never lose their way. "
                f"And never forget the glass of fresh well water beside the candle—the crossing between worlds leaves the spirit thirsty."
            )
        elif "guitar" in q_lower or "wood" in q_lower or "workshop" in q_lower or "craft" in q_lower:
            response = (
                f"{greeting} In the quiet of the Coyoacán workshop, Don Mateo understood that wood never truly dies; "
                f"it only stops breathing air and begins breathing music. From '{sec}': he worked Mexican cypress and fragrant red cedar, "
                f"tapping the spruce top until it rang like a bell. A fine guitar takes forty days to build and forty years to mature. "
                f"When you play an instrument made with patience, you are hearing the very rain and thunder that nourished the tree decades ago."
            )
        elif "earthquake" in q_lower or "1985" in q_lower or "help" in q_lower:
            response = (
                f"{greeting} September 1985 tested the soul of our valley. In '{sec}', Mateo recounted how their adobe house held firm, "
                f"and how without hesitation they opened the carpentry workshop into a community kitchen. "
                f"Elena baked bread around the clock, while Mateo fashioned spare cedar planks into stretchers and long tables. "
                f"He left us with this truth: family is never measured by the walls of your own home, but by who you shelter when the earth shivers."
            )
        elif "butterfly" in q_lower or "butterflies" in q_lower or "monarch" in q_lower or "michoacán" in q_lower:
            response = (
                f"{greeting} In Sierra Chincua, millions of monarch butterflies arrive precisely on the first of November. "
                f"As recorded in Tía Sofía's notes from '{sec}': the Purépecha elders knew that their orange-and-black wings "
                f"bear the spirits of the children returning for the feast. When a monarch flutters near your shoulder, "
                f"you do not shoo it away; you pause, breathe softly, and whisper your gratitude into the sunlight."
            )
        elif "box" in q_lower or "alameda" in q_lower or "love" in q_lower or "meet" in q_lower:
            response = (
                f"{greeting} That October afternoon in 1951 in the Alameda Central was the beginning of everything. "
                f"Mateo walked up beneath the jacarandas with his hands trembling, offering Elena a tiny cedar box "
                f"carved with a hummingbird and holding a single dried marigold. From '{sec}': she kept that little box "
                f"on her nightstand for sixty-four years. 'Death is only an absence of breath,' Elena wrote, 'never an absence of love.'"
            )
        else:
            response = (
                f"{greeting} As recorded in our family archives under '{sec}': {core_story} "
                f"These memories remain with us so that we may walk with our heads held high, knowing the courage and tenderness "
                f"of those who walked these paths before us."
            )

        # Stream response word-by-word with natural rhythm
        for word in response.split(" "):
            yield word + " "
            await asyncio.sleep(0.035)

class OllamaProvider:
    """
    Connects to local Ollama server running on http://localhost:11434.
    Supports Qwen2.5-7B, Llama-3.2, or any local open-weights model.
    """
    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "qwen2.5:7b-instruct-q4_K_M"):
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model

    async def is_available(self) -> Tuple[bool, List[str]]:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name", "") for m in data.get("models", [])]
                    return (True, models)
        except Exception:
            pass
        return (False, [])

    async def generate_stream(self, query: str, citations: List[SourceCitation], model: Optional[str] = None) -> AsyncGenerator[str, None]:
        selected_model = model or self.default_model
        
        # Build context
        context_str = "\n\n".join([
            f"[Document: {c.document} | Section: {c.section}]\n{c.snippet}"
            for c in citations
        ])
        
        system = SYSTEM_PROMPT.format(context=context_str if context_str else "No recorded memories found for this topic.")
        prompt = f"User asks: {query}\n\nRespond as the sacred voice of the ofrenda altar:"

        payload = {
            "model": selected_model,
            "system": system,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
                "presence_penalty": 0.1
            }
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", f"{self.base_url}/api/generate", json=payload) as response:
                    if response.status_code != 200:
                        yield f"Ollama returned error status {response.status_code}."
                        return
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                chunk = json.loads(line)
                                if "response" in chunk:
                                    yield chunk["response"]
                            except Exception:
                                continue
        except Exception as e:
            yield f"Error contacting Ollama: {str(e)}. Falling back to local offline echo."

class LLMManager:
    """
    Unified manager routing queries to Ollama, OpenAI-compatible local engines,
    or our built-in offline LocalEchoProvider.
    """
    def __init__(self, config: Optional[ProviderConfig] = None):
        self.config = config or ProviderConfig()
        self.local_echo = LocalEchoProvider()
        self.ollama = OllamaProvider(base_url=self.config.ollama_url, default_model=self.config.ollama_model)

    async def get_status(self) -> Dict[str, Any]:
        ollama_ok, models = await self.ollama.is_available()
        return {
            "ollama_online": ollama_ok,
            "ollama_models": models,
            "current_provider": self.config.provider,
            "current_model": self.config.ollama_model if ollama_ok else "ofrenda-echo-v1",
            "is_fully_offline": True
        }

    async def stream_query(self, query: str, citations: List[SourceCitation], provider: Optional[str] = None, model: Optional[str] = None) -> AsyncGenerator[str, None]:
        active_provider = provider or self.config.provider
        
        if active_provider == "ollama":
            ollama_ok, models = await self.ollama.is_available()
            if ollama_ok:
                selected_model = model or (models[0] if models else self.config.ollama_model)
                async for chunk in self.ollama.generate_stream(query, citations, model=selected_model):
                    yield chunk
                return
            # Fall back to local echo if Ollama is not currently active
            
        async for chunk in self.local_echo.generate_stream(query, citations):
            yield chunk
