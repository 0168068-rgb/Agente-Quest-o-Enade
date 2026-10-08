#!/usr/bin/env python3
"""
======================================================================
  🎓 AUTOMAÇÃO DE REGISTRO DE FREQUÊNCIA - PORTAL SOPHIA (UNIG / NEAD)
  Interface Gráfica Dinâmica de 2 Passos (GUI) para Professores
======================================================================
"""

import os
import re
import sys
import json
import io
import asyncio
import threading
import queue
import requests
import pandas as pd
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Importa as funções principais do script de backend
from registrar_frequencia_sophia import (
    auto_detect_sheet_and_columns,
    load_dates_and_presents,
    load_student_courses,
    run_automation,
    SOPHIA_URL
)

# Configuração do caminho de navegadores do Playwright para executáveis (.exe)
if os.name == 'nt':
    local_appdata = os.environ.get('LOCALAPPDATA', os.path.expanduser('~/AppData/Local'))
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.join(local_appdata, 'ms-playwright')
else:
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.expanduser('~/.cache/ms-playwright')

# Configurações globais de tema do CustomTkinter
ctk.set_appearance_mode("System")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue")

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config_usuario.json")

def parse_google_sheet_id(url_or_id: str) -> str:
    """Extrai o ID da planilha do Google a partir do link fornecido."""
    if not url_or_id:
        return None
    url_or_id = url_or_id.strip()
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url_or_id)
    if match:
        return match.group(1)
    if len(url_or_id) > 20 and '/' not in url_or_id:
        return url_or_id
    return None

def download_google_sheet_as_excel(sheet_id: str) -> str:
    """Baixa a planilha pública ou compartilhada do Google Sheets como arquivo Excel temporário."""
    export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    
    headers = {}
    token_path = '/home/hamilcar/Downloads/token_drive.json'
    if os.path.exists(token_path):
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            headers['Authorization'] = f'Bearer {creds.token}'
        except Exception:
            pass

    response = requests.get(export_url, headers=headers, timeout=15)
    if response.status_code == 200:
        temp_path = os.path.join(os.path.dirname(__file__), "_temp_planilha_google.xlsx")
        with open(temp_path, "wb") as f:
            f.write(response.content)
        return temp_path
    else:
        raise Exception(f"Não foi possível baixar a planilha do Google (Status HTTP: {response.status_code}). Verifique se o link está correto e se o acesso está liberado.")

class SophiaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🎓 Automação de Frequência SophiA - UNIG / NEAD")
        self.geometry("880x760")
        self.minsize(800, 700)

        self.msg_queue = queue.Queue()
        self.is_running = False
        self.loaded_file_path = None
        self.dates_dict = {}
        self.courses_dict = {}
        self.raw_dates_list = []

        self.create_widgets()
        self.load_saved_config()
        self.check_queue()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # ------------------------------------------------------------------
        # 1. CABEÇALHO / TÍTULO
        # ------------------------------------------------------------------
        header_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("#1f538d", "#14375e"))
        header_frame.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="ew")

        title_label = ctk.CTkLabel(
            header_frame,
            text="🎓 AUTOMAÇÃO DE REGISTRO DE FREQUÊNCIA SOPHIA",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        title_label.pack(padx=20, pady=(12, 2))

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Faculdade UNIG / NEAD — Desenvolvido por Hamilcar Silva",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#e0e0e0"
        )
        subtitle_label.pack(padx=20, pady=(0, 12))

        # ------------------------------------------------------------------
        # 2. PASSO 1: CARREGAR PLANILHA
        # ------------------------------------------------------------------
        passo1_frame = ctk.CTkFrame(self, corner_radius=10)
        passo1_frame.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        passo1_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            passo1_frame,
            text="PASSO 1: Selecionar e Carregar Planilha",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1f538d", "#3b82f6")
        ).grid(row=0, column=0, columnspan=3, padx=15, pady=(10, 5), sticky="w")

        ctk.CTkLabel(passo1_frame, text="Planilha (Link ou Excel):", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=15, pady=8, sticky="w")
        
        input_file_frame = ctk.CTkFrame(passo1_frame, fg_color="transparent")
        input_file_frame.grid(row=1, column=1, padx=(0, 10), pady=8, sticky="ew")
        input_file_frame.grid_columnconfigure(0, weight=1)

        self.entry_planilha = ctk.CTkEntry(input_file_frame, placeholder_text="Cole o Link da Planilha do Google Drive ou escolha um arquivo Excel...")
        self.entry_planilha.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        btn_browse = ctk.CTkButton(input_file_frame, text="📁 Procurar", width=90, command=self.browse_file)
        btn_browse.grid(row=0, column=1, sticky="e")

        self.btn_carregar = ctk.CTkButton(
            passo1_frame,
            text="🔍 Carregar Planilha",
            width=150,
            font=ctk.CTkFont(weight="bold"),
            fg_color="#3b82f6",
            hover_color="#2563eb",
            command=self.load_spreadsheet_data
        )
        self.btn_carregar.grid(row=1, column=2, padx=(0, 15), pady=8, sticky="e")

        self.lbl_status_planilha = ctk.CTkLabel(
            passo1_frame,
            text="⚠️ Nenhuma planilha carregada ainda. Cole o link e clique em 'Carregar Planilha'.",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="#d97706"
        )
        self.lbl_status_planilha.grid(row=2, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="w")

        self.chk_save_planilha = ctk.CTkCheckBox(passo1_frame, text="Lembrar link da planilha")
        self.chk_save_planilha.grid(row=2, column=2, padx=(0, 15), pady=(0, 10), sticky="e")
        self.chk_save_planilha.select()

        # ------------------------------------------------------------------
        # 3. PASSO 2: DADOS DO SOPHIA E SELEÇÃO DINÂMICA
        # ------------------------------------------------------------------
        passo2_frame = ctk.CTkFrame(self, corner_radius=10)
        passo2_frame.grid(row=2, column=0, padx=15, pady=5, sticky="ew")
        passo2_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            passo2_frame,
            text="PASSO 2: Credenciais e Opções Detectadas",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1f538d", "#3b82f6")
        ).grid(row=0, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="w")

        # Credenciais
        ctk.CTkLabel(passo2_frame, text="Usuário SophiA:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=15, pady=6, sticky="w")
        self.entry_usuario = ctk.CTkEntry(passo2_frame, placeholder_text="Ex: prof.joao ou código de acesso")
        self.entry_usuario.grid(row=1, column=1, padx=(0, 15), pady=6, sticky="ew")

        ctk.CTkLabel(passo2_frame, text="Senha SophiA:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=15, pady=6, sticky="w")
        
        pass_frame = ctk.CTkFrame(passo2_frame, fg_color="transparent")
        pass_frame.grid(row=2, column=1, padx=(0, 15), pady=6, sticky="ew")
        pass_frame.grid_columnconfigure(0, weight=1)

        self.entry_senha = ctk.CTkEntry(pass_frame, show="•", placeholder_text="Sua senha de acesso ao portal SophiA")
        self.entry_senha.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.btn_show_pass = ctk.CTkButton(pass_frame, text="👁️", width=40, command=self.toggle_password)
        self.btn_show_pass.grid(row=0, column=1, sticky="e")

        # Turma (OptionMenu alimentado dinamicamente)
        ctk.CTkLabel(passo2_frame, text="Turma / Curso (da Planilha):", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, padx=15, pady=6, sticky="w")
        self.option_turma = ctk.CTkOptionMenu(passo2_frame, values=["Carregue a planilha primeiro..."], command=self.on_turma_selected)
        self.option_turma.grid(row=3, column=1, padx=(0, 15), pady=6, sticky="ew")

        # Disciplina
        ctk.CTkLabel(passo2_frame, text="Disciplina:", font=ctk.CTkFont(weight="bold")).grid(row=4, column=0, padx=15, pady=6, sticky="w")
        self.entry_disciplina = ctk.CTkEntry(passo2_frame, placeholder_text="Ex: 065 - Programação em PYTHON")
        self.entry_disciplina.grid(row=4, column=1, padx=(0, 15), pady=6, sticky="ew")

        # Data da Chamada (OptionMenu alimentado dinamicamente)
        ctk.CTkLabel(passo2_frame, text="Data da Chamada (da Planilha):", font=ctk.CTkFont(weight="bold")).grid(row=5, column=0, padx=15, pady=6, sticky="w")
        
        data_frame = ctk.CTkFrame(passo2_frame, fg_color="transparent")
        data_frame.grid(row=5, column=1, padx=(0, 15), pady=6, sticky="ew")
        data_frame.grid_columnconfigure(0, weight=1)

        self.option_data = ctk.CTkOptionMenu(data_frame, values=["Carregue a planilha primeiro..."])
        self.option_data.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.chk_save_credentials = ctk.CTkCheckBox(data_frame, text="Lembrar meus dados")
        self.chk_save_credentials.grid(row=0, column=1, sticky="e")

        # ------------------------------------------------------------------
        # 4. OPÇÕES DE NAVEGAÇÃO E BOTÃO DE AÇÃO
        # ------------------------------------------------------------------
        action_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        action_frame.grid(row=3, column=0, padx=15, pady=5, sticky="ew")
        action_frame.grid_columnconfigure(1, weight=1)

        self.chk_headful = ctk.CTkCheckBox(action_frame, text="Exibir janela do navegador durante o lançamento")
        self.chk_headful.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.switch_dry_run = ctk.CTkSwitch(action_frame, text="Modo Simulação (não clica em Salvar no SophiA)")
        self.switch_dry_run.grid(row=0, column=1, padx=10, pady=5, sticky="e")

        self.btn_iniciar = ctk.CTkButton(
            action_frame,
            text="🚀 INICIAR LANÇAMENTO AUTOMÁTICO",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45,
            fg_color="#2fa572",
            hover_color="#1e7e54",
            command=self.start_automation
        )
        self.btn_iniciar.grid(row=1, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="ew")

        # ------------------------------------------------------------------
        # 5. ÁREA DE LOGS E BARRA DE PROGRESSO
        # ------------------------------------------------------------------
        log_frame = ctk.CTkFrame(self, corner_radius=10)
        log_frame.grid(row=4, column=0, padx=15, pady=(5, 15), sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)

        self.progress_bar = ctk.CTkProgressBar(log_frame)
        self.progress_bar.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="ew")
        self.progress_bar.set(0)

        self.log_text = ctk.CTkTextbox(log_frame, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_text.grid(row=1, column=0, padx=15, pady=(5, 5), sticky="nsew")

        footer_label = ctk.CTkLabel(
            log_frame,
            text="⚡ Feito por Hamilcar Silva",
            font=ctk.CTkFont(size=11, weight="bold", slant="italic"),
            text_color=("#1f538d", "#60a5fa")
        )
        footer_label.grid(row=2, column=0, padx=15, pady=(2, 8), sticky="e")

    def toggle_password(self):
        if self.entry_senha.cget("show") == "•":
            self.entry_senha.configure(show="")
            self.btn_show_pass.configure(text="🔒")
        else:
            self.entry_senha.configure(show="•")
            self.btn_show_pass.configure(text="👁️")

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Selecionar Planilha de Frequência",
            filetypes=[("Arquivos Excel", "*.xlsx *.xls"), ("Todos os arquivos", "*.*")]
        )
        if filename:
            self.entry_planilha.delete(0, "end")
            self.entry_planilha.insert(0, filename)

    def log(self, message: str):
        """Envia uma mensagem de log de forma thread-safe."""
        self.msg_queue.put(message)

    def check_queue(self):
        """Lê as mensagens da fila e atualiza a interface."""
        while not self.msg_queue.empty():
            msg = self.msg_queue.get()
            self.log_text.insert("end", msg + "\n")
            self.log_text.see("end")
            
            if "PROCESSANDO CHAMADA DO DIA" in msg:
                self.progress_bar.set(0.5)
            elif "Lançamento concluído com sucesso" in msg or "Processamento concluído" in msg:
                self.progress_bar.set(1.0)
                
        self.after(100, self.check_queue)

    def load_spreadsheet_data(self):
        """Lê a planilha informada no Passo 1 e atualiza dinamicamente as opções de Turmas e Datas."""
        planilha_val = self.entry_planilha.get().strip()
        if not planilha_val:
            messagebox.showerror("Erro", "Informe o Link da Planilha do Google ou selecione um arquivo Excel.")
            return

        self.btn_carregar.configure(state="disabled", text="⏳ Lendo...")
        self.lbl_status_planilha.configure(text="⏳ Baixando e analisando dados da planilha...", text_color="#3b82f6")
        
        threading.Thread(target=self._background_load_spreadsheet, args=(planilha_val,), daemon=True).start()

    def _background_load_spreadsheet(self, planilha_val):
        try:
            sheet_id = parse_google_sheet_id(planilha_val)
            if sheet_id:
                self.log(f"📥 Conectando ao Google Drive e baixando planilha (ID: {sheet_id})...")
                file_path = download_google_sheet_as_excel(sheet_id)
            else:
                file_path = planilha_val
                if not os.path.exists(file_path):
                    raise Exception(f"O arquivo não foi encontrado: {file_path}")

            sheet_name, date_col, name_col = auto_detect_sheet_and_columns(file_path)
            self.dates_dict = load_dates_and_presents(file_path, sheet_name, date_col, name_col)
            self.courses_dict = load_student_courses(file_path)
            self.loaded_file_path = file_path

            # Identificar cursos únicos
            turmas_encontradas = list(set(self.courses_dict.values())) if self.courses_dict else []
            if not turmas_encontradas:
                turmas_encontradas = ["S - 2026.2.1P - Análise e Des. de Sistemas"]

            # Identificar datas únicas com quantidade de presenças
            datas_opcoes = ["📅 TODAS AS DATAS PENDENTES"]
            for d, pres in self.dates_dict.items():
                datas_opcoes.append(f"{d} ({len(pres)} presentes)")

            # Atualizar os menus dropdown na thread principal
            self.after(0, self._update_dropdowns_after_load, turmas_encontradas, datas_opcoes)

        except Exception as e:
            self.after(0, self._handle_load_error, str(e))

    def on_turma_selected(self, selected_turma: str):
        """Atualiza a lista de datas exibidas conforme o curso/turma selecionado no menu."""
        if not self.dates_dict or not self.courses_dict:
            return

        from registrar_frequencia_sophia import get_student_course, courses_match
        datas_opcoes = [f"📅 TODAS AS DATAS PARA ESTA TURMA"]

        for d, presents in self.dates_dict.items():
            count_turma = 0
            for p in presents:
                st_course = get_student_course(p, self.courses_dict)
                if st_course and courses_match(st_course, selected_turma):
                    count_turma += 1

            datas_opcoes.append(f"{d} ({count_turma} presente(s) desta turma)")

        self.option_data.configure(values=datas_opcoes)
        self.option_data.set(datas_opcoes[0])

    def _update_dropdowns_after_load(self, turmas_encontradas, datas_opcoes):
        self.option_turma.configure(values=turmas_encontradas)
        self.option_turma.set(turmas_encontradas[0])

        self.on_turma_selected(turmas_encontradas[0])

        total_datas = len(self.dates_dict)
        total_presencas = sum(len(p) for p in self.dates_dict.values())

        self.lbl_status_planilha.configure(
            text=f"✅ Planilha carregada! Encontradas {total_datas} datas e {total_presencas} presenças no total.",
            text_color="#10b981"
        )
        self.log(f"✅ Planilha analisada: {total_datas} datas e {len(turmas_encontradas)} turma(s) identificada(s).")
        self.btn_carregar.configure(state="normal", text="🔍 Recarregar")

    def _handle_load_error(self, err_msg):
        self.lbl_status_planilha.configure(text=f"❌ Erro ao ler planilha: {err_msg}", text_color="#ef4444")
        self.log(f"❌ Erro na leitura da planilha: {err_msg}")
        self.btn_carregar.configure(state="normal", text="🔍 Tentar Novamente")
        messagebox.showerror("Erro na Planilha", f"Não foi possível ler a planilha:\n{err_msg}")

    def load_saved_config(self):
        """Carrega credenciais e configurações salvas anteriormente."""
        has_saved_planilha = False
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    if "planilha" in cfg and cfg["planilha"]:
                        self.entry_planilha.delete(0, "end")
                        self.entry_planilha.insert(0, cfg["planilha"])
                        has_saved_planilha = True
                    if "usuario" in cfg: self.entry_usuario.insert(0, cfg["usuario"])
                    if "senha" in cfg: self.entry_senha.insert(0, cfg["senha"])
                    if "disciplina" in cfg: self.entry_disciplina.insert(0, cfg["disciplina"])
                    if cfg.get("lembrar_dados", False): self.chk_save_credentials.select()
                    if cfg.get("lembrar_planilha", True):
                        self.chk_save_planilha.select()
                    else:
                        self.chk_save_planilha.deselect()
            except Exception:
                pass
        else:
            self.entry_planilha.insert(0, "https://docs.google.com/spreadsheets/d/1HR5X80eZIAwaoVR0WfwKxQQIRGlqF3bKXHWaN8ZD4AM/edit")
            self.entry_disciplina.insert(0, "065 - Programação em PYTHON")
            has_saved_planilha = True

        # Se houver uma planilha preenchida, carrega os dados automaticamente na inicialização
        if has_saved_planilha and self.entry_planilha.get().strip():
            self.after(500, self.load_spreadsheet_data)

    def save_config(self):
        """Salva a planilha e credenciais conforme os checkboxes selecionados."""
        cfg = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            except Exception:
                cfg = {}

        if self.chk_save_planilha.get():
            cfg["planilha"] = self.entry_planilha.get().strip()
            cfg["lembrar_planilha"] = True
        else:
            cfg["planilha"] = ""
            cfg["lembrar_planilha"] = False

        if self.chk_save_credentials.get():
            cfg["usuario"] = self.entry_usuario.get().strip()
            cfg["senha"] = self.entry_senha.get().strip()
            cfg["disciplina"] = self.entry_disciplina.get().strip()
            cfg["lembrar_dados"] = True
        else:
            cfg["usuario"] = ""
            cfg["senha"] = ""
            cfg["lembrar_dados"] = False

        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def start_automation(self):
        if self.is_running:
            messagebox.showwarning("Aviso", "A automação já está em execução!")
            return

        if not self.loaded_file_path or not self.dates_dict:
            messagebox.showerror("Atenção", "Por favor, clique primeiro no botão '🔍 Carregar Planilha' no Passo 1.")
            return

        usuario_val = self.entry_usuario.get().strip()
        senha_val = self.entry_senha.get().strip()
        turma_val = self.option_turma.get().strip()
        disciplina_val = self.entry_disciplina.get().strip()
        data_opcao_val = self.option_data.get().strip()

        if not usuario_val or not senha_val:
            messagebox.showerror("Erro", "Por favor, informe o Usuário e a Senha do portal SophiA.")
            return

        self.save_config()

        # Tratar seleção de data
        if "TODAS" in data_opcao_val:
            selected_dates = list(self.dates_dict.keys())
        else:
            data_limpa = data_opcao_val.split(" ")[0].strip()
            selected_dates = [data_limpa]

        self.is_running = True
        self.btn_iniciar.configure(state="disabled", text="⏳ PROCESSANDO CHAMADA...")
        self.progress_bar.set(0.1)
        self.log_text.delete("1.0", "end")
        self.log("🚀 Iniciando processo de automação de frequência...")

        thread = threading.Thread(
            target=self.run_background_task,
            args=(self.loaded_file_path, usuario_val, senha_val, turma_val, disciplina_val, selected_dates),
            daemon=True
        )
        thread.start()

    def run_background_task(self, file_path, usuario_val, senha_val, turma_val, disciplina_val, selected_dates):
        try:
            self.log(f"📅 Data(s) selecionada(s) para lançamento: {', '.join(selected_dates)}")
            self.log(f"👤 Usuário SophiA: {usuario_val}")
            self.log(f"🏫 Turma selecionada: {turma_val}")
            self.log(f"📚 Disciplina: {disciplina_val}")
            
            dry_run_flag = self.switch_dry_run.get() == 1
            headless_flag = not (self.chk_headful.get() == 1)

            self.log(f"⚙️ Modo: {'SIMULAÇÃO (sem salvar)' if dry_run_flag else 'OFICIAL (salvando no SophiA)'}")

            class ArgsMock:
                periodo = "2026.2"
                unidade = "Nova Iguaçu"
                turma = turma_val
                disciplina = disciplina_val
                planilha = file_path
                dry_run = dry_run_flag
                headless = headless_flag

            args = ArgsMock()

            # Garantir que o navegador Chromium do Playwright esteja instalado no computador
            try:
                import subprocess
                browsers_dir = os.environ.get('PLAYWRIGHT_BROWSERS_PATH', '')
                if not os.path.exists(browsers_dir) or not os.listdir(browsers_dir):
                    self.log("🌐 Baixando o navegador Chromium para o Playwright (apenas na 1ª execução)...")
                    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=False)
            except Exception as err_b:
                self.log(f"ℹ️ Verificação do navegador: {err_b}")

            self.log("\n🌐 Conectando ao Portal SophiA e iniciando navegação...")
            asyncio.run(run_automation(usuario_val, senha_val, self.dates_dict, selected_dates, args))

            self.log("\n✨ Processamento concluído com sucesso!")
            messagebox.showinfo("Sucesso", "Automação finalizada com sucesso!")

        except Exception as e:
            self.log(f"\n❌ ERRO DURANTE A EXECUÇÃO: {e}")
            messagebox.showerror("Erro na Automação", f"Ocorreu um erro:\n{e}")

        finally:
            self.is_running = False
            self.btn_iniciar.configure(state="normal", text="🚀 INICIAR LANÇAMENTO AUTOMÁTICO")

if __name__ == "__main__":
    app = SophiaApp()
    app.mainloop()
