#!/usr/bin/env python3
"""
Harness Principal para Testes e Diagnóstico do SmartFox Autônomo 11.2
Verifica arquivos essenciais, integridade dos templates e manifesto.
"""

import os
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
EXTENSAO_DIR = BASE_DIR / "src" / "extensao"

def verificar_integridade():
    print("🦊 [Harness SmartFox] Verificando integridade da extensão...")
    
    arquivos_essenciais = [
        "manifest.json",
        "background.js",
        "page-bridge.js",
        "content.js",
        "tools-hub.js",
        "bank-manager.js",
        "grading-assistant.js",
        "docx-parser.js",
        "docx-exporter.js",
        "pdf-reader.js"
    ]
    
    faltando = []
    for arq in arquivos_essenciais:
        p = EXTENSAO_DIR / arq
        if not p.is_file():
            faltando.append(arq)
            
    if faltando:
        print(f"❌ Arquivos ausentes: {faltando}")
        return False
        
    manifest_path = EXTENSAO_DIR / "manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    print(f"✅ Extensão: {manifest.get('name')} v{manifest.get('version')}")
    print(f"✅ Domínio Alvo: {manifest.get('host_permissions', [])}")
    print("🎉 SmartFox 11.2 operacional e pronto para uso no AvaliA!")
    return True

if __name__ == "__main__":
    ok = verificar_integridade()
    sys.exit(0 if ok else 1)
