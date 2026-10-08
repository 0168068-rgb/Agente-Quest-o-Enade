import os
import sys
import shutil
import subprocess

# Garantir suporte a codificação UTF-8 no console Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def build():
    print("==========================================================")
    print(" 🛠️ COMPILANDO AVALIA AUTOBATCH PARA WINDOWS (.EXE)")
    print("==========================================================")
    
    # 1. Instalar dependências necessárias
    print("📦 Verificando e instalando bibliotecas no Python...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "pandas", "openpyxl", "playwright", "python-docx"], check=False)

    # 2. Argumentos do PyInstaller (invocado via sys.executable -m PyInstaller para evitar erro de PATH no Windows)
    pyinstaller_args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name=AVALIA_AutoBatch",
        "--icon=NONE",
        "--exclude-module=matplotlib",
        "--exclude-module=scipy",
        "--exclude-module=jedi",
        "--exclude-module=parso",
        "--exclude-module=PIL",
        "--exclude-module=IPython",
        "--exclude-module=pygments",
        "--exclude-module=curses",
        "--exclude-module=unittest",
        "--exclude-module=sqlite3",
        "--clean",
        "app_avalia_gui.py"
    ]

    print(f"\n🚀 Executando PyInstaller: {' '.join(pyinstaller_args)}")
    res = subprocess.run(pyinstaller_args)
    
    if res.returncode == 0:
        dist_dir = os.path.join("dist", "AVALIA_AutoBatch")
        print("\n📁 Copiando arquivos auxiliares para a pasta dist...")
        
        # Copiar Roteiro e Modelos para a pasta dist
        aux_files = [
            "Roteiro_de_Uso_AVALIA_AutoBatch.docx",
            "Roteiro_de_Uso_AVALIA_AutoBatch.md",
            "Modelo_Planilha_AVALIA_Exemplo.xlsx"
        ]
        
        for f in aux_files:
            if os.path.exists(f):
                shutil.copy(f, os.path.join(dist_dir, f))
                print(f"  └─ Copiado: {f}")
        
        # Garantir que o executável possua extensão .exe no pacote para Windows
        exe_path = os.path.join(dist_dir, "AVALIA_AutoBatch.exe")
        bin_path = os.path.join(dist_dir, "AVALIA_AutoBatch")
        if os.path.exists(bin_path) and not os.path.exists(exe_path):
            shutil.copy2(bin_path, exe_path)

        print("\n🎉 COMPILAÇÃO CONCLUÍDA COM SUCESSO!")
        print("==========================================================")
        print(f"📁 Pasta pronta para distribuição: {os.path.abspath(dist_dir)}")
        print(f"🚀 Executável principal: {os.path.abspath(exe_path)}")
        print("==========================================================")
    else:
        print(f"\n❌ Erro durante a compilação. Código de retorno: {res.returncode}")

if __name__ == "__main__":
    build()
