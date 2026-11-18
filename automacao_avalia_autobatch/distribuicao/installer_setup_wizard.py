#!/usr/bin/env python3
"""
AVALIA AutoBatch — Assistente de Instalação para Windows (.EXE Installer)
==========================================================================
Instalador gráfico interativo que pergunta o diretório de destino,
cria atalhos na Área de Trabalho (Desktop) e no Menu Iniciar, e instala a aplicação.
"""

import os
import sys
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class AVALIAInstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Assistente de Instalação — AVALIA AutoBatch v5.1")
        self.root.geometry("640x480")
        self.root.resizable(False, False)
        self.root.configure(bg="#11111b")

        self._load_installer_icon()

        # Configurar diretório padrão de instalação
        if sys.platform == "win32":
            local_appdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
            self.default_install_dir = os.path.join(local_appdata, "Programs", "AVALIA_AutoBatch")
        else:
            self.default_install_dir = os.path.expanduser("~/AVALIA_AutoBatch")

        self.install_dir_var = tk.StringVar(value=self.default_install_dir)
        self.create_desktop_shortcut_var = tk.BooleanVar(value=True)
        self.create_startmenu_shortcut_var = tk.BooleanVar(value=True)
        self.run_after_install_var = tk.BooleanVar(value=True)

        self.setup_styles()
        self.build_ui()

    def _load_installer_icon(self):
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            icon_ico = os.path.join(base_dir, "assets", "icon.ico")
            icon_png = os.path.join(base_dir, "assets", "icon_64x64.png")
            if sys.platform.startswith("win") and os.path.exists(icon_ico):
                self.root.iconbitmap(default=icon_ico)
            elif os.path.exists(icon_png):
                self._icon_img = tk.PhotoImage(file=icon_png)
                self.root.iconphoto(True, self._icon_img)
        except Exception:
            pass

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        self.BG_MAIN = "#11111b"
        self.BG_CARD = "#1e1e2e"
        self.BG_INPUT = "#313244"
        self.BORDER_CARD = "#45475a"
        self.ACCENT_BLUE = "#89b4fa"
        self.ACCENT_GREEN = "#a6e3a1"
        self.TEXT_PRIMARY = "#cdd6f4"
        self.TEXT_MUTED = "#a6adc8"

        style.configure(".", background=self.BG_MAIN, foreground=self.TEXT_PRIMARY, font=("Segoe UI", 10))
        style.configure("TLabel", background=self.BG_MAIN, foreground=self.TEXT_PRIMARY)
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground=self.ACCENT_BLUE, background=self.BG_MAIN)
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10), foreground=self.TEXT_MUTED, background=self.BG_MAIN)
        style.configure("Card.TFrame", background=self.BG_CARD)

    def build_ui(self):
        # Header
        header = ttk.Frame(self.root, padding=(25, 18))
        header.pack(fill="x")

        lbl_title = ttk.Label(header, text="⚡ Instalação do AVALIA AutoBatch v5.1", style="Title.TLabel")
        lbl_title.pack(anchor="w")

        lbl_sub = ttk.Label(header, text="Assistente de Configuração e Criação de Atalhos no Windows", style="Subtitle.TLabel")
        lbl_sub.pack(anchor="w", pady=(2, 0))

        ttk.Separator(self.root, orient="horizontal").pack(fill="x", padx=25)

        # Card Principal
        card = ttk.Frame(self.root, style="Card.TFrame", padding=20)
        card.pack(fill="both", expand=True, padx=25, pady=20)

        # 1. Escolha de Pasta de Destino
        lbl_dest = tk.Label(card, text="1. Selecione a pasta onde o programa será instalado:", font=("Segoe UI", 10, "bold"), fg=self.ACCENT_BLUE, bg=self.BG_CARD)
        lbl_dest.pack(anchor="w", pady=(0, 6))

        dir_box = tk.Frame(card, bg=self.BG_CARD)
        dir_box.pack(fill="x", pady=(0, 15))

        entry_dir = tk.Entry(dir_box, textvariable=self.install_dir_var, font=("Segoe UI", 10), bg=self.BG_INPUT, fg=self.TEXT_PRIMARY, insertbackground=self.TEXT_PRIMARY, relief="flat", bd=4)
        entry_dir.pack(side="left", fill="x", expand=True, padx=(0, 10))

        btn_browse = tk.Button(dir_box, text="📂 Procurar...", command=self.browse_folder, font=("Segoe UI", 9, "bold"), bg=self.BG_INPUT, fg=self.TEXT_PRIMARY, activebackground="#45475a", activeforeground=self.TEXT_PRIMARY, relief="flat", bd=0, padx=12, pady=5, cursor="hand2")
        btn_browse.pack(side="right")

        # 2. Opções de Atalhos
        lbl_options = tk.Label(card, text="2. Opções de Atalhos no Windows:", font=("Segoe UI", 10, "bold"), fg=self.ACCENT_BLUE, bg=self.BG_CARD)
        lbl_options.pack(anchor="w", pady=(0, 6))

        chk_desktop = tk.Checkbutton(
            card,
            text="☑️ Criar atalho na Área de Trabalho (Desktop)",
            variable=self.create_desktop_shortcut_var,
            bg=self.BG_CARD,
            fg=self.ACCENT_GREEN,
            activebackground=self.BG_CARD,
            activeforeground=self.ACCENT_GREEN,
            selectcolor=self.BG_INPUT,
            font=("Segoe UI", 10)
        )
        chk_desktop.pack(anchor="w", pady=2)

        chk_startmenu = tk.Checkbutton(
            card,
            text="☑️ Criar atalho no Menu Iniciar (Start Menu)",
            variable=self.create_startmenu_shortcut_var,
            bg=self.BG_CARD,
            fg=self.ACCENT_GREEN,
            activebackground=self.BG_CARD,
            activeforeground=self.ACCENT_GREEN,
            selectcolor=self.BG_INPUT,
            font=("Segoe UI", 10)
        )
        chk_startmenu.pack(anchor="w", pady=2)

        chk_run = tk.Checkbutton(
            card,
            text="☑️ Abrir o AVALIA AutoBatch após concluir a instalação",
            variable=self.run_after_install_var,
            bg=self.BG_CARD,
            fg=self.TEXT_PRIMARY,
            activebackground=self.BG_CARD,
            activeforeground=self.TEXT_PRIMARY,
            selectcolor=self.BG_INPUT,
            font=("Segoe UI", 10)
        )
        chk_run.pack(anchor="w", pady=(8, 0))

        # Status
        self.lbl_status = tk.Label(card, text="Pronto para instalar.", font=("Segoe UI", 9, "italic"), fg=self.TEXT_MUTED, bg=self.BG_CARD)
        self.lbl_status.pack(anchor="w", pady=(15, 0))

        # Barra de Progresso
        self.progress = ttk.Progressbar(card, mode="determinate")
        self.progress.pack(fill="x", pady=(5, 0))

        # Rodapé com Botões de Ação
        footer = ttk.Frame(self.root, padding=(25, 12))
        footer.pack(fill="x", side="bottom")

        btn_cancel = tk.Button(footer, text="Cancelar", command=self.root.destroy, font=("Segoe UI", 10), bg="#45475a", fg=self.TEXT_PRIMARY, activebackground="#585b70", activeforeground=self.TEXT_PRIMARY, relief="flat", padx=15, pady=6, cursor="hand2")
        btn_cancel.pack(side="left")

        self.btn_install = tk.Button(footer, text="🚀 INSTALAR AGORA", command=self.start_install, font=("Segoe UI", 11, "bold"), bg=self.ACCENT_BLUE, fg="#11111b", activebackground="#b4befe", activeforeground="#11111b", relief="flat", padx=25, pady=6, cursor="hand2")
        self.btn_install.pack(side="right")

    def browse_folder(self):
        chosen = filedialog.askdirectory(title="Selecione a Pasta de Destino da Instalação", initialdir=self.install_dir_var.get())
        if chosen:
            self.install_dir_var.set(chosen)

    def start_install(self):
        target_dir = os.path.abspath(self.install_dir_var.get())
        self.btn_install.config(state="disabled")
        self.lbl_status.config(text="Instalando arquivos...", fg=self.ACCENT_BLUE)
        self.progress["value"] = 20
        self.root.update()

        try:
            os.makedirs(target_dir, exist_ok=True)

            # Localizar pasta dos arquivos a serem copiados
            src_dir = None
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                payload_dir = os.path.join(sys._MEIPASS, "AVALIA_AutoBatch")
                if os.path.exists(payload_dir):
                    src_dir = payload_dir
            if not src_dir:
                possible_src = [
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist", "AVALIA_AutoBatch"),
                    os.path.join(os.getcwd(), "dist", "AVALIA_AutoBatch"),
                    os.path.dirname(os.path.abspath(__file__))
                ]
                for p in possible_src:
                    if os.path.exists(p) and (os.path.exists(os.path.join(p, "AVALIA_AutoBatch.exe")) or os.path.exists(os.path.join(p, "app_avalia_gui.py"))):
                        src_dir = p
                        break

            if not src_dir:
                src_dir = os.path.dirname(os.path.abspath(__file__))

            self.progress["value"] = 50
            self.lbl_status.config(text="Copiando arquivos de aplicação...")
            self.root.update()

            # Copiar arquivos
            for item in os.listdir(src_dir):
                s = os.path.join(src_dir, item)
                d = os.path.join(target_dir, item)
                if os.path.isdir(s):
                    if os.path.exists(d):
                        shutil.rmtree(d)
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)

            self.progress["value"] = 80
            self.lbl_status.config(text="Criando atalhos no Windows...")
            self.root.update()

            # Localizar executável principal instalado
            exe_installed = os.path.join(target_dir, "AVALIA_AutoBatch.exe")
            if not os.path.exists(exe_installed):
                exe_installed = os.path.join(target_dir, "app_avalia_gui.py")

            # 1. Criar atalho na Área de Trabalho (Desktop)
            if self.create_desktop_shortcut_var.get():
                desktop_path = self.get_desktop_path()
                if desktop_path:
                    shortcut_file = os.path.join(desktop_path, "AVALIA AutoBatch.lnk")
                    self.create_windows_shortcut(exe_installed, shortcut_file, target_dir)

            # 2. Criar atalho no Menu Iniciar (Start Menu)
            if self.create_startmenu_shortcut_var.get():
                startmenu_path = self.get_startmenu_path()
                if startmenu_path:
                    start_folder = os.path.join(startmenu_path, "AVALIA AutoBatch")
                    os.makedirs(start_folder, exist_ok=True)
                    shortcut_file = os.path.join(start_folder, "AVALIA AutoBatch.lnk")
                    self.create_windows_shortcut(exe_installed, shortcut_file, target_dir)

            # 3. Criar desinstalador básico
            uninstaller_script = os.path.join(target_dir, "Desinstalar_AVALIA_AutoBatch.bat")
            with open(uninstaller_script, "w", encoding="latin-1", errors="ignore") as f:
                f.write(f'@echo off\n')
                f.write(f'echo Desinstalando AVALIA AutoBatch...\n')
                f.write(f'rmdir /s /q "{target_dir}"\n')
                f.write(f'echo Desinstalacao concluida!\n')

            self.progress["value"] = 100
            self.lbl_status.config(text="🎉 Instalação concluída com sucesso!", fg=self.ACCENT_GREEN)
            
            messagebox.showinfo(
                "Instalação Concluída",
                f"🎉 O AVALIA AutoBatch v5.1 foi instalado com sucesso!\n\n"
                f"📁 Pasta de Instalação:\n{target_dir}\n\n"
                f"Atalhos criados conforme selecionado."
            )

            if self.run_after_install_var.get() and os.path.exists(exe_installed):
                try:
                    if sys.platform == "win32":
                        os.startfile(exe_installed)
                    else:
                        subprocess.Popen([sys.executable, exe_installed])
                except Exception:
                    pass

            self.root.destroy()

        except Exception as e:
            self.lbl_status.config(text=f"Erro na instalação: {e}", fg="#f38ba8")
            messagebox.showerror("Erro de Instalação", f"Ocorreu uma falha durante a instalação:\n{e}")
            self.btn_install.config(state="normal")

    def get_desktop_path(self):
        if sys.platform == "win32":
            userprofile = os.environ.get("USERPROFILE", os.path.expanduser("~"))
            desktop = os.path.join(userprofile, "Desktop")
            if os.path.exists(desktop): return desktop
            desktop_pt = os.path.join(userprofile, "Área de Trabalho")
            if os.path.exists(desktop_pt): return desktop_pt
            return desktop
        return os.path.expanduser("~/Desktop")

    def get_startmenu_path(self):
        if sys.platform == "win32":
            appdata = os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
            return os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs")
        return None

    def create_windows_shortcut(self, target_exe, shortcut_path, working_dir):
        if sys.platform != "win32":
            vbs_script = os.path.join(working_dir, "criar_atalhos.vbs")
            with open(vbs_script, "w", encoding="utf-8") as f:
                f.write(f'Set oWS = WScript.CreateObject("WScript.Shell")\n')
                f.write(f'sLinkFile = "{shortcut_path}"\n')
                f.write(f'Set oLink = oWS.CreateShortcut(sLinkFile)\n')
                f.write(f'oLink.TargetPath = "{target_exe}"\n')
                f.write(f'oLink.WorkingDirectory = "{working_dir}"\n')
                f.write(f'oLink.Description = "AVALIA AutoBatch — Automação de Questões em Lote"\n')
                f.write(f'oLink.Save\n')
            return

        try:
            vbs_code = f"""
            Set oWS = CreateObject("WScript.Shell")
            sLinkFile = "{shortcut_path}"
            Set oLink = oWS.CreateShortcut(sLinkFile)
            oLink.TargetPath = "{target_exe}"
            oLink.WorkingDirectory = "{working_dir}"
            oLink.Description = "AVALIA AutoBatch — Automação de Questões em Lote"
            oLink.Save
            """
            vbs_path = os.path.join(os.environ.get("TEMP", os.getcwd()), "make_link.vbs")
            with open(vbs_path, "w", encoding="latin-1") as f:
                f.write(vbs_code)
            subprocess.run(["cscript", "//Nologo", vbs_path], check=False)
            if os.path.exists(vbs_path):
                os.remove(vbs_path)
        except Exception as e:
            print(f"Erro ao criar atalho: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AVALIAInstallerApp(root)
    root.mainloop()
