# -*- coding: utf-8 -*-
"""
Módulo de Validação de Guardrails ENADE.
Executa a verificação dos 18 pontos do checklist para garantir conformidade total.
"""
import re

class ENADEValidator:
    def __init__(self):
        self.required_fields = [
            "IDENTIFICAÇÃO", "VERSÃO E DATA", "CURSO / COMPONENTE", "PÚBLICO-ALVO", "FINALIDADE",
            "CONTEÚDO CENTRAL", "CONHECIMENTOS E PRÉ-REQUISITOS", "HABILIDADE OBSERVÁVEL",
            "REFERÊNCIA CURRICULAR / MATRIZ", "NÍVEL COGNITIVO PREDOMINANTE", "OPERAÇÕES AUXILIARES",
            "DIFICULDADE ESTIMADA E JUSTIFICATIVA", "TIPO ESTRUTURAL", "RECURSOS DO ENUNCIADO",
            "SITUAÇÃO-PROBLEMA", "DADOS, REGRAS E RESTRIÇÕES", "CAMINHO DE RESOLUÇÃO", "TEMPO ESTIMADO",
            "RESPOSTA ESPERADA", "ERROS QUE ORIGINAM OS DISTRATORES", "RUBRICA, SE DISCURSIVA",
            "FONTES E CONVENÇÕES TÉCNICAS", "VERIFICAÇÕES REALIZADAS"
        ]

    def validate_bifurcation(self, markdown_text: str) -> dict:
        """Verifica se a entrega possui Versão do Estudante e Versão do Professor separadas."""
        has_part1 = "PARTE I" in markdown_text.upper() or "VERSÃO DO ESTUDANTE" in markdown_text.upper()
        has_part2 = "PARTE II" in markdown_text.upper() or "VERSÃO DO PROFESSOR" in markdown_text.upper()
        
        return {
            "valid": has_part1 and has_part2,
            "has_part1_student": has_part1,
            "has_part2_teacher": has_part2
        }

    def validate_student_cleanliness(self, student_text: str) -> dict:
        """Garante que a versão do estudante não vazou gabarito ou respostas."""
        leaks = []
        lowered = student_text.lower()
        
        if "gabarito:" in lowered or "gabarito oficial:" in lowered:
            leaks.append("Vazamento de palavra-chave Gabarito")
        if "resposta correta:" in lowered or "alternativa correta:" in lowered:
            leaks.append("Vazamento de indicação de resposta correta")
        if "justificativa:" in lowered and "alternativa a" in lowered:
            leaks.append("Vazamento de justificativas de alternativas")
            
        return {
            "clean": len(leaks) == 0,
            "leaks_found": leaks
        }

    def validate_23_fields(self, teacher_text: str) -> dict:
        """Verifica o preenchimento de todos os 23 campos da Ficha de Especificação."""
        missing = []
        for field in self.required_fields:
            if field.upper() not in teacher_text.upper():
                missing.append(field)
                
        return {
            "complete": len(missing) == 0,
            "missing_fields": missing,
            "total_present": len(self.required_fields) - len(missing),
            "total_required": len(self.required_fields)
        }
