# -*- coding: utf-8 -*-
import os, glob, shutil

# 1. Modificar os scripts build_batch_tg_1.py ate 6.py para usar subfolder='AD' e prefixo 'AD '
for i in range(1, 7):
    script_path = f"/home/hamilcar/Antigravity/build_batch_tg_{i}.py"
    if os.path.exists(script_path):
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Substituir "TG " por "AD " e subfolder='TG' por subfolder='AD'
        new_content = content.replace('"TG ', '"AD ').replace("subfolder='TG'", "subfolder='AD'")
        
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Atualizado {script_path} para AD")

# 2. Executar todos os 6 scripts de batch
print("\n--- Executando geração dos arquivos AD ---")
for i in range(1, 7):
    os.system(f"python3 /home/hamilcar/Antigravity/build_batch_tg_{i}.py")

# 3. Remover pastas 'TG' criadas anteriormente dentro de 'Provas 2026-4'
print("\n--- Limpando pastas 'TG' residuais ---")
nead_base = "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD"
tg_dirs = glob.glob(os.path.join(nead_base, "*", "Provas 2026-4", "TG"))
for d in tg_dirs:
    if os.path.isdir(d):
        shutil.rmtree(d)
        print(f"Removido: {d}")

print("\nProcesso de migração de TG para AD concluído com sucesso!")
