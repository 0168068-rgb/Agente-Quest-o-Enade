import os
import sys
import shutil
import subprocess

def build_installer():
    print("==========================================================")
    print(" 🛠️ COMPILANDO INSTALADOR WINDOWS (.EXE SETUP INSTALLER)")
    print("==========================================================")
    
    # 1. Garantir que a pasta dist/AVALIA_AutoBatch já existe
    dist_payload = os.path.join("dist", "AVALIA_AutoBatch")
    if not os.path.exists(dist_payload):
        print("📦 Compilando a aplicação principal primeiro...")
        import build_windows_exe
        build_windows_exe.build()

    # 2. Argumentos do PyInstaller para o Instalador
    pyinstaller_args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name=AVALIA_AutoBatch_Setup_Instalador",
        "--add-data=" + f"{dist_payload}{os.pathsep}AVALIA_AutoBatch",
        "--clean",
        "installer_setup_wizard.py"
    ]

    print(f"\n🚀 Executando PyInstaller para o Instalador: {' '.join(pyinstaller_args)}")
    res = subprocess.run(pyinstaller_args)
    
    if res.returncode == 0:
        installer_exe = os.path.join("dist", "AVALIA_AutoBatch_Setup_Instalador.exe")
        installer_bin = os.path.join("dist", "AVALIA_AutoBatch_Setup_Instalador")
        if os.path.exists(installer_bin) and not os.path.exists(installer_exe):
            shutil.copy2(installer_bin, installer_exe)
        if os.path.exists(installer_bin) and os.path.exists(installer_exe):
            try: os.remove(installer_bin)
            except Exception: pass

        print("\n🎉 INSTALADOR CRIADO COM SUCESSO!")
        print("==========================================================")
        print(f"🚀 Executável do Instalador: {os.path.abspath(installer_exe)}")
        print("==========================================================")
    else:
        print(f"\n❌ Erro durante a criação do instalador. Código: {res.returncode}")

if __name__ == "__main__":
    build_installer()
