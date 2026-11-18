#!/usr/bin/env python3
"""
Regras de Validação e Guardrails para o SmartDuck
Verifica regras de integridade de notas, RAs, nomes e divergências entre AVA e SophiA.
"""

from typing import Dict, List, Any, Optional
import re

class SmartDuckGuardrails:
    CAMPOS_VALIDOS = {"AD", "AI", "PS"}
    NOTA_MINIMA = 0.0
    NOTA_MAXIMA = 10.0

    @classmethod
    def validar_nota(cls, valor: Any) -> Optional[float]:
        """Valida se o valor de uma nota está no intervalo permitido [0.0, 10.0] ou é falta/vazio."""
        if valor is None or valor == "" or str(valor).strip() == "-":
            return None
        
        texto = str(valor).strip().upper()
        if texto in {"F", "FALTA"}:
            return 0.0
        
        texto = texto.replace(",", ".")
        try:
            nota = float(texto)
            if cls.NOTA_MINIMA <= nota <= cls.NOTA_MAXIMA:
                return round(nota, 2)
            raise ValueError(f"Nota fora da faixa permitida [0.0, 10.0]: {nota}")
        except ValueError:
            raise ValueError(f"Formato de nota inválido: '{valor}'")

    @classmethod
    def validar_ra(cls, ra: Any) -> str:
        """Sanitiza e valida RA de aluno."""
        if not ra:
            raise ValueError("RA não pode ser vazio.")
        ra_str = str(ra).strip()
        # Remove caracteres indesejados mas mantém identificadores numéricos ou alfanuméricos padrão
        ra_limpo = re.sub(r'[^0-9A-Za-z]', '', ra_str)
        if not ra_limpo:
            raise ValueError(f"RA inválido após higienização: '{ra}'")
        return ra_limpo

    @classmethod
    def verificar_sobreposicao(cls, nota_existente: Any, nova_nota: Any, permitir_sobrescrita: bool = False) -> bool:
        """
        Retorna True se for seguro lançar a nova nota.
        Regra pétrea: se o campo já possui valor, não sobrescrever a menos que permitido.
        """
        if nota_existente is None or str(nota_existente).strip() in {"", "-"}:
            return True
        if not permitir_sobrescrita:
            return False
        return True

    @classmethod
    def conciliar_aluno(cls, aluno_ava: Dict[str, Any], lista_sophia: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Concilia aluno do AVA com a lista de matriculados do SophiA.
        Retorna status: 'MATCH_EXATO', 'HOMONIMO_DIVERGENTE', 'SOMENTE_NO_AVA'.
        """
        ra_ava = aluno_ava.get("ra")
        nome_ava = aluno_ava.get("nome", "").strip().lower()

        # 1. Busca por RA
        if ra_ava:
            for s in lista_sophia:
                if str(s.get("ra", "")).strip() == str(ra_ava).strip():
                    return {"status": "MATCH_EXATO", "aluno_sophia": s}

        # 2. Busca por Nome Exato
        matches_nome = [s for s in lista_sophia if s.get("nome", "").strip().lower() == nome_ava]
        if len(matches_nome) == 1:
            return {"status": "MATCH_EXATO", "aluno_sophia": matches_nome[0]}
        elif len(matches_nome) > 1:
            return {"status": "HOMONIMO_DIVERGENTE", "candidatos": matches_nome}

        return {"status": "SOMENTE_NO_AVA", "aluno_ava": aluno_ava}
