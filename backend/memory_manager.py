import os
import glob
import time
from typing import List, Dict, Any, Optional
from backend.models import MemoryItem

class MemoryManager:
    def __init__(self, memories_dir: str = "./memories"):
        self.memories_dir = memories_dir
        os.makedirs(self.memories_dir, exist_ok=True)

    def list_memories(self) -> List[MemoryItem]:
        items: List[MemoryItem] = []
        files = glob.glob(os.path.join(self.memories_dir, "*.txt")) + glob.glob(os.path.join(self.memories_dir, "*.md"))
        
        for fpath in files:
            fname = os.path.basename(fpath)
            stat = os.stat(fpath)
            updated = time.strftime("%Y-%m-%d %H:%M", time.localtime(stat.st_mtime))
            
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
                
            lines = [l.strip() for l in content.split("\n") if l.strip()]
            title = lines[0].lstrip("#").strip() if lines else fname
            preview = " ".join(lines[1:4]) if len(lines) > 1 else content[:150]
            
            # Count sections
            chunks = [l for l in lines if l.startswith("### ") or l.startswith("## ")]
            chunk_count = max(1, len(chunks))
            
            items.append(MemoryItem(
                id=fname,
                filename=fname,
                title=title,
                preview=preview[:200] + ("..." if len(preview) > 200 else ""),
                chunk_count=chunk_count,
                char_count=len(content),
                updated_at=updated
            ))
            
        return sorted(items, key=lambda x: x.filename)

    def get_memory_content(self, filename: str) -> Optional[str]:
        # Sanitize filename
        safe_name = os.path.basename(filename)
        path = os.path.join(self.memories_dir, safe_name)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    def save_memory(self, filename: str, content: str) -> str:
        safe_name = os.path.basename(filename)
        if not safe_name.endswith(".txt") and not safe_name.endswith(".md"):
            safe_name += ".txt"
            
        path = os.path.join(self.memories_dir, safe_name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return safe_name

    def delete_memory(self, filename: str) -> bool:
        safe_name = os.path.basename(filename)
        path = os.path.join(self.memories_dir, safe_name)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False
