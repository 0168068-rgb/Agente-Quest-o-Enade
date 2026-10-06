# -*- coding: utf-8 -*-
"""
Núcleo do Agente de IA para Geração de Questões ENADE.
Orquestra o carregamento de contexto, memória de longo prazo, síntese de prompt, chamada de modelo LLM e motor de guardrails.
"""
import os, sys, yaml
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.memory_manager import MemoryManager
from src.guardrail_engine import GuardrailEngine

class AgenteGeradorENADE:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.memory_mgr = MemoryManager(base_dir)
        self.guardrails = GuardrailEngine()
        self.config = self._load_config()
        self.system_prompt = self._load_system_prompt()

    def _load_config(self) -> dict:
        config_path = os.path.join(self.base_dir, "config/agent_config.yaml")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {}

    def _load_system_prompt(self) -> str:
        prompt_path = os.path.join(self.base_dir, "context/system_prompt_especialista_enade.md")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def generate_question(self, curso: str, topico: str, tipo_estrutural: str = "ESCOLHA_COMBINADA") -> str:
        """
        Executa a geração de uma questão ENADE no padrão bifurcado.
        Injeta a base de memória de longo prazo e as regras de distratores do INEP.
        """
        kb = self.memory_mgr.load_long_term_memory()
        distractors = self.memory_mgr.load_distractors_patterns()
        
        prompt_montado = f"""
{self.system_prompt}

### PARÂMETROS DA SOLICITAÇÃO ATIVA:
- Curso: {curso}
- Tópico Técnico: {topico}
- Tipo Estrutural Solicitado: {tipo_estrutural}

### DIRETRIZES DE MEMÓRIA E REGRAS DA BASE:
- Diretrizes do Curso ({curso}): {kb.get("diretrizes_curriculares", {}).get(curso, "Tópicos de Tecnologia")}
- Padrões de Distratores do INEP a aplicar: {distractors.get("padroes_erros_alunos", [])}

Gere a questão completa no formato Markdown com a PARTE I (Versão do Estudante) e a PARTE II (Versão do Professor contendo a Ficha de Especificação de 23 campos, Resolução Comentada e Justificativa de cada distrator).
"""
        return prompt_montado
