import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from core.models import SessionData


class SessionStorage:
    
    def __init__(self, storage_dir: str = ".session_memory"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.messages_dir = self.storage_dir / "messages"
        self.metadata_dir = self.storage_dir / "metadata"
        
        self.messages_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_message_file(self, session_id: str) -> Path:
        return self.messages_dir / f"{session_id}.jsonl"
    
    def _get_metadata_file(self, session_id: str) -> Path:
        return self.metadata_dir / f"{session_id}.json"
    
    def append_messages(self, session_id: str, messages: List[Dict[str, str]]):
        message_file = self._get_message_file(session_id)
        with open(message_file, "a", encoding="utf-8") as f:
            for msg in messages:
                f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    
    def read_all_messages(self, session_id: str) -> List[Dict[str, str]]:
        message_file = self._get_message_file(session_id)
        if not message_file.exists():
            return []
        
        messages = []
        with open(message_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    messages.append(json.loads(line))
        return messages
    
    def save_metadata(self, session_id: str, data: SessionData):
        metadata_file = self._get_metadata_file(session_id)
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(data.model_dump(), f, ensure_ascii=False, indent=2)
    
    def load_metadata(self, session_id: str) -> Optional[SessionData]:
        metadata_file = self._get_metadata_file(session_id)
        if not metadata_file.exists():
            return None
        
        with open(metadata_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return SessionData(**data)
    
    def session_exists(self, session_id: str) -> bool:
        return self._get_metadata_file(session_id).exists()
    
    def list_sessions(self) -> List[str]:
        return [f.stem for f in self.metadata_dir.glob("*.json")]
