from __future__ import annotations

import asyncio
import os
import queue
import re
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from .data import Columns, detect_column, read_file, records_from_frame, suggest_grade_max
from .widgets import RoundedButton, RoundedCombobox, RoundedEntry, RoundedSurface


STAGE_HELP = {
    1: "Selecione a planilha que contém as notas a serem lançadas. Clique em Escolher arquivo e abra um CSV, XLSX ou XLS.",
    2: "Confira as colunas identificadas para aluno, curso, disciplina, nota, matrícula e polo. Se estiverem corretas, mantenha a seleção; caso contrário, escolha a coluna correspondente em cada campo.",
    3: "Clique nos cursos que deseja processar. Você pode marcar mais de um; clique novamente para desmarcar. A lista mostra somente os cursos presentes na planilha carregada.",
    4: "Escolha a prova, confira o período e a faixa de notas (0 a 10 ou 0 a 100). As notas serão enviadas como estão, sem divisão ou conversão de escala. Use Simulação para testar sem gravar.",
    5: "Escolha a pasta onde o relatório Excel será salvo, ou mantenha a pasta sugerida. Depois de conferir as etapas anteriores, clique em Iniciar.",
    6: "Faça login na janela do navegador quando solicitado e acompanhe as mensagens. Ao terminar, clique em Abrir relatório. Para interromper, use Cancelar; gravações já concluídas não são desfeitas.",
}


def documents_folder() -> Path:
    if sys.platform == "win32":
        import ctypes
        buffer = ctypes.create_unicode_buffer(260)
        if ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buffer) == 0:
            return Path(buffer.value)
    if sys.platform.startswith("linux"):
        try:
            value = subprocess.check_output(["xdg-user-dir", "DOCUMENTS"], text=True).strip()
            if value:
                return Path(value)
        except (OSError, subprocess.CalledProcessError):
            pass
    return Path.home() / "Documents"


class Application:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.frame = None
        self.busy = False
        self.close_when_done = False
        self.events = queue.Queue()
        self.cancel_event = threading.Event()
        self.last_report = None
        self.file = tk.StringVar()
        self.folder = tk.StringVar(value=str(documents_folder() / "Lançador de Notas SophiA"))
        self.exam = tk.StringVar(value="AD")
        self.period = tk.StringVar(value="2026.2")
        self.mode = tk.StringVar(value="simulacao")
        self.grade_range = tk.StringVar(value="0 a 10")
        self.state = tk.StringVar(value="Escolha uma planilha para começar.")
        self.guide_title = tk.StringVar(value="Etapa 1 • Planilha de notas")
        self.guide = tk.StringVar(value=STAGE_HELP[1])
        self.active_stage = 1
        self.columns = {key: tk.StringVar() for key in ("name", "course", "discipline", "grade", "registration", "unit")}
        self.editable = []
        root.title("Lançador de Notas SophiA")
        root.geometry(f"1080x{min(940, max(650, root.winfo_screenheight() - 90))}")
        root.minsize(860, 650)
        style = ttk.Style(root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TFrame", background="#f3f6f8")
        style.configure("TLabel", background="#f3f6f8", font=("Segoe UI", 10, "bold"))
        style.configure("TLabelframe", background="#f3f6f8")
        style.configure("TLabelframe.Label", font=("Segoe UI", 12, "bold"), foreground="#24556b")
        style.configure("TLabelframe", borderwidth=2, relief="groove")
        style.configure("TEntry", font=("Segoe UI", 10))
        style.configure("TCombobox", padding=5)
        style.layout("Rounded.TCombobox", [("Combobox.downarrow", {"side": "right", "sticky": "ns"}), ("Combobox.textarea", {"sticky": "nswe"})])
        style.configure("Rounded.TCombobox", fieldbackground="#ffffff", background="#ffffff", borderwidth=0, relief="flat", padding=0, arrowcolor="#24556b", font=("Segoe UI", 10))
        style.map("Rounded.TCombobox", fieldbackground=[("readonly", "#ffffff"), ("disabled", "#ffffff")], background=[("active", "#ffffff"), ("readonly", "#ffffff"), ("disabled", "#ffffff")])
        style.configure("TButton", padding=(12, 7), font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 21, "bold"), foreground="#24556b")
        style.configure("Credit.TLabel", font=("Segoe UI", 9, "bold"), foreground="#526c7b")
        style.configure("TRadiobutton", background="#f3f6f8", font=("Segoe UI", 10, "bold"))
        style.configure("Guide.TLabel", background="#e5eff4", foreground="#173e50", font=("Segoe UI", 10, "bold"))
        header = ttk.Frame(root, padding=(20, 16, 20, 8))
        header.pack(side="top", fill="x")
        ttk.Label(header, text="Lançador de Notas SophiA", style="Title.TLabel").pack(anchor="w")
        guide_panel = RoundedSurface(header, fill="#e5eff4", border="#d4e4ed", radius=22, padding=12)
        guide_panel.pack(fill="x", pady=(10, 0))
        ttk.Label(guide_panel, textvariable=self.guide_title, style="Guide.TLabel").pack(anchor="w")
        self.guide_label = ttk.Label(guide_panel, textvariable=self.guide, style="Guide.TLabel", wraplength=980, justify="left")
        self.guide_label.pack(anchor="w", pady=(4, 0))
        guide_panel.bind("<Configure>", lambda event: self.guide_label.configure(wraplength=max(200, event.width - 24)))

        # O formulário rola, mas as orientações e ações continuam visíveis.
        actions = ttk.Frame(root, padding=(20, 10, 20, 12))
        actions.pack(side="bottom", fill="x")
        viewport = ttk.Frame(root)
        viewport.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(viewport, background="#f3f6f8", highlightthickness=0)
        scrollbar = ttk.Scrollbar(viewport, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        body = ttk.Frame(self.canvas, padding=(20, 10, 20, 20))
        self.body = body
        self.body_window = self.canvas.create_window((0, 0), window=body, anchor="nw")
        body.bind("<Configure>", lambda _: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda event: self.canvas.itemconfigure(self.body_window, width=event.width))
        for event in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            root.bind(event, self.scroll_form, add="+")
        body.columnconfigure(0, weight=1)

        source = RoundedSurface(body, text="1. Planilha de notas", radius=24, padding=14)
        source.grid(row=2, column=0, sticky="ew")
        source.columnconfigure(0, weight=1)
        ttk.Label(source, text="Selecione a planilha com as notas a serem lançadas.").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        RoundedEntry(source, textvariable=self.file, state="readonly").grid(row=1, column=0, sticky="ew", padx=(0, 10))
        choose = RoundedButton(source, text="Escolher arquivo…", command=self.choose_file)
        choose.grid(row=1, column=1)
        self.editable.append((choose, "normal"))

        mapping = RoundedSurface(body, text="2. Colunas da planilha", radius=24, padding=14)
        mapping.grid(row=3, column=0, sticky="ew", pady=18)
        self.add_hint(mapping, "Confira as colunas detectadas. Ajuste apenas os campos que não correspondem à sua planilha.", 0, 6)
        self.combos = {}
        for idx, (key, label) in enumerate((("name", "Nome do aluno"), ("course", "Curso"), ("discipline", "Disciplina"), ("grade", "Nota"), ("registration", "RA / Matrícula (opcional)"), ("unit", "Polo / Unidade (opcional)"))):
            column, row = (idx % 3) * 2, idx // 3
            mapping.columnconfigure(column + 1, weight=1)
            ttk.Label(mapping, text=label).grid(row=row * 2 + 1, column=column, columnspan=2, sticky="w", pady=(0, 3))
            combo = RoundedCombobox(mapping, textvariable=self.columns[key], state="readonly", width=25)
            combo.grid(row=row * 2 + 2, column=column, columnspan=2, sticky="ew", padx=(0, 10), pady=(0, 7))
            self.combos[key] = combo
            self.editable.append((combo, "readonly"))
        self.combos["course"].bind("<<ComboboxSelected>>", lambda _: self.refresh_courses())
        self.combos["grade"].bind("<<ComboboxSelected>>", lambda _: self.detect_grade_range())

        choices = ttk.Frame(body)
        choices.grid(row=4, column=0, sticky="ew")
        choices.columnconfigure(0, weight=1)
        choices.columnconfigure(1, weight=1)
        courses = RoundedSurface(choices, text="3. Cursos (selecione um ou mais)", radius=24, padding=14)
        courses.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        courses.columnconfigure(0, weight=1)
        self.course_hint = tk.StringVar(value="Carregue uma planilha para ver os cursos disponíveis.")
        self.add_hint(courses, self.course_hint, 0, 2, variable=True)
        list_surface = RoundedSurface(courses, fill="#ffffff", radius=18, padding=10)
        list_surface.grid(row=1, column=0, columnspan=2, sticky="nsew")
        list_surface.columnconfigure(0, weight=1)
        self.course_list = tk.Listbox(list_surface, selectmode="multiple", exportselection=False, height=6, font=("Segoe UI", 10, "bold"), relief="flat", highlightthickness=0, bd=0, selectbackground="#24556b", selectforeground="#ffffff")
        self.course_list.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(list_surface, orient="vertical", command=self.course_list.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.course_list.configure(yscrollcommand=scroll.set)
        self.editable.append((self.course_list, "normal"))
        self.course_list.bind("<<ListboxSelect>>", lambda _: self.show_stage(3), add="+")
        controls = ttk.Frame(courses)
        controls.grid(row=2, column=0, sticky="w", pady=(5, 0))
        for label, action in (("Selecionar todos", lambda: self.select_courses(True)), ("Limpar seleção", lambda: self.select_courses(False))):
            button = RoundedButton(controls, text=label, command=action)
            button.pack(side="left", padx=(0, 5))
            self.editable.append((button, "normal"))

        options = RoundedSurface(choices, text="4. Avaliação e execução", radius=24, padding=14)
        options.grid(row=0, column=1, sticky="nsew")
        self.add_hint(options, "Confira prova, período e faixa. As notas serão mantidas, sem conversão. Use Simulação para testar.", 0, 2)
        ttk.Label(options, text="Avaliação").grid(row=1, column=0, sticky="w")
        exam = RoundedCombobox(options, textvariable=self.exam, values=("AD", "AI", "PS", "AE"), state="readonly", width=8)
        exam.grid(row=2, column=0, sticky="w", pady=(3, 10))
        exam.bind("<<ComboboxSelected>>", lambda _: self.detect_grade())
        ttk.Label(options, text="Período letivo").grid(row=1, column=1, sticky="w", padx=(20, 0))
        period = RoundedCombobox(options, textvariable=self.period, values=("2026.2",), width=16)
        period.grid(row=2, column=1, sticky="w", padx=(20, 0), pady=(3, 10))
        self.editable.extend(((exam, "readonly"), (period, "normal")))
        self.period_combo = period
        ttk.Label(options, text="Faixa de notas").grid(row=3, column=0, columnspan=2, sticky="w")
        self.grade_range_combo = RoundedCombobox(options, textvariable=self.grade_range, values=("0 a 10", "0 a 100"), state="readonly", width=12)
        self.grade_range_combo.grid(row=4, column=0, columnspan=2, sticky="w", pady=(3, 10))
        self.editable.append((self.grade_range_combo, "readonly"))
        for row, value, label in ((5, "simulacao", "Simulação — preenche sem gravar"), (6, "real", "Lançamento real — grava no portal")):
            radio = ttk.Radiobutton(options, variable=self.mode, value=value, text=label)
            radio.grid(row=row, column=0, columnspan=2, sticky="w", pady=3)
            self.editable.append((radio, "normal"))

        output = RoundedSurface(body, text="5. Pasta dos relatórios", radius=24, padding=14)
        output.grid(row=5, column=0, sticky="ew", pady=18)
        output.columnconfigure(0, weight=1)
        self.add_hint(output, "Escolha onde salvar o relatório, ou mantenha a pasta sugerida. Depois, clique em Iniciar.", 0, 2)
        folder = RoundedEntry(output, textvariable=self.folder)
        folder.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        folder_button = RoundedButton(output, text="Escolher pasta…", command=self.choose_folder)
        folder_button.grid(row=1, column=1)
        self.editable.extend(((folder, "normal"), (folder_button, "normal")))

        progress = RoundedSurface(body, text="6. Login, processamento e relatório", radius=24, padding=14)
        progress.grid(row=6, column=0, sticky="nsew")
        progress.columnconfigure(0, weight=1)
        self.add_hint(progress, "Faça login no navegador quando solicitado. Ao terminar, use Abrir relatório para conferir os resultados.", 0, 1)
        progress.rowconfigure(3, weight=1)
        self.status_label = ttk.Label(progress, textvariable=self.state, wraplength=900, justify="left")
        self.status_label.grid(row=1, column=0, sticky="w", pady=(0, 6))
        progress.bind("<Configure>", lambda event: self.status_label.configure(wraplength=max(200, event.width - 24)), add="+")
        self.progress = ttk.Progressbar(progress, mode="indeterminate")
        self.progress.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        log_surface = RoundedSurface(progress, fill="#ffffff", radius=18, padding=10)
        log_surface.grid(row=3, column=0, sticky="nsew")
        log_surface.columnconfigure(0, weight=1)
        self.log = ScrolledText(log_surface, height=7, font=("Consolas", 10), state="disabled", wrap="word", relief="flat", bd=0, highlightthickness=0)
        self.log.grid(row=0, column=0, sticky="nsew")
        self.start_button = RoundedButton(actions, text="Iniciar", command=self.start, state="disabled")
        self.start_button.pack(side="left")
        self.cancel_button = RoundedButton(actions, text="Cancelar", command=self.cancel, state="disabled")
        self.cancel_button.pack(side="left", padx=10)
        self.open_button = RoundedButton(actions, text="Abrir relatório", command=self.open_report, state="disabled")
        self.open_button.pack(side="right")
        self.credit_label = ttk.Label(actions, text="Criado por Hamilcar Silva", style="Credit.TLabel")
        self.credit_label.pack(side="left", expand=True, padx=12)
        self.sections = {1: source, 2: mapping, 3: courses, 4: options, 5: output, 6: progress}
        for number, group in self.sections.items():
            self.bind_stage(group, number)
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.after(100, self.poll)

    def add_hint(self, parent, text, row, span, variable=False):
        kwargs = {"textvariable" if variable else "text": text}
        label = ttk.Label(parent, justify="left", wraplength=900, **kwargs)
        label.grid(row=row, column=0, columnspan=span, sticky="ew", pady=(0, 9))
        parent.bind("<Configure>", lambda event: label.configure(wraplength=max(200, event.width - 24)), add="+")

    def bind_stage(self, widget, number):
        widget.bind("<FocusIn>", lambda _: self.show_stage(number), add="+")
        widget.bind("<Button-1>", lambda _: self.show_stage(number), add="+")
        if isinstance(widget, RoundedCombobox):
            for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                widget.bind(sequence, self.scroll_from_selector, add="+")
        if isinstance(widget, (RoundedEntry, RoundedCombobox)):
            return
        for child in widget.winfo_children():
            self.bind_stage(child, number)

    def show_stage(self, number, *, force=False):
        if self.busy and number != 6 and not force:
            return
        self.active_stage = number
        names = {1: "Planilha de notas", 2: "Colunas da planilha", 3: "Seleção dos cursos", 4: "Avaliação e execução", 5: "Pasta dos relatórios", 6: "Login, processamento e relatório"}
        self.guide_title.set(f"Etapa {number} • {names[number]}")
        text = STAGE_HELP[number]
        if number == 3 and self.frame is not None:
            total = self.course_list.size()
            selected = len(self.course_list.curselection())
            text += f" Disponíveis: {total}. Selecionados: {selected}."
        self.guide.set(text)
        self.root.after_idle(lambda: self.reveal_stage(number))

    def reveal_stage(self, number):
        if number != self.active_stage:
            return
        if not self.root.winfo_exists():
            return
        group = self.sections[number]
        top = group.winfo_y()
        parent = group.master
        while parent != self.body:
            top += parent.winfo_y()
            parent = parent.master
        height = max(1, self.body.winfo_height())
        visible_top = self.canvas.yview()[0] * height
        visible_bottom = visible_top + self.canvas.winfo_height()
        bottom = top + group.winfo_height()
        if top < visible_top or bottom > visible_bottom:
            self.canvas.yview_moveto(max(0, top - 12) / height)

    def scroll_from_selector(self, event):
        # A roda deve rolar o formulário, não trocar silenciosamente a
        # coluna Nota, o curso, a prova ou o modo de validação.
        self.scroll_form(event, from_selector=True)
        return "break"

    def scroll_form(self, event, *, from_selector=False):
        if not from_selector and isinstance(event.widget, (tk.Listbox, tk.Text, ttk.Combobox)):
            return  # Preservar a rolagem das listas e do acompanhamento.
        if self.body.winfo_height() <= self.canvas.winfo_height():
            return
        direction = -1 if getattr(event, "num", None) == 4 or getattr(event, "delta", 0) > 0 else 1
        self.canvas.yview_scroll(direction * 3, "units")
        return "break"

    def append_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def busy_state(self, busy):
        self.busy = busy
        for widget, state in self.editable:
            widget.configure(state="disabled" if busy else state)
        self.start_button.configure(state="disabled" if busy or self.frame is None else "normal")
        self.cancel_button.configure(state="normal" if busy else "disabled")
        self.open_button.configure(state="normal" if self.last_report and not busy else "disabled")
        if busy:
            self.progress.configure(mode="indeterminate")
            self.progress.start(12)
        else:
            self.progress.stop()

    def choose_file(self):
        self.show_stage(1)
        path = filedialog.askopenfilename(title="Escolha a planilha de notas", filetypes=[("Planilhas", "*.csv *.xlsx *.xls"), ("Todos os arquivos", "*.*")])
        if not path:
            return
        self.cancel_event.clear()
        self.busy_state(True)
        self.state.set("Carregando planilha…")
        def load():
            try:
                self.events.put(("loaded", path, read_file(Path(path))))
            except Exception as exc:
                self.events.put(("load_error", str(exc)))
        threading.Thread(target=load, daemon=True).start()

    def refresh_courses(self):
        previous_state = self.course_list.cget("state")
        # Tk ignora insert/delete em Listbox desabilitado. Durante a leitura
        # a lista fica bloqueada para o usuário, mas precisa aceitar os dados.
        self.course_list.configure(state="normal")
        try:
            self.course_list.delete(0, "end")
            if self.frame is not None and self.columns["course"].get() in self.frame.columns:
                for course in sorted({str(v).strip() for v in self.frame[self.columns["course"].get()].unique() if str(v).strip()}):
                    self.course_list.insert("end", course)
        finally:
            self.course_list.configure(state=previous_state)
        total = self.course_list.size()
        if self.frame is None:
            self.course_hint.set("Carregue uma planilha para ver os cursos disponíveis.")
        elif total == 0:
            self.course_hint.set("Nenhum curso encontrado. Confira a coluna Curso na etapa 2.")
        else:
            suffix = "curso disponível" if total == 1 else "cursos disponíveis"
            self.course_hint.set(f"{total} {suffix} nesta planilha. Clique nos nomes para marcar ou desmarcar.")

    def select_courses(self, select):
        if select:
            self.course_list.selection_set(0, "end")
        else:
            self.course_list.selection_clear(0, "end")
        self.show_stage(3)

    def detect_grade(self):
        if self.frame is not None:
            exam = self.exam.get()
            self.columns["grade"].set(detect_column(self.frame.columns, [exam, f"Nota {exam}", f"Nota_{exam}", "Nota"]))
            self.detect_grade_range()

    def detect_grade_range(self):
        column = self.columns["grade"].get()
        maximum = suggest_grade_max(self.frame[column]) if self.frame is not None and column in self.frame.columns else 10
        self.grade_range.set(f"0 a {maximum}")

    def choose_folder(self):
        self.show_stage(5)
        path = filedialog.askdirectory(title="Pasta dos relatórios")
        if path:
            self.folder.set(path)

    def start(self):
        if self.busy or self.frame is None:
            return
        try:
            columns = Columns(**{k: v.get() for k, v in self.columns.items()})
            courses = tuple(self.course_list.get(i) for i in self.course_list.curselection())
            if not courses:
                self.show_stage(3)
                raise ValueError("Na etapa 3, clique em pelo menos um curso para selecioná-lo.")
            records = records_from_frame(self.frame, columns, courses)
            if not self.period.get().strip() or not self.folder.get().strip():
                raise ValueError("Informe período e pasta dos relatórios.")
            from .engine import RunConfig, run
            config = RunConfig(self.period.get().strip(), self.exam.get(), courses, self.mode.get() != "real", Path(self.folder.get()).expanduser(), grade_max=100 if self.grade_range.get() == "0 a 100" else 10)
        except Exception as exc:
            if "coluna" in str(exc).lower():
                self.show_stage(2)
            messagebox.showerror("Confira a configuração", str(exc))
            return
        if not config.simulation and not messagebox.askyesno("Confirmar lançamento real", f"As notas serão gravadas no SophiA.\n\nArquivo: {self.file.get()}\nCursos: {', '.join(courses)}\nAvaliação: {config.exam}\nPeríodo: {config.period}\nFaixa: 0 a {config.grade_max} (sem conversão)\nRegistros: {len(records)}\n\nDeseja iniciar o lançamento real?", default="no"):
            return
        self.cancel_event.clear()
        self.busy_state(True)
        self.show_stage(6, force=True)
        self.state.set("Abrindo o navegador para login manual…")
        self.append_log(f"Início: {'SIMULAÇÃO — SEM GRAVAR' if config.simulation else 'LANÇAMENTO REAL'} | {config.period} | {config.exam} | {len(records)} registros")
        self.append_log(f"Faixa de notas: 0 a {config.grade_max}. Valores preservados, sem divisão ou conversão de escala.")
        self.append_log(f"Colunas: Nome={columns.name}; Curso={columns.course}; Disciplina={columns.discipline}; Nota={columns.grade}; RA={columns.registration or '(sem RA)'}; Polo={columns.unit or '(sem polo)'}. ")
        def worker():
            try:
                result = asyncio.run(run(config, records, self.cancel_event, lambda event: self.events.put(("event", event))))
                self.events.put(("done", result))
            except Exception as exc:
                self.events.put(("run_error", str(exc)))
        threading.Thread(target=worker, daemon=True).start()

    def cancel(self):
        self.cancel_event.set()
        self.cancel_button.configure(state="disabled")
        self.state.set("Cancelamento solicitado. Aguardando concluir a operação atual…")

    def poll(self):
        try:
            while True:
                event = self.events.get_nowait()
                kind = event[0]
                if kind == "loaded":
                    if not self.cancel_event.is_set():
                        self.file.set(event[1])
                        self.frame = event[2]
                        for key, keywords in {"name": ["Nome", "Aluno", "Estudante"], "course": ["CursoMatricula", "CursoTurma", "Curso"], "discipline": ["Disciplina", "Matéria", "Módulo"], "registration": ["RA", "Matrícula", "Código do aluno", "Codigo do aluno"], "unit": ["CampusPolo", "Polo", "Unidade", "Campus"]}.items():
                            self.columns[key].set(detect_column(self.frame.columns, keywords))
                        for combo in self.combos.values():
                            combo.configure(values=["", *self.frame.columns])
                        self.detect_grade()
                        self.refresh_courses()
                        periods = {self.period.get()}
                        period_column = detect_column(self.frame.columns, ["CodigoPeriodoLetivo", "Período letivo", "PeriodoLetivo"])
                        if period_column:
                            for value in self.frame[period_column].unique():
                                match = re.fullmatch(r"(\d{4})[.\-_]?([12])(?:_[A-Za-z]+)?", str(value).strip())
                                if match:
                                    periods.add(f"{match[1]}.{match[2]}")
                        self.period_combo.configure(values=sorted(periods, reverse=True))
                        self.state.set(f"Planilha carregada: {len(self.frame)} registros. Confira as colunas e selecione os cursos.")
                        self.append_log(self.state.get())
                        self.append_log(f"Faixa sugerida pela coluna Nota: {self.grade_range.get()}. Confira na etapa 4; os valores não serão convertidos.")
                        repaired = self.frame.attrs.get("csv_normalized_rows", [])
                        if repaired:
                            self.append_log(f"Exportação SophiA: {len(repaired)} linhas realinhadas para preservar disciplina, aluno, nota e polo. Confira as colunas antes de iniciar.")
                        self.show_stage(2, force=True)
                    else:
                        self.state.set("Carregamento cancelado.")
                        self.show_stage(1, force=True)
                    self.busy_state(False)
                elif kind in {"load_error", "run_error"}:
                    self.busy_state(False)
                    self.state.set("Processamento interrompido por erro.")
                    self.append_log(event[1])
                    self.show_stage(1 if kind == "load_error" else 6, force=True)
                    if not self.close_when_done:
                        messagebox.showerror("Erro", event[1])
                elif kind == "event":
                    payload = event[1]
                    self.state.set(payload["message"])
                    self.append_log(payload["message"])
                    if "total" in payload:
                        self.progress.stop()
                        self.progress.configure(mode="determinate", maximum=max(1, payload["total"]), value=payload.get("current", 0))
                elif kind == "done":
                    result = event[1]
                    self.last_report = result.path
                    self.busy_state(False)
                    text = f"{'Relatório parcial' if result.partial else 'Concluído'}: {len(result.results)} resultados, {len(result.pending)} pendências; {result.omitted} registros fora das disciplinas disponíveis."
                    self.state.set(text)
                    self.append_log(text + f"\nRelatório: {result.path}")
                    self.show_stage(6, force=True)
                    self.guide.set("O relatório foi salvo. Clique em Abrir relatório para conferir os resultados e as pendências. Para outra execução, revise as etapas e clique em Iniciar.")
                    if result.error and not self.close_when_done:
                        messagebox.showwarning("Processamento parcial", result.error + "\n\nO relatório parcial foi salvo.")
                if not self.busy and self.close_when_done:
                    self.root.destroy()
                    return
        except queue.Empty:
            pass
        self.root.after(100, self.poll)

    def open_report(self):
        if not self.last_report:
            return
        try:
            if sys.platform == "win32":
                os.startfile(str(self.last_report))
            else:
                subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", str(self.last_report)])
        except OSError as exc:
            messagebox.showerror("Abrir relatório", str(exc))

    def close(self):
        if self.busy:
            if not messagebox.askyesno("Encerrar", "Cancelar o processamento e fechar após salvar o relatório parcial? Gravações anteriores não serão desfeitas."):
                return
            self.close_when_done = True
            self.cancel()
        else:
            self.root.destroy()


def main():
    root = tk.Tk()
    Application(root)
    root.mainloop()
