# -*- coding: utf-8 -*-
import os, json

class MemoryManager:
    def __init__(self, base_dir: str):
        self.short_term_path = os.path.join(base_dir, "memory/short_term/session_store.json")
        self.long_term_path = os.path.join(base_dir, "memory/long_term/enade_knowledge_base.json")
        self.distractors_path = os.path.join(base_dir, "memory/long_term/padroes_distratores_inep.json")
        self.history_path = os.path.join(base_dir, "memory/long_term/banco_questoes_historico.json")

    def load_long_term_memory(self) -> dict:
        if os.path.exists(self.long_term_path):
            with open(self.long_term_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def load_distractors_patterns(self) -> dict:
        if os.path.exists(self.distractors_path):
            with open(self.distractors_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_generated_question(self, question_data: dict):
        history = []
        if os.path.exists(self.history_path):
            with open(self.history_path, "r", encoding="utf-8") as f:
                try:
                    history = json.load(f)
                except Exception:
                    history = []
        history.append(question_data)
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
