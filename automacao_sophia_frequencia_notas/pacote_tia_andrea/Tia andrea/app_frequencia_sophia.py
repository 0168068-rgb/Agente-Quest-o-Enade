#!/usr/bin/env python3
"""
======================================================================
  🎓 AUTOMAÇÃO DE REGISTRO DE FREQUÊNCIA - PORTAL SOPHIA (UNIG / NEAD)
  Interface Gráfica Amigável (GUI) para Professores
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
        self.geometry("850x720")
        self.minsize(780, 650)

        self.msg_queue = queue.Queue()
        self.is_running = False

        self.create_widgets()
        self.load_saved_config()
        self.check_queue()

    def create_widgets(self):
        # Grid layout principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

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
            text="Faculdade UNIG / NEAD — Lançamento automático de presenças",
            font=ctk.CTkFont(size=12),
            text_color="#e0e0e0"
        )
        subtitle_label.pack(padx=20, pady=(0, 12))

        # ------------------------------------------------------------------
        # 2. FORMULÁRIO DE CONFIGURAÇÕES E CREDENCIAIS
        # ------------------------------------------------------------------
        form_frame = ctk.CTkFrame(self, corner_radius=10)
        form_frame.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        form_frame.grid_columnconfigure(1, weight=1)

        # Linha 1: Link da Planilha Google ou Arquivo Excel
        ctk.CTkLabel(form_frame, text="Planilha (Google Link ou Excel):", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=15, pady=8, sticky="w")
        
        input_file_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        input_file_frame.grid(row=0, column=1, padx=(0, 15), pady=8, sticky="ew")
        input_file_frame.grid_columnconfigure(0, weight=1)

        self.entry_planilha = ctk.CTkEntry(input_file_frame, placeholder_text="Cole o Link da Planilha do Google Drive ou escolha um arquivo Excel...")
        self.entry_planilha.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        btn_browse = ctk.CTkButton(input_file_frame, text="📁 Procurar", width=90, command=self.browse_file)
        btn_browse.grid(row=0, column=1, sticky="e")

        # Linha 2: Credenciais do SophiA
        ctk.CTkLabel(form_frame, text="Usuário SophiA:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=15, pady=8, sticky="w")
        self.entry_usuario = ctk.CTkEntry(form_frame, placeholder_text="Ex: prof.joao ou código de acesso")
        self.entry_usuario.grid(row=1, column=1, padx=(0, 15), pady=8, sticky="ew")

        ctk.CTkLabel(form_frame, text="Senha SophiA:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=15, pady=8, sticky="w")
        
        pass_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        pass_frame.grid(row=2, column=1, padx=(0, 15), pady=8, sticky="ew")
        pass_frame.grid_columnconfigure(0, weight=1)

        self.entry_senha = ctk.CTkEntry(pass_frame, show="•", placeholder_text="Sua senha de acesso ao portal")
        self.entry_senha.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.btn_show_pass = ctk.CTkButton(pass_frame, text="👁️", width=40, command=self.toggle_password)
        self.btn_show_pass.grid(row=0, column=1, sticky="e")

        # Linha 3: Turma e Disciplina
        ctk.CTkLabel(form_frame, text="Turma no SophiA:", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, padx=15, pady=8, sticky="w")
        self.entry_turma = ctk.CTkEntry(form_frame, placeholder_text="Ex: S - 2026.2.1P - Análise e Des. de Sistemas")
        self.entry_turma.grid(row=3, column=1, padx=(0, 15), pady=8, sticky="ew")

        ctk.CTkLabel(form_frame, text="Disciplina:", font=ctk.CTkFont(weight="bold")).grid(row=4, column=0, padx=15, pady=8, sticky="w")
        self.entry_disciplina = ctk.CTkEntry(form_frame, placeholder_text="Ex: 065 - Programação em PYTHON")
        self.entry_disciplina.grid(row=4, column=1, padx=(0, 15), pady=8, sticky="ew")

        # Linha 4: Data da Chamada e Modo
        ctk.CTkLabel(form_frame, text="Data(s) da Chamada:", font=ctk.CTkFont(weight="bold")).grid(row=5, column=0, padx=15, pady=8, sticky="w")
        
        options_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        options_frame.grid(row=5, column=1, padx=(0, 15), pady=8, sticky="ew")
        options_frame.grid_columnconfigure(0, weight=1)

        self.entry_data = ctk.CTkEntry(options_frame, placeholder_text="Deixe em branco para TODAS ou digite ex: 20/08/2026")
        self.entry_data.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.chk_save_credentials = ctk.CTkCheckBox(options_frame, text="Lembrar meus dados")
        self.chk_save_credentials.grid(row=0, column=1, sticky="e")

        # ------------------------------------------------------------------
        # 3. OPÇÕES DE NAVEGAÇÃO E BOTÃO DE AÇÃO
        # ------------------------------------------------------------------
        action_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        action_frame.grid(row=2, column=0, padx=15, pady=5, sticky="ew")
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
        # 4. ÁREA DE LOGS E BARRA DE PROGRESSO
        # ------------------------------------------------------------------
        log_frame = ctk.CTkFrame(self, corner_radius=10)
        log_frame.grid(row=3, column=0, padx=15, pady=(5, 15), sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)

        self.progress_bar = ctk.CTkProgressBar(log_frame)
        self.progress_bar.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="ew")
        self.progress_bar.set(0)

        self.log_text = ctk.CTkTextbox(log_frame, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_text.grid(row=1, column=0, padx=15, pady=(5, 15), sticky="nsew")

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
            
            # Atualiza barra de progresso em alguns eventos
            if "PROCESSANDO CHAMADA DO DIA" in msg:
                self.progress_bar.set(0.5)
            elif "Lançamento concluído com sucesso" in msg or "Processamento concluído" in msg:
                self.progress_bar.set(1.0)
                
        self.after(100, self.check_queue)

    def load_saved_config(self):
        """Carrega dados salvos anteriormente no arquivo de configuração."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    if "planilha" in cfg: self.entry_planilha.insert(0, cfg["planilha"])
                    if "usuario" in cfg: self.entry_usuario.insert(0, cfg["usuario"])
                    if "senha" in cfg: self.entry_senha.insert(0, cfg["senha"])
                    if "turma" in cfg: self.entry_turma.insert(0, cfg["turma"])
                    if "disciplina" in cfg: self.entry_disciplina.insert(0, cfg["disciplina"])
                    if cfg.get("lembrar", False): self.chk_save_credentials.select()
            except Exception:
                pass
        else:
            # Preenche valores padrão se não houver arquivo salvo
            self.entry_planilha.insert(0, "https://docs.google.com/spreadsheets/d/1HR5X80eZIAwaoVR0WfwKxQQIRGlqF3bKXHWaN8ZD4AM/edit")
            self.entry_turma.insert(0, "S - 2026.2.1P - Análise e Des. de Sistemas")
            self.entry_disciplina.insert(0, "065 - Programação em PYTHON")

    def save_config(self):
        """Salva as configurações se o checkbox 'Lembrar meus dados' estiver ativo."""
        if self.chk_save_credentials.get():
            cfg = {
                "planilha": self.entry_planilha.get().strip(),
                "usuario": self.entry_usuario.get().strip(),
                "senha": self.entry_senha.get().strip(),
                "turma": self.entry_turma.get().strip(),
                "disciplina": self.entry_disciplina.get().strip(),
                "lembrar": True
            }
            try:
                with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                    json.dump(cfg, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

    def start_automation(self):
        if self.is_running:
            messagebox.showwarning("Aviso", "A automação já está em execução!")
            return

        planilha_val = self.entry_planilha.get().strip()
        usuario_val = self.entry_usuario.get().strip()
        senha_val = self.entry_senha.get().strip()
        turma_val = self.entry_turma.get().strip()
        disciplina_val = self.entry_disciplina.get().strip()
        data_val = self.entry_data.get().strip()

        if not planilha_val:
            messagebox.showerror("Erro", "Por favor, informe a Planilha (Link do Google Drive ou caminho do arquivo Excel).")
            return
        if not usuario_val or not senha_val:
            messagebox.showerror("Erro", "Por favor, informe o Usuário e a Senha do portal SophiA.")
            return

        self.save_config()

        self.is_running = True
        self.btn_iniciar.configure(state="disabled", text="⏳ PROCESSANDO CHAMADA...")
        self.progress_bar.set(0.1)
        self.log_text.delete("1.0", "end")
        self.log("🚀 Iniciando processo de automação de frequência...")

        # Inicia a execução em uma thread de segundo plano
        thread = threading.Thread(
            target=self.run_background_task,
            args=(planilha_val, usuario_val, senha_val, turma_val, disciplina_val, data_val),
            daemon=True
        )
        thread.start()

    def run_background_task(self, planilha_val, usuario_val, senha_val, turma_val, disciplina_val, data_val):
        try:
            # 1. Tratar Link do Google Sheets ou Arquivo Local
            sheet_id = parse_google_sheet_id(planilha_val)
            if sheet_id:
                self.log(f"📥 Baixando planilha do Google Drive (ID: {sheet_id})...")
                file_path = download_google_sheet_as_excel(sheet_id)
                self.log("✅ Planilha do Google Sheets carregada com sucesso!")
            else:
                file_path = planilha_val
                if not os.path.exists(file_path):
                    raise Exception(f"O arquivo local não foi encontrado: {file_path}")

            # 2. Carregar dados da planilha
            self.log("📊 Analisando estrutura e presenças na planilha...")
            sheet_name, date_col, name_col = auto_detect_sheet_and_columns(file_path)
            dates_dict = load_dates_and_presents(file_path, sheet_name, date_col, name_col)

            if not dates_dict:
                raise Exception("Nenhum registro de presença válido foi encontrado na planilha.")

            # Filtrar datas
            if data_val:
                selected_dates = [d.strip() for d in data_val.split(',')]
            else:
                selected_dates = list(dates_dict.keys())

            self.log(f"📅 Datas identificadas para registro: {', '.join(selected_dates)}")
            self.log(f"👤 Usuário SophiA: {usuario_val}")
            self.log(f"🏫 Turma: {turma_val}")
            self.log(f"📚 Disciplina: {disciplina_val}")
            
            dry_run_flag = self.switch_dry_run.get() == 1
            headless_flag = not (self.chk_headful.get() == 1)

            self.log(f"⚙️ Modo: {'SIMULAÇÃO (sem salvar)' if dry_run_flag else 'OFICIAL (salvando no SophiA)'}")

            # Objeto mock de args para o backend
            class ArgsMock:
                periodo = "2026.2"
                unidade = "Nova Iguaçu"
                turma = turma_val
                disciplina = disciplina_val
                dry_run = dry_run_flag
                headless = headless_flag

            args = ArgsMock()

            # 3. Executar Automação com Playwright
            self.log("\n🌐 Abrindo navegador e conectando ao Portal SophiA...")
            asyncio.run(run_automation(usuario_val, senha_val, dates_dict, selected_dates, args))

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
