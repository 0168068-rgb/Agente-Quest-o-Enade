# -*- coding: utf-8 -*-
import re

class BloomDepthVerifier:
    def __init__(self):
        self.blocked_level1_patterns = [
            r"o que significa a sigla",
            r"assinale o significado da palavra",
            r"qual e a definicao exata de",
            r"quem foi o criador de",
            r"em que ano foi lancado"
        ]

    def verify_question(self, question_text: str) -> dict:
        text_lowered = question_text.lower()
        for pattern in self.blocked_level1_patterns:
            if re.search(pattern, text_lowered):
                return {
                    "approved": False,
                    "level": 1,
                    "reason": "Questao identificada como Nivel 1 (Memorizacao). O ENADE exige Nivel 2, 3 ou 4."
                }
        return {
            "approved": True,
            "level": "2, 3 ou 4",
            "reason": "Questao atende aos requisitos de profundidade cognitiva do ENADE."
        }
