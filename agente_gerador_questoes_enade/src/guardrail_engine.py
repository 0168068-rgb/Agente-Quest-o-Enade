# -*- coding: utf-8 -*-
"""
Motor de Guardrails do Agente.
Combina as validações de profundidade cognitiva de Bloom, checklist de 18 pontos e limpeza da versão do estudante.
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from guardrails.validator_enade import ENADEValidator
from guardrails.bloom_depth_verifier import BloomDepthVerifier

class GuardrailEngine:
    def __init__(self):
        self.validator = ENADEValidator()
        self.bloom_verifier = BloomDepthVerifier()

    def run_all_checks(self, full_markdown_output: str) -> dict:
        # 1. Checar bifurcação
        bifurcation = self.validator.validate_bifurcation(full_markdown_output)
        
        # 2. Checar profundidade de Bloom
        bloom = self.bloom_verifier.verify_question(full_markdown_output)
        
        # 3. Checar 23 campos na ficha
        fields_check = self.validator.validate_23_fields(full_markdown_output)
        
        # 4. Checar se a versão do estudante está limpa
        # Separar a parte I (estudante)
        parts = full_markdown_output.split("PART II")
        student_text = parts[0] if len(parts) > 0 else full_markdown_output
        student_clean = self.validator.validate_student_cleanliness(student_text)
        
        passed_all = (
            bifurcation["valid"] and 
            bloom["approved"] and 
            fields_check["complete"] and 
            student_clean["clean"]
        )
        
        return {
            "passed_all": passed_all,
            "bifurcation": bifurcation,
            "bloom": bloom,
            "fields_check": fields_check,
            "student_clean": student_clean
        }
