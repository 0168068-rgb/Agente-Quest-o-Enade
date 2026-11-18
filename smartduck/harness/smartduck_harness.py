#!/usr/bin/env python3
"""
Harness Principal para Testes e Diagnóstico do SmartDuck
Executa rotinas de verificação da extensão, auditoria de arquivos e integridade de conciliação.
"""

import os
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
EXTENSAO_DIR = BASE_DIR / "src" / "extensao"
CONFIG_FILE = BASE_DIR / "config" / "config_smartduck.json"

sys.path.insert(0, str(BASE_DIR / "harness" / "guardrails"))
try:
    from regras_validacao_smartduck import SmartDuckGuardrails
except ImportError:
    SmartDuckGuardrails = None


def verificar_integridade_extensao() -> bool:
    """Verifica se os arquivos essenciais do Manifest V3 do SmartDuck estão presentes."""
    print("🦆 [Harness SmartDuck] Verificando integridade dos arquivos da extensão...")
    
    arquivos_essenciais = [
        "manifest.json",
        "background.js",
        "widget.js",
        "painel.html",
        "painel.mjs",
        "batch-engine.mjs",
        "ava.mjs",
        "portal.mjs",
        "reconcile.mjs",
        "report-xlsx.mjs"
    ]
    
    faltando = []
    for arq in arquivos_essenciais:
        p = EXTENSAO_DIR / arq
        if not p.is_file():
            faltando.append(arq)
            
    if faltando:
        print(f"❌ Arquivos ausentes na extensão: {faltando}")
        return False
        
    print(f"✅ Todos os {len(arquivos_essenciais)} módulos essenciais estão presentes.")
    
    # Validar JSON do manifest
    manifest_path = EXTENSAO_DIR / "manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    print(f"ℹ️  Extensão: {manifest.get('name')} v{manifest.get('version')}")
    print(f"ℹ️  Manifest Version: {manifest.get('manifest_version')}")
    print(f"ℹ️  Permissões: {', '.join(manifest.get('permissions', []))}")
    return True


def executar_testes_guardrails() -> bool:
    """Executa testes de validação dos guardrails de notas e conciliação."""
    print("\n🛡️  [Harness SmartDuck] Executando testes unitários dos guardrails...")
    if not SmartDuckGuardrails:
        print("❌ Guardrails não puderam ser carregados.")
        return False
        
    # Teste de notas
    assert SmartDuckGuardrails.validar_nota("8,5") == 8.5
    assert SmartDuckGuardrails.validar_nota("10") == 10.0
    assert SmartDuckGuardrails.validar_nota("F") == 0.0
    assert SmartDuckGuardrails.validar_nota("") is None
    
    # Teste de sobreposição
    assert SmartDuckGuardrails.verificar_sobreposicao(None, 8.0) is True
    assert SmartDuckGuardrails.verificar_sobreposicao(9.0, 8.0, permitir_sobrescrita=False) is False
    assert SmartDuckGuardrails.verificar_sobreposicao(9.0, 8.0, permitir_sobrescrita=True) is True
    
    # Teste de conciliação
    sophia = [{"ra": "12345", "nome": "Fulano de Tal"}]
    ava_match = {"ra": "12345", "nome": "Fulano de Tal"}
    ava_novo = {"ra": "99999", "nome": "Ciclano Novo"}
    
    res1 = SmartDuckGuardrails.conciliar_aluno(ava_match, sophia)
    assert res1["status"] == "MATCH_EXATO"
    
    res2 = SmartDuckGuardrails.conciliar_aluno(ava_novo, sophia)
    assert res2["status"] == "SOMENTE_NO_AVA"
    
    print("✅ Todos os guardrails e testes de lógica de negócios passaram com sucesso.")
    return True


def main():
    print("=" * 60)
    print("        🚀 HARNESS DE AUTOMAÇÃO SMARTDUCK 1.9.0             ")
    print("=" * 60)
    
    ok_ext = verificar_integridade_extensao()
    ok_gr = executar_testes_guardrails()
    
    if ok_ext and ok_gr:
        print("\n🎉 Ambiente do SmartDuck 1.9.0 validado e operacional para uso no Linux.")
        sys.exit(0)
    else:
        print("\n❌ Falha na validação do ambiente.")
        sys.exit(1)


if __name__ == "__main__":
    main()
