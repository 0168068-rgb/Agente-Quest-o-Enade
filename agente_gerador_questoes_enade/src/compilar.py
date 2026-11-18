#!/usr/bin/env python3
"""
Script de compilação automática para Windows/Linux
"""
import sys
import subprocess

def run_cmd(cmd):
    print(f"-> Executando: {cmd}")
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        print(f"⚠️ Erro ao executar: {cmd}")

print("======================================================================")
print("  COMPILADOR DO LANÇADOR DE FREQUÊNCIA SOPHIA")
print("======================================================================")

print("\n1. Instalando dependências...")
run_cmd(f"{sys.executable} -m pip install -r requirements.txt")
run_cmd(f"{sys.executable} -m pip install pyinstaller customtkinter playwright")
run_cmd(f"{sys.executable} -m playwright install chromium")

print("\n2. Compilando executável...")
run_cmd(f"{sys.executable} -m PyInstaller --noconsole --onefile --name=\"LancadorFrequenciaSophia\" app_frequencia_sophia.py")

print("\n======================================================================")
print("  SUCESSO! O arquivo foi gerado na pasta 'dist'.")
print("======================================================================")
input("\nPressione ENTER para fechar...")
