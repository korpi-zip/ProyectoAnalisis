import json
import os
import hashlib
from typing import Dict, Optional

class KnowledgeBase:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data: Dict[str, Dict[str, str]] = {}
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except json.JSONDecodeError:
                self.data = {}
        else:
            self.data = {}

    def save(self):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4)

    def get_complexity(self, signature: str) -> Optional[Dict[str, str]]:
        return self.data.get(signature)

    def add_complexity(self, signature: str, complexity: Dict[str, str]):
        self.data[signature] = complexity
        self.save()

    @staticmethod
    def compute_signature(node_dict: Dict) -> str:
        """
        Computes a deterministic hash of the node structure.
        We serialize the dict to a sorted JSON string and hash it.
        """
        # We need to be careful about what we include in the signature.
        # Variable names might matter for dependency analysis, but for generic structure
        # we might want to abstract them. For now, let's hash the exact structure.
        serialized = json.dumps(node_dict, sort_keys=True)
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()
