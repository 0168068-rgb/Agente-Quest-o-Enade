# -*- coding: utf-8 -*-
import argparse, os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent_core import AgenteGeradorENADE

def main():
    parser = argparse.ArgumentParser(description="Agente de IA para Geracao de Questoes no Padrao ENADE")
    parser.add_argument("--curso", type=str, required=True, help="Curso (ADS, GTI, REDES, CIENCIA_COMPUTACAO)")
    parser.add_argument("--topico", type=str, required=True, help="Topico tecnico da questao")
    parser.add_argument("--tipo", type=str, default="ESCOLHA_COMBINADA", help="Tipo estrutural")
    
    args = parser.parse_args()
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    agent = AgenteGeradorENADE(base_dir)
    
    print("[AGENTE ENADE] Iniciando para o curso [" + str(args.curso) + "] - Topico: [" + str(args.topico) + "]...")
    prompt_completo = agent.generate_question(args.curso, args.topico, args.tipo)
    
    print("[AGENTE ENADE] Contexto, Memoria de Longo Prazo e Guardrails carregados com sucesso!")
    print("\n--- PROMPT SINTETIZADO PRONTO PARA PROCESSAMENTO ---")
    print(prompt_completo[:400] + "\n...")

if __name__ == "__main__":
    main()
