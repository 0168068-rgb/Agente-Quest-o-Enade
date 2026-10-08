#!/usr/bin/env python3
"""
AVALIA AutoBatch Desktop App v5.1
=================================
Aplicativo Desktop para automação de cadastro em lote de questões no AVALIA (Grupo A).
"""

import sys
import os
import time
import json
import re
import threading
import subprocess
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from playwright.sync_api import sync_playwright

LOGIN_URL = "https://avauni.grupoa.education/plataforma/auth/signin"

# =============================================================================
# WIDGETS CUSTOMIZADOS COM CANTOS ARREDONDADOS E SOMBRAS 3D (IHC & USABILIDADE)
# =============================================================================

class RoundedCard(tk.Canvas):
    """Container estilo card com cantos arredondados (border-radius) e sombra projetada suave"""
    def __init__(self, parent, bg_color="#1e1e2e", border_color="#45475a", radius=14, shadow_offset=3, shadow_color="#08080c", padding=12, fit_height=True, **kwargs):
        super().__init__(parent, bg=parent['bg'] if hasattr(parent, '__getitem__') and 'bg' in parent.keys() else "#11111b", highlightthickness=0, bd=0, **kwargs)
        self.bg_color = bg_color
        self.border_color = border_color
        self.radius = radius
        self.shadow_offset = shadow_offset
        self.shadow_color = shadow_color
        self.padding = padding
        self.fit_height = fit_height
        
        self.inner = tk.Frame(self, bg=bg_color)
        self.win_id = self.create_window((padding, padding), window=self.inner, anchor="nw")
        
        self.bind("<Configure>", self._on_canvas_configure)
        self.inner.bind("<Configure>", self._on_inner_configure)

    def _on_inner_configure(self, event=None):
        if self.fit_height:
            req_h = self.inner.winfo_reqheight() + 2 * self.padding + self.shadow_offset
            if abs(self.winfo_height() - req_h) > 1:
                self.config(height=req_h)
        self._redraw()

    def _on_canvas_configure(self, event=None):
        self._redraw()

    def _redraw(self):
        self.delete("bg_shape")
        w = self.winfo_width()
        if w <= 1:
            try: w = int(self['width'])
            except Exception: w = self.winfo_reqwidth()
        h = self.winfo_height()
        if h <= 1:
            try: h = int(self['height'])
            except Exception: h = self.winfo_reqheight()

        r = self.radius
        so = self.shadow_offset
        if w <= 2*r or h <= 2*r:
            return

        if so > 0:
            self._draw_rounded_rect(so, so, w - 1, h - 1, r, fill=self.shadow_color, outline="", tag="bg_shape")

        w_card = w - so
        h_card = h - so
        self._draw_rounded_rect(0, 0, w_card, h_card, r, fill=self.bg_color, outline=self.border_color, width=1, tag="bg_shape")
        
        self.tag_raise(self.win_id)
        pad = self.padding
        inner_w = max(10, w_card - 2*pad)
        if self.fit_height:
            self.itemconfig(self.win_id, width=inner_w)
        else:
            inner_h = max(10, h_card - 2*pad)
            self.itemconfig(self.win_id, width=inner_w, height=inner_h)

    def _draw_rounded_rect(self, x1, y1, x2, y2, r, fill, outline="", width=1, tag="bg_shape"):
        w = x2 - x1
        h = y2 - y1
        if w < 2*r or h < 2*r:
            r = max(1, min(w//2, h//2))

        if fill:
            self.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, fill=fill, outline=fill, tags=tag)
            self.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, fill=fill, outline=fill, tags=tag)
            self.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, fill=fill, outline=fill, tags=tag)
            self.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, fill=fill, outline=fill, tags=tag)
            self.create_rectangle(x1+r, y1, x2-r, y2, fill=fill, outline=fill, tags=tag)
            self.create_rectangle(x1, y1+r, x2, y2-r, fill=fill, outline=fill, tags=tag)

        if outline:
            self.create_line(x1+r, y1, x2-r, y1, fill=outline, width=width, tags=tag)
            self.create_line(x1+r, y2, x2-r, y2, fill=outline, width=width, tags=tag)
            self.create_line(x1, y1+r, x1, y2-r, fill=outline, width=width, tags=tag)
            self.create_line(x2, y1+r, x2, y2-r, fill=outline, width=width, tags=tag)
            self.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, style="arc", outline=outline, width=width, tags=tag)
            self.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, style="arc", outline=outline, width=width, tags=tag)
            self.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, style="arc", outline=outline, width=width, tags=tag)
            self.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, style="arc", outline=outline, width=width, tags=tag)


class RoundedButton(tk.Canvas):
    """Botão moderno com cantos arredondados (border-radius), sombra projetada 3D e efeitos de pressão/hover"""
    def __init__(self, parent, text, command=None, bg_color="#89b4fa", fg_color="#11111b",
                 hover_bg="#b4befe", shadow_color="#08080c", radius=10, shadow_offset=3,
                 font=("Segoe UI", 10, "bold"), state="normal", height=36, width=180, **kwargs):
        super().__init__(parent, bg=parent['bg'] if hasattr(parent, '__getitem__') and 'bg' in parent.keys() else "#1e1e2e", highlightthickness=0, bd=0, height=height, width=width, **kwargs)
        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_bg = hover_bg
        self.shadow_color = shadow_color
        self.radius = radius
        self.base_shadow_offset = shadow_offset
        self.shadow_offset = shadow_offset
        self.font = font
        self.state = state
        self.current_bg = bg_color

        self.bind("<Configure>", self._redraw)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _redraw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        if w <= 1:
            try: w = int(self['width'])
            except Exception: w = 180
        h = self.winfo_height()
        if h <= 1:
            try: h = int(self['height'])
            except Exception: h = 36
        r = self.radius
        so = self.shadow_offset if self.state == "normal" else 1

        if self.state == "disabled":
            bg = "#45475a"
            fg = "#7f849c"
            sh = "#181825"
        else:
            bg = self.current_bg
            fg = self.fg_color
            sh = self.shadow_color

        if so > 0:
            self._draw_rounded_rect(so, so, w - 1, h - 1, r, fill=sh, outline="")

        w_b = w - so
        h_b = h - so
        self._draw_rounded_rect(0, 0, w_b, h_b, r, fill=bg, outline="")
        self.create_text(w_b / 2, h_b / 2, text=self.text, fill=fg, font=self.font)

    def _draw_rounded_rect(self, x1, y1, x2, y2, r, fill, outline="", width=1):
        w = x2 - x1
        h = y2 - y1
        if w < 2*r or h < 2*r:
            r = max(1, min(w//2, h//2))

        if fill:
            self.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, fill=fill, outline=fill)
            self.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, fill=fill, outline=fill)
            self.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, fill=fill, outline=fill)
            self.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, fill=fill, outline=fill)
            self.create_rectangle(x1+r, y1, x2-r, y2, fill=fill, outline=fill)
            self.create_rectangle(x1, y1+r, x2, y2-r, fill=fill, outline=fill)

        if outline:
            self.create_line(x1+r, y1, x2-r, y1, fill=outline, width=width)
            self.create_line(x1+r, y2, x2-r, y2, fill=outline, width=width)
            self.create_line(x1, y1+r, x1, y2-r, fill=outline, width=width)
            self.create_line(x2, y1+r, x2, y2-r, fill=outline, width=width)
            self.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, style="arc", outline=outline, width=width)
            self.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, style="arc", outline=outline, width=width)
            self.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, style="arc", outline=outline, width=width)
            self.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, style="arc", outline=outline, width=width)

    def _on_enter(self, e):
        if self.state == "normal":
            self.current_bg = self.hover_bg
            self._redraw()

    def _on_leave(self, e):
        if self.state == "normal":
            self.current_bg = self.bg_color
            self._redraw()

    def _on_press(self, e):
        if self.state == "normal":
            self.shadow_offset = 1
            self._redraw()

    def _on_release(self, e):
        if self.state == "normal":
            self.shadow_offset = self.base_shadow_offset
            self._redraw()
            if self.command:
                self.command()

    def config_state(self, new_state):
        self.state = new_state
        self._redraw()

    def config(self, **kwargs):
        if "state" in kwargs:
            self.config_state(kwargs["state"])


class RoundedInput(tk.Canvas):
    """Caixa de entrada com cantos arredondados (border-radius) e efeito de foco"""
    def __init__(self, parent, bg_color="#313244", fg_color="#cdd6f4", border_color="#45475a", focus_color="#89b4fa", radius=10, font=("Segoe UI", 10), height=38, **kwargs):
        super().__init__(parent, bg=parent['bg'] if hasattr(parent, '__getitem__') and 'bg' in parent.keys() else "#1e1e2e", highlightthickness=0, bd=0, height=height, **kwargs)
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.border_color = border_color
        self.focus_color = focus_color
        self.radius = radius
        self.current_border = border_color

        self.entry = tk.Entry(self, bg=bg_color, fg=fg_color, insertbackground=fg_color, font=font, relief="flat", bd=0)
        self.win_id = self.create_window((12, height/2), window=self.entry, anchor="w")
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.bind("<Configure>", self._redraw)

    def _redraw(self, event=None):
        tk.Canvas.delete(self, "bg_shape")
        w = self.winfo_width()
        if w <= 1:
            try: w = int(self['width'])
            except Exception: w = 300
        h = self.winfo_height()
        if h <= 1:
            try: h = int(self['height'])
            except Exception: h = 36
        r = self.radius

        if w <= 2*r or h <= 2*r: return

        self._draw_rounded_rect(0, 0, w - 1, h - 1, r, fill=self.bg_color, outline=self.current_border, width=1, tag="bg_shape")
        self.tag_raise(self.win_id)
        self.coords(self.win_id, 12, h/2)
        self.itemconfig(self.win_id, width=max(10, w - 24))

    def _draw_rounded_rect(self, x1, y1, x2, y2, r, fill, outline="", width=1, tag="bg_shape"):
        w = x2 - x1
        h = y2 - y1
        if w < 2*r or h < 2*r:
            r = max(1, min(w//2, h//2))

        if fill:
            self.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, fill=fill, outline=fill, tags=tag)
            self.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, fill=fill, outline=fill, tags=tag)
            self.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, fill=fill, outline=fill, tags=tag)
            self.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, fill=fill, outline=fill, tags=tag)
            self.create_rectangle(x1+r, y1, x2-r, y2, fill=fill, outline=fill, tags=tag)
            self.create_rectangle(x1, y1+r, x2, y2-r, fill=fill, outline=fill, tags=tag)

        if outline:
            self.create_line(x1+r, y1, x2-r, y1, fill=outline, width=width, tags=tag)
            self.create_line(x1+r, y2, x2-r, y2, fill=outline, width=width, tags=tag)
            self.create_line(x1, y1+r, x1, y2-r, fill=outline, width=width, tags=tag)
            self.create_line(x2, y1+r, x2, y2-r, fill=outline, width=width, tags=tag)
            self.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, style="arc", outline=outline, width=width, tags=tag)
            self.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, style="arc", outline=outline, width=width, tags=tag)
            self.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, style="arc", outline=outline, width=width, tags=tag)
            self.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, style="arc", outline=outline, width=width, tags=tag)

    def _on_focus_in(self, e):
        self.current_border = self.focus_color
        self._redraw()

    def _on_focus_out(self, e):
        self.current_border = self.border_color
        self._redraw()

    def get(self): return self.entry.get()
    def delete(self, first, last=None): self.entry.delete(first, last)
    def insert(self, index, string): self.entry.insert(index, string)
    def config(self, **kwargs): self.entry.config(**kwargs)


class RoundedBadge(tk.Canvas):
    """Badge de status com cantos arredondados"""
    def __init__(self, parent, text="", bg_color="#313244", fg_color="#f9e2af", radius=10, font=("Segoe UI", 9, "bold"), height=30, width=170, **kwargs):
        super().__init__(parent, bg=parent['bg'] if hasattr(parent, '__getitem__') and 'bg' in parent.keys() else "#11111b", highlightthickness=0, bd=0, height=height, width=width, **kwargs)
        self.text = text
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.radius = radius
        self.font = font
        self.bind("<Configure>", self._redraw)

    def _redraw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        if w <= 1:
            try: w = int(self['width'])
            except Exception: w = 170
        h = self.winfo_height()
        if h <= 1:
            try: h = int(self['height'])
            except Exception: h = 30
        r = self.radius

        self._draw_rounded_rect(0, 0, w - 1, h - 1, r, fill=self.bg_color, outline="")
        self.create_text(w/2, h/2, text=self.text, fill=self.fg_color, font=self.font)

    def _draw_rounded_rect(self, x1, y1, x2, y2, r, fill, outline="", width=1):
        w = x2 - x1
        h = y2 - y1
        if w < 2*r or h < 2*r:
            r = max(1, min(w//2, h//2))

        if fill:
            self.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, fill=fill, outline=fill)
            self.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, fill=fill, outline=fill)
            self.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, fill=fill, outline=fill)
            self.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, fill=fill, outline=fill)
            self.create_rectangle(x1+r, y1, x2-r, y2, fill=fill, outline=fill)
            self.create_rectangle(x1, y1+r, x2, y2-r, fill=fill, outline=fill)

        if outline:
            self.create_line(x1+r, y1, x2-r, y1, fill=outline, width=width)
            self.create_line(x1+r, y2, x2-r, y2, fill=outline, width=width)
            self.create_line(x1, y1+r, x1, y2-r, fill=outline, width=width)
            self.create_line(x2, y1+r, x2, y2-r, fill=outline, width=width)
            self.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, style="arc", outline=outline, width=width)
            self.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, style="arc", outline=outline, width=width)
            self.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, style="arc", outline=outline, width=width)
            self.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, style="arc", outline=outline, width=width)

    def config_badge(self, text, bg_color, fg_color):
        self.text = text
        self.bg_color = bg_color
        self.fg_color = fg_color
        self._redraw()


class AvaliaIHCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AVALIA AutoBatch — Automação de Questões em Lote")
        self.root.geometry("920x760")
        self.root.minsize(880, 680)
        self.root.configure(bg="#11111b")

        self.selected_excel = ""
        self.is_running = False
        self.should_stop = False

        self.setup_styles()
        self.build_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Palette Catppuccin Mocha / Dark Mode
        self.BG_MAIN = "#11111b"
        self.BG_CARD = "#1e1e2e"
        self.BG_INPUT = "#313244"
        self.BORDER_CARD = "#45475a"
        self.SHADOW_COLOR = "#08080c"
        self.ACCENT_BLUE = "#89b4fa"
        self.ACCENT_GREEN = "#a6e3a1"
        self.ACCENT_RED = "#f38ba8"
        self.ACCENT_YELLOW = "#f9e2af"
        self.TEXT_PRIMARY = "#cdd6f4"
        self.TEXT_MUTED = "#a6adc8"

        style.configure(".", background=self.BG_MAIN, foreground=self.TEXT_PRIMARY, font=("Segoe UI", 10))
        style.configure("TLabel", background=self.BG_MAIN, foreground=self.TEXT_PRIMARY)
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), foreground=self.ACCENT_BLUE, background=self.BG_MAIN)
        style.configure("CardTitle.TLabel", font=("Segoe UI", 11, "bold"), foreground=self.ACCENT_BLUE, background=self.BG_CARD)

        # Progressbar
        style.configure("TProgressbar", thickness=18, troughcolor=self.BG_INPUT, background=self.ACCENT_GREEN)

    def build_ui(self):
        # 1. Header Principal com Crédito do Autor
        header_frame = ttk.Frame(self.root, padding=(20, 12))
        header_frame.pack(fill="x")

        title_box = ttk.Frame(header_frame)
        title_box.pack(side="left")

        lbl_title = ttk.Label(title_box, text="⚡ AVALIA AutoBatch Desktop", style="Title.TLabel")
        lbl_title.pack(anchor="w")

        lbl_subtitle = ttk.Label(title_box, text="Criado por Hamilcar Silva", font=("Segoe UI", 10, "bold"), foreground=self.ACCENT_GREEN)
        lbl_subtitle.pack(anchor="w")

        # Status Badge Superior com Cantos Arredondados
        self.lbl_badge = RoundedBadge(header_frame, text="🟡 AGUARDANDO ETAPA 4", bg_color="#313244", fg_color=self.ACCENT_YELLOW, radius=12, width=190, height=32)
        self.lbl_badge.pack(side="right")

        # Divisor
        ttk.Separator(self.root, orient="horizontal").pack(fill="x", padx=20)

        # Rodapé com Crédito de Autoria
        footer_frame = ttk.Frame(self.root, padding=(20, 6))
        footer_frame.pack(fill="x", side="bottom")

        lbl_author = ttk.Label(footer_frame, text="Criado por Hamilcar Silva — Automação AVALIA v5.1", font=("Segoe UI", 9, "bold"), foreground=self.ACCENT_BLUE)
        lbl_author.pack(side="left")

        lbl_footer_right = ttk.Label(footer_frame, text="Interface projetada sob Metas de Usabilidade e IHC", font=("Segoe UI", 9, "italic"), foreground=self.TEXT_MUTED)
        lbl_footer_right.pack(side="right")

        # Container Principal
        content = tk.Frame(self.root, bg=self.BG_MAIN)
        content.pack(fill="both", expand=True, padx=20, pady=15)

        # PASSO 1: CONEXÃO E CONFIRMAÇÃO DA ETAPA 4 (Card com Cantos Arredondados e Sombra)
        card1 = RoundedCard(content, bg_color=self.BG_CARD, border_color=self.BORDER_CARD, radius=14, shadow_offset=3, padding=12, fit_height=True)
        card1.pack(fill="x", pady=(0, 10))

        lbl_step1 = ttk.Label(card1.inner, text="📌 Passo 1 — Conexão com o Navegador e Confirmação da Etapa 4", style="CardTitle.TLabel")
        lbl_step1.pack(anchor="w", pady=(0, 6))

        step1_desc = ttk.Label(card1.inner, text="Faça login no Avalia no Chrome que foi aberto e siga para o passo 4 (tela de inserção de questão) da disciplina das questões a serem inseridas.", font=("Segoe UI", 10), foreground=self.TEXT_PRIMARY, background=self.BG_CARD, wraplength=820, justify="left")
        step1_desc.pack(anchor="w", pady=(0, 8))

        step1_controls = tk.Frame(card1.inner, bg=self.BG_CARD)
        step1_controls.pack(fill="x")

        btn_chrome = RoundedButton(step1_controls, text="🌐 Abrir Chrome AVALIA", command=self.open_chrome, bg_color=self.BG_INPUT, fg_color=self.TEXT_PRIMARY, hover_bg="#45475a", radius=10, shadow_offset=3, width=180, height=36)
        btn_chrome.pack(side="left", padx=(0, 10))

        btn_assistant = RoundedButton(step1_controls, text="💡 Passo a Passo", command=self.show_guide_step1, bg_color="#f9e2af", fg_color="#11111b", hover_bg="#fab387", radius=10, shadow_offset=3, width=140, height=36)
        btn_assistant.pack(side="left", padx=(0, 10))

        btn_guide = RoundedButton(step1_controls, text="📖 Roteiro Doc", command=self.open_guide, bg_color=self.BG_INPUT, fg_color=self.TEXT_PRIMARY, hover_bg="#45475a", radius=10, shadow_offset=3, width=140, height=36)
        btn_guide.pack(side="left", padx=(0, 15))

        # Interação para confirmação do usuário se já está no Passo 4
        self.var_step4_confirmed = tk.BooleanVar(value=False)
        chk_step4 = tk.Checkbutton(
            step1_controls, 
            text="☑️ Confirmo que já naveguei até o Passo 4 (Inserção de Questão) no Chrome", 
            variable=self.var_step4_confirmed, 
            bg=self.BG_CARD, 
            fg=self.ACCENT_GREEN, 
            activebackground=self.BG_CARD, 
            activeforeground=self.ACCENT_GREEN, 
            selectcolor=self.BG_INPUT, 
            font=("Segoe UI", 10, "bold"),
            command=self.on_step4_toggle
        )
        chk_step4.pack(side="left", pady=2)

        # PASSO 2: SELEÇÃO E MODELO DA PLANILHA EXCEL (Caixa de Entrada com Cantos Arredondados)
        card2 = RoundedCard(content, bg_color=self.BG_CARD, border_color=self.BORDER_CARD, radius=14, shadow_offset=3, padding=12, fit_height=True)
        card2.pack(fill="x", pady=(0, 10))

        lbl_step2 = ttk.Label(card2.inner, text="📌 Passo 2 — Carregar Planilha de Questões & Modelo Exemplo", style="CardTitle.TLabel")
        lbl_step2.pack(anchor="w", pady=(0, 6))

        step2_top = tk.Frame(card2.inner, bg=self.BG_CARD)
        step2_top.pack(fill="x", pady=(0, 6))

        # Caixa de Entrada com Cantos Arredondados
        self.entry_path = RoundedInput(step2_top, bg_color=self.BG_INPUT, fg_color=self.TEXT_PRIMARY, radius=10, height=36)
        self.entry_path.pack(side="left", fill="x", expand=True, padx=(0, 10))

        btn_browse = RoundedButton(step2_top, text="📂 Escolher Excel...", command=self.browse_excel, bg_color=self.BG_INPUT, fg_color=self.TEXT_PRIMARY, hover_bg="#45475a", radius=10, shadow_offset=3, width=150, height=36)
        btn_browse.pack(side="right")

        step2_bottom = tk.Frame(card2.inner, bg=self.BG_CARD)
        step2_bottom.pack(fill="x", pady=(2, 0))

        self.lbl_excel_validation = ttk.Label(step2_bottom, text="Nenhuma planilha carregada.", font=("Segoe UI", 9, "italic"), foreground=self.TEXT_MUTED, background=self.BG_CARD)
        self.lbl_excel_validation.pack(side="left", pady=2)

        # Botão com Sombra para baixar Modelo Exemplo
        btn_download_template = RoundedButton(step2_bottom, text="📥 Baixar Modelo de Planilha Exemplo (.xlsx)", command=self.download_template, bg_color="#fab387", fg_color="#11111b", hover_bg="#f9e2af", radius=10, shadow_offset=3, width=310, height=34)
        btn_download_template.pack(side="right")

        # PASSO 3: EXECUÇÃO & PAUSA (Botões com Sombra Projetada 3D)
        card3 = RoundedCard(content, bg_color=self.BG_CARD, border_color=self.BORDER_CARD, radius=14, shadow_offset=3, padding=12, fit_height=True)
        card3.pack(fill="x", pady=(0, 10))

        lbl_step3 = ttk.Label(card3.inner, text="📌 Passo 3 — Execução da Automação em Lote", style="CardTitle.TLabel")
        lbl_step3.pack(anchor="w", pady=(0, 6))

        btn_box = tk.Frame(card3.inner, bg=self.BG_CARD)
        btn_box.pack(fill="x", pady=(0, 8))

        self.btn_start = RoundedButton(btn_box, text="🚀 INICIAR INSERÇÃO EM LOTE", command=self.start_automation, bg_color=self.ACCENT_BLUE, fg_color="#11111b", hover_bg="#b4befe", radius=12, shadow_offset=3, font=("Segoe UI", 11, "bold"), width=320, height=40)
        self.btn_start.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.btn_stop = RoundedButton(btn_box, text="⏹️ PAUSAR/PARAR", command=self.stop_automation, bg_color=self.ACCENT_RED, fg_color="#11111b", hover_bg="#f5e0dc", radius=12, shadow_offset=3, font=("Segoe UI", 10, "bold"), state="disabled", width=160, height=40)
        self.btn_stop.pack(side="right")

        self.progress = ttk.Progressbar(card3.inner, mode="determinate")
        self.progress.pack(fill="x", pady=(0, 5))

        self.lbl_status = ttk.Label(card3.inner, text="Aguardando confirmação do Passo 4...", font=("Segoe UI", 9, "bold"), foreground=self.ACCENT_YELLOW, background=self.BG_CARD)
        self.lbl_status.pack(anchor="w")

        # CONSOLE DE LOGS EM TEMPO REAL (Card Arredondado com Sombra)
        card_log = RoundedCard(content, bg_color=self.BG_CARD, border_color=self.BORDER_CARD, radius=14, shadow_offset=3, padding=12, fit_height=False)
        card_log.pack(fill="both", expand=True)

        lbl_log = ttk.Label(card_log.inner, text="📋 Console de Logs & Relatório em Tempo Real", style="CardTitle.TLabel")
        lbl_log.pack(anchor="w", pady=(0, 8))

        log_container = tk.Frame(card_log.inner, bg=self.BG_CARD)
        log_container.pack(fill="both", expand=True)

        log_frame = tk.Frame(log_container, bg="#0d0e15")
        log_frame.pack(fill="both", expand=True, side="left")

        self.txt_log = tk.Text(log_frame, bg="#0d0e15", fg="#a6e3a1", insertbackground="#cdd6f4", font=("Consolas", 9), wrap="word", relief="flat", bd=0)
        self.txt_log.pack(fill="both", expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(log_container, command=self.txt_log.yview)
        scrollbar.pack(side="right", fill="y")
        self.txt_log.config(yscrollcommand=scrollbar.set)

    def on_step4_toggle(self):
        if self.var_step4_confirmed.get():
            self.set_badge("🟢 PRONTO NA ETAPA 4", self.BG_INPUT, self.ACCENT_GREEN)
            self.lbl_status.config(text="Confirmação recebida! Pronto para carregar planilha e iniciar.", foreground=self.ACCENT_GREEN)
            self.log("✅ Usuário confirmou que o Chrome está posicionado na Etapa 4 de Inserção de Questão.")
            self.show_guide_step2()
        else:
            self.set_badge("🟡 AGUARDANDO ETAPA 4", self.BG_INPUT, self.ACCENT_YELLOW)
            self.lbl_status.config(text="Aguardando confirmação do Passo 4...", foreground=self.ACCENT_YELLOW)

    def _center_modal(self, dlg, width, height):
        dlg.update_idletasks()
        rx = self.root.winfo_x()
        ry = self.root.winfo_y()
        rw = self.root.winfo_width()
        rh = self.root.winfo_height()
        x = max(0, rx + (rw - width) // 2)
        y = max(0, ry + (rh - height) // 2)
        dlg.geometry(f"{width}x{height}+{x}+{y}")

    def show_guide_step1(self):
        """Janela orientativa para o Passo 1"""
        dlg = tk.Toplevel(self.root)
        dlg.title("💡 Orientação — Passo 1: Navegador e Login")
        dlg.configure(bg=self.BG_CARD)
        dlg.transient(self.root)
        self._center_modal(dlg, 560, 380)

        hdr = tk.Frame(dlg, bg="#181825", padx=20, pady=14)
        hdr.pack(fill="x")
        lbl_h = tk.Label(hdr, text="1️⃣ Passo 1: Abrir Chrome e Navegar no AVALIA", font=("Segoe UI", 12, "bold"), fg=self.ACCENT_BLUE, bg="#181825")
        lbl_h.pack(anchor="w")

        body = tk.Frame(dlg, bg=self.BG_CARD, padx=22, pady=18)
        body.pack(fill="both", expand=True)

        msg_text = (
            "Siga os passos abaixo para preparar a automação:\n\n"
            "1. Clique no botão '🌐 Abrir Chrome AVALIA'.\n"
            "2. Faça o seu login com usuário e senha no sistema AVALIA.\n"
            "3. Navegue na disciplina até o PASSO 4 (tela de Inserção de Questão).\n"
            "4. Marque a caixa de verificação no aplicativo:\n"
            "   '☑️ Confirmo que já naveguei até o Passo 4 (Inserção de Questão)'."
        )
        lbl_body = tk.Label(body, text=msg_text, font=("Segoe UI", 10), fg=self.TEXT_PRIMARY, bg=self.BG_CARD, justify="left", wraplength=510)
        lbl_body.pack(anchor="w", pady=(0, 20))

        btn_box = tk.Frame(body, bg=self.BG_CARD)
        btn_box.pack(fill="x", side="bottom")

        btn_close = tk.Button(btn_box, text="Fechar", command=dlg.destroy, font=("Segoe UI", 10), bg=self.BG_INPUT, fg=self.TEXT_PRIMARY, activebackground="#45475a", activeforeground=self.TEXT_PRIMARY, relief="flat", padx=15, pady=6, cursor="hand2")
        btn_close.pack(side="left")

        btn_ok = tk.Button(btn_box, text="🌐 Abrir Chrome Agora", command=lambda: [dlg.destroy(), self.open_chrome()], font=("Segoe UI", 10, "bold"), bg=self.ACCENT_BLUE, fg="#11111b", activebackground="#b4befe", activeforeground="#11111b", relief="flat", padx=20, pady=6, cursor="hand2")
        btn_ok.pack(side="right")

        dlg.update_idletasks()
        dlg.grab_set()

    def show_guide_step2(self):
        """Janela orientativa para o Passo 2 — Seleção da Planilha Excel"""
        dlg = tk.Toplevel(self.root)
        dlg.title("💡 Orientação — Passo 2: Seleção da Planilha Excel")
        dlg.configure(bg=self.BG_CARD)
        dlg.transient(self.root)
        self._center_modal(dlg, 560, 360)

        hdr = tk.Frame(dlg, bg="#181825", padx=20, pady=14)
        hdr.pack(fill="x")
        lbl_h = tk.Label(hdr, text="2️⃣ Passo 2: Carregar Planilha de Questões", font=("Segoe UI", 12, "bold"), fg=self.ACCENT_GREEN, bg="#181825")
        lbl_h.pack(anchor="w")

        body = tk.Frame(dlg, bg=self.BG_CARD, padx=22, pady=18)
        body.pack(fill="both", expand=True)

        msg_text = (
            "Excelente! Você confirmou que o Chrome está na Etapa 4.\n\n"
            "Agora siga a próxima etapa:\n\n"
            "1. Clique no botão '📂 Escolher Excel...' para carregar a planilha com as questões.\n"
            "2. O sistema fará a leitura automática e exibirá o total de questões detectadas."
        )
        lbl_body = tk.Label(body, text=msg_text, font=("Segoe UI", 10), fg=self.TEXT_PRIMARY, bg=self.BG_CARD, justify="left", wraplength=510)
        lbl_body.pack(anchor="w", pady=(0, 20))

        btn_box = tk.Frame(body, bg=self.BG_CARD)
        btn_box.pack(fill="x", side="bottom")

        btn_close = tk.Button(btn_box, text="Fechar", command=dlg.destroy, font=("Segoe UI", 10), bg=self.BG_INPUT, fg=self.TEXT_PRIMARY, activebackground="#45475a", activeforeground=self.TEXT_PRIMARY, relief="flat", padx=15, pady=6, cursor="hand2")
        btn_close.pack(side="left")

        btn_ok = tk.Button(btn_box, text="📂 Escolher Excel...", command=lambda: [dlg.destroy(), self.browse_excel()], font=("Segoe UI", 10, "bold"), bg=self.ACCENT_GREEN, fg="#11111b", activebackground="#a6e3a1", activeforeground="#11111b", relief="flat", padx=20, pady=6, cursor="hand2")
        btn_ok.pack(side="right")

        dlg.update_idletasks()
        dlg.grab_set()

    def show_guide_step3(self, rows, filename):
        """Janela orientativa para o Passo 3 — Conferência e Início em Lote"""
        dlg = tk.Toplevel(self.root)
        dlg.title("💡 Orientação — Passo 3: Iniciar Inserção em Lote")
        dlg.configure(bg=self.BG_CARD)
        dlg.transient(self.root)
        self._center_modal(dlg, 580, 410)

        hdr = tk.Frame(dlg, bg="#181825", padx=20, pady=14)
        hdr.pack(fill="x")
        lbl_h = tk.Label(hdr, text="3️⃣ Passo 3: Conferência de Questões e Início da Automação", font=("Segoe UI", 12, "bold"), fg=self.ACCENT_GREEN, bg="#181825")
        lbl_h.pack(anchor="w")

        body = tk.Frame(dlg, bg=self.BG_CARD, padx=22, pady=18)
        body.pack(fill="both", expand=True)

        info_card = tk.Frame(body, bg="#11111b", highlightbackground=self.BORDER_CARD, highlightthickness=1, padx=14, pady=12)
        info_card.pack(fill="x", pady=(0, 15))

        lbl_f = tk.Label(info_card, text=f"📁 Planilha Carregada: {filename}", font=("Segoe UI", 10, "bold"), fg=self.TEXT_PRIMARY, bg="#11111b", anchor="w")
        lbl_f.pack(fill="x", pady=2)

        lbl_q = tk.Label(info_card, text=f"📊 Total Detectado: {rows} questões válidas a serem inseridas", font=("Segoe UI", 10, "bold"), fg=self.ACCENT_GREEN, bg="#11111b", anchor="w")
        lbl_q.pack(fill="x", pady=2)

        msg_text = (
            f"Confira a quantidade acima ({rows} questões na planilha).\n\n"
            f"Se a quantidade estiver correta, basta clicar no botão abaixo '🚀 INICIAR INSERÇÃO EM LOTE' para que o robô faça a inserção automática de todas as {rows} questões no AVALIA!"
        )
        lbl_body = tk.Label(body, text=msg_text, font=("Segoe UI", 10), fg=self.TEXT_PRIMARY, bg=self.BG_CARD, justify="left", wraplength=530)
        lbl_body.pack(anchor="w", pady=(0, 18))

        btn_box = tk.Frame(body, bg=self.BG_CARD)
        btn_box.pack(fill="x", side="bottom")

        btn_close = tk.Button(btn_box, text="Fechar", command=dlg.destroy, font=("Segoe UI", 10), bg=self.BG_INPUT, fg=self.TEXT_PRIMARY, activebackground="#45475a", activeforeground=self.TEXT_PRIMARY, relief="flat", padx=15, pady=6, cursor="hand2")
        btn_close.pack(side="left")

        btn_ok = tk.Button(btn_box, text="🚀 INICIAR INSERÇÃO EM LOTE", command=lambda: [dlg.destroy(), self.start_automation()], font=("Segoe UI", 10, "bold"), bg=self.ACCENT_BLUE, fg="#11111b", activebackground="#b4befe", activeforeground="#11111b", relief="flat", padx=20, pady=6, cursor="hand2")
        btn_ok.pack(side="right")

        dlg.update_idletasks()
        dlg.grab_set()

    def show_completion_guide(self, report_docx, report_md, subject_name, count):
        """Janela orientativa bonita exibida ao concluir o lote"""
        dlg = tk.Toplevel(self.root)
        dlg.title("🎉 Relatório Gerado — Lote Concluído")
        dlg.configure(bg=self.BG_CARD)
        dlg.transient(self.root)
        self._center_modal(dlg, 620, 440)

        folder_path = os.path.abspath(os.path.dirname(report_docx) if os.path.dirname(report_docx) else ".")

        hdr = tk.Frame(dlg, bg="#181825", padx=20, pady=14)
        hdr.pack(fill="x")
        lbl_h = tk.Label(hdr, text="🎉 Processamento em Lote Concluído com Sucesso!", font=("Segoe UI", 12, "bold"), fg=self.ACCENT_GREEN, bg="#181825")
        lbl_h.pack(anchor="w")

        body = tk.Frame(dlg, bg=self.BG_CARD, padx=22, pady=18)
        body.pack(fill="both", expand=True)

        msg_intro = f"✨ Total de {count} questões da disciplina '{subject_name}' cadastradas com sucesso!"
        lbl_intro = tk.Label(body, text=msg_intro, font=("Segoe UI", 10, "bold"), fg=self.TEXT_PRIMARY, bg=self.BG_CARD, justify="left", wraplength=570)
        lbl_intro.pack(anchor="w", pady=(0, 12))

        info_card = tk.Frame(body, bg="#11111b", highlightbackground=self.BORDER_CARD, highlightthickness=1, padx=14, pady=12)
        info_card.pack(fill="x", pady=(0, 15))

        lbl_doc1 = tk.Label(info_card, text=f"📄 Relatório Word (.docx): {os.path.basename(report_docx)}", font=("Segoe UI", 9, "bold"), fg=self.ACCENT_BLUE, bg="#11111b", anchor="w")
        lbl_doc1.pack(fill="x", pady=2)

        lbl_doc2 = tk.Label(info_card, text=f"📄 Relatório Markdown (.md): {os.path.basename(report_md)}", font=("Segoe UI", 9), fg=self.TEXT_MUTED, bg="#11111b", anchor="w")
        lbl_doc2.pack(fill="x", pady=2)

        lbl_dir = tk.Label(info_card, text=f"📁 Salvo em: {folder_path}", font=("Segoe UI", 9, "italic"), fg=self.TEXT_PRIMARY, bg="#11111b", anchor="w", justify="left")
        lbl_dir.pack(fill="x", pady=(6, 0))

        actions_frame = tk.Frame(body, bg=self.BG_CARD)
        actions_frame.pack(fill="x", side="bottom")

        def _open_folder():
            try:
                if sys.platform == "win32":
                    os.startfile(folder_path)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", folder_path])
                else:
                    subprocess.Popen(["xdg-open", folder_path])
            except Exception as e:
                messagebox.showinfo("Pasta", f"Pasta do relatório:\n{folder_path}")

        def _open_word():
            try:
                full_p = os.path.abspath(report_docx)
                if sys.platform == "win32":
                    os.startfile(full_p)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", full_p])
                else:
                    subprocess.Popen(["xdg-open", full_p])
            except Exception as e:
                messagebox.showinfo("Relatório", f"Relatório salvo em:\n{report_docx}")

        def _next_discipline():
            dlg.destroy()
            self.var_step4_confirmed.set(False)
            self.on_step4_toggle()
            self.lbl_status.config(text="Selecione a planilha da nova disciplina e navegue até a Etapa 4 no AVALIA.", foreground=self.ACCENT_YELLOW)
            self.progress["value"] = 0
            self.root.after(300, self.browse_excel)

        btn_folder = tk.Button(actions_frame, text="📂 Abrir Pasta", command=_open_folder, font=("Segoe UI", 9, "bold"), bg=self.BG_INPUT, fg=self.TEXT_PRIMARY, activebackground="#45475a", activeforeground=self.TEXT_PRIMARY, relief="flat", padx=12, pady=6, cursor="hand2")
        btn_folder.pack(side="left", padx=(0, 8))

        btn_word = tk.Button(actions_frame, text="📄 Abrir Word", command=_open_word, font=("Segoe UI", 9, "bold"), bg=self.ACCENT_BLUE, fg="#11111b", activebackground="#b4befe", activeforeground="#11111b", relief="flat", padx=12, pady=6, cursor="hand2")
        btn_word.pack(side="left", padx=(0, 8))

        btn_next = tk.Button(actions_frame, text="🔄 Outra Disciplina", command=_next_discipline, font=("Segoe UI", 9, "bold"), bg=self.ACCENT_GREEN, fg="#11111b", activebackground="#a6e3a1", activeforeground="#11111b", relief="flat", padx=14, pady=6, cursor="hand2")
        btn_next.pack(side="right")

        dlg.update_idletasks()
        dlg.grab_set()

    def open_guide(self):
        # Busca inteligente do roteiro em múltiplos diretórios (compatível com .exe compilado e script .py)
        possible_dirs = []
        if getattr(sys, 'frozen', False):
            possible_dirs.append(os.path.dirname(sys.executable))
            if hasattr(sys, '_MEIPASS'):
                possible_dirs.append(sys._MEIPASS)
        possible_dirs.append(os.path.dirname(os.path.abspath(__file__)))
        possible_dirs.append(os.getcwd())

        target = None
        for d in possible_dirs:
            docx_p = os.path.join(d, "Roteiro_de_Uso_AVALIA_AutoBatch.docx")
            md_p = os.path.join(d, "Roteiro_de_Uso_AVALIA_AutoBatch.md")
            if os.path.exists(docx_p):
                target = docx_p
                break
            elif os.path.exists(md_p) and not target:
                target = md_p

        if target and os.path.exists(target):
            try:
                if sys.platform == "win32":
                    os.startfile(target)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", target])
                else:
                    subprocess.Popen(["xdg-open", target])
                self.log(f"📖 Roteiro de uso aberto: {os.path.basename(target)}")
            except Exception as e:
                messagebox.showinfo("Roteiro de Uso", f"O arquivo do roteiro está salvo em:\n{target}")
        else:
            messagebox.showwarning("Roteiro Não Encontrado", f"O arquivo 'Roteiro_de_Uso_AVALIA_AutoBatch.docx' não foi encontrado na pasta do programa.")

    def set_badge(self, text, bg, fg):
        if hasattr(self.lbl_badge, 'config_badge'):
            self.lbl_badge.config_badge(text, bg, fg)
        else:
            self.lbl_badge.config(text=text, bg=bg, fg=fg)

    def log(self, message):
        self.txt_log.insert("end", message + "\n")
        self.txt_log.see("end")
        self.root.update_idletasks()

    def download_template(self):
        """Gera e salva uma planilha modelo com 1 questão contendo a estrutura esperada"""
        save_path = filedialog.asksaveasfilename(
            title="Salvar Planilha Modelo Exemplo AVALIA",
            defaultextension=".xlsx",
            initialfile="Modelo_Planilha_AVALIA_Exemplo.xlsx",
            filetypes=[("Planilha Excel", "*.xlsx")]
        )
        if save_path:
            try:
                data = [{
                    "Identificação da questão": "UA-01_QUESTÃO-1_OBJ-1_FÁCIL",
                    "Palavra chave": "Conceitos Gerais",
                    "Tipo da Questão": "questão de complementação Simples",
                    "Nível cognitivo": "Reconhecimento",
                    "Texto da Questão": "Escreva aqui o enunciado completo da questão...",
                    "Alternativa A": "Texto descritivo da alternativa A.",
                    "Alternativa B": "Texto descritivo da alternativa B.",
                    "Alternativa C": "Texto descritivo da alternativa C.",
                    "Alternativa D": "Texto descritivo da alternativa D.",
                    "Feedback da questão": "A resposta certa é a alternativa A. Justificativa detalhada do gabarito."
                }]
                df_template = pd.DataFrame(data)
                df_template.to_excel(save_path, index=False)
                self.log(f"📥 Planilha modelo exemplo gerada e salva com sucesso em: {save_path}")
                messagebox.showinfo("Modelo Gerado", f"Planilha modelo salva em:\n{save_path}\n\nVocê pode abrir este arquivo no Excel para usar como referência!")
            except Exception as e:
                messagebox.showerror("Erro ao Gerar Modelo", str(e))

    def browse_excel(self):
        filename = filedialog.askopenfilename(
            title="Selecionar Planilha Excel do AVALIA",
            filetypes=[("Planilhas Excel", "*.xlsx *.xls")]
        )
        if filename:
            self.selected_excel = filename
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, filename)
            
            try:
                df = pd.read_excel(filename).fillna("")
                rows = len(df)
                has_cols = "Identificação da questão" in df.columns or df.shape[1] >= 5
                if has_cols and rows > 0:
                    basename = os.path.basename(filename)
                    self.lbl_excel_validation.config(
                        text=f"📊 PLANILHA CARREGADA: {basename}  |  TOTAL: {rows} QUESTÕES DETECTADAS",
                        font=("Segoe UI", 10, "bold"),
                        foreground=self.ACCENT_GREEN
                    )
                    self.log(f"📌 Planilha selecionada ({rows} questões): {basename}")
                    # Abrir janela orientativa do Passo 3 para conferência e confirmação de início em lote
                    self.root.after(250, lambda: self.show_guide_step3(rows, basename))
                else:
                    self.lbl_excel_validation.config(text="⚠️ Planilha com formato atípico.", font=("Segoe UI", 9, "bold"), foreground=self.ACCENT_YELLOW)
            except Exception as e:
                self.lbl_excel_validation.config(text=f"❌ Arquivo inválido: {e}", font=("Segoe UI", 9, "bold"), foreground=self.ACCENT_RED)

    def open_chrome(self):
        def _launch():
            self.log("🌐 Lançando Chrome em modo depuração (Porta 9222)...")
            user_data_dir = os.path.join(os.path.expanduser("~"), "AvaliaChromeProfile")
            
            if sys.platform == "win32":
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
                ]
                executable = next((p for p in chrome_paths if os.path.exists(p)), "chrome.exe")
                cmd = [executable, f"--user-data-dir={user_data_dir}", "--remote-debugging-port=9222", LOGIN_URL]
            else:
                cmd = ["google-chrome", f"--user-data-dir={user_data_dir}", "--remote-debugging-port=9222", LOGIN_URL]

            try:
                subprocess.Popen(cmd)
                self.log("✅ Chrome aberto! Faça o login no AVALIA e siga para a Etapa 4.")
            except Exception as e:
                self.log(f"❌ Erro ao abrir Chrome: {e}")

        threading.Thread(target=_launch, daemon=True).start()

    def start_automation(self):
        excel_path = self.entry_path.get().strip()
        if not excel_path or not os.path.exists(excel_path):
            messagebox.showerror("Erro de Validação", "Por favor, escolha um arquivo Excel (.xlsx) válido antes de iniciar!")
            return

        if not self.var_step4_confirmed.get():
            confirm = messagebox.askyesno(
                "Confirmação Necessária",
                "Você ainda não marcou a confirmação do Passo 1.\n\n"
                "O navegador Chrome AVALIA já está aberto na tela da Etapa 4 (Formulário da Questão)?\n\n"
                "Deseja prosseguir mesmo assim?"
            )
            if not confirm:
                return
            self.var_step4_confirmed.set(True)
            self.on_step4_toggle()

        if self.is_running:
            return

        self.is_running = True
        self.should_stop = False
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.set_badge("🟡 EM EXECUÇÃO", self.BG_INPUT, self.ACCENT_YELLOW)
        self.progress["value"] = 0

        threading.Thread(target=self.run_process, args=(excel_path,), daemon=True).start()

    def stop_automation(self):
        if self.is_running:
            self.should_stop = True
            self.log("⚠️ Solicitação de interrupção recebida! Aguardando fim da questão atual...")
            self.lbl_status.config(text="Interrompendo lote...", foreground=self.ACCENT_YELLOW)

    def run_process(self, excel_path):
        try:
            self.log("\n==========================================================")
            self.log(f" 🚀 INICIANDO AVALIA BATCH ENGINE")
            self.log("==========================================================")

            df = pd.read_excel(excel_path).fillna("")
            total = len(df)

            with sync_playwright() as p:
                try:
                    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
                    context = browser.contexts[0]
                    self.log("✅ Conectado ao navegador ativo via CDP na porta 9222.")
                except Exception:
                    self.log("❌ Falha de Conexão: O Chrome não está aberto na porta 9222. Clique em 'Abrir Chrome AVALIA' primeiro.")
                    self.set_badge("🔴 ERRO DE CONEXÃO", self.BG_INPUT, self.ACCENT_RED)
                    return

                last_net_id = {'id': None}

                def handle_response(response):
                    try:
                        url = response.url
                        status = response.status
                        headers = response.headers

                        # 1. Extração segura via URL ou cabeçalho Location (para redirects 302/301 sem ler body)
                        loc = headers.get("location", "")
                        m_loc = re.search(r'/(?:Questao|Editar|Visualizar|Detalhes)/(\d+)', loc, re.IGNORECASE) or re.search(r'idQuestao=(\d+)', loc, re.IGNORECASE)
                        if m_loc:
                            last_net_id['id'] = m_loc.group(1)

                        m_url = re.search(r'/(?:Questao|Editar|Visualizar|Detalhes)/(\d+)', url, re.IGNORECASE) or re.search(r'idQuestao=(\d+)', url, re.IGNORECASE)
                        if m_url:
                            last_net_id['id'] = m_url.group(1)

                        # 2. Se status for 200/201, tentar ler body JSON/Text com try-except individual
                        if status in [200, 201] and any(k in url.lower() for k in ["salvar", "enviar", "questao"]):
                            try:
                                text = response.text()
                                try:
                                    data = json.loads(text)
                                    q_id = data.get("idQuestao") or data.get("IdQuestao") or data.get("id") or data.get("Id") or data.get("questaoId")
                                    if q_id: last_net_id['id'] = str(q_id)
                                except Exception:
                                    m = re.search(r'(?:idQuestao|IdQuestao|id_questao|questaoId)["\']?\s*[:=]\s*["\']?(\d+)', text, re.IGNORECASE)
                                    if m: last_net_id['id'] = m.group(1)
                            except Exception:
                                pass
                    except Exception:
                        pass

                def handle_dialog(dialog):
                    try:
                        msg = dialog.message.lower()
                        self.log(f"  💬 Pop-up do navegador detectado: '{dialog.message}'")
                        if any(k in msg for k in ["sair", "beforeunload", "deseja sair", "alterações não salvas"]):
                            self.log("  🛡️ Cancelando popup de saída da página (dismiss) para MANTER a tela de inserção ativa!")
                            dialog.dismiss()
                        else:
                            dialog.accept()
                    except:
                        pass

                for pg in context.pages:
                    pg.on("response", handle_response)
                    pg.on("dialog", handle_dialog)
                context.on("page", lambda pg: (pg.on("response", handle_response), pg.on("dialog", handle_dialog)))

                results = []
                for i in range(total):
                    if self.should_stop:
                        self.log("⏹️ Execução interrompida pelo usuário.")
                        break



                    row = df.iloc[i]
                    ident = str(row.get('Identificação da questão', '')).strip()

                    self.lbl_status.config(text=f"Processando questão {i+1} de {total}: {ident}", foreground=self.ACCENT_BLUE)
                    self.progress["value"] = ((i + 1) / total) * 100
                    self.log(f"\n⚡ [{i+1}/{total}] Preenchendo: {ident}")

                    # 2. Obter página ativa do AVALIA com o formulário (Passo 4)
                    page = None
                    for attempt in range(10):
                        if self.should_stop: break
                        for pg in context.pages:
                            try:
                                if pg.locator("#Questao_Nome").count() > 0:
                                    page = pg
                                    try: pg.bring_to_front()
                                    except: pass
                                    break
                            except:
                                pass
                        if page: break
                        time.sleep(0.8)

                    if not page and context.pages:
                        page = context.pages[0]



                    if self.should_stop: break

                    # Executar Submissão da Questão
                    res = self.process_single_question(page, row, i, total, last_net_id)
                    if res: results.append(res)

                # Gerar Relatório
                if results:
                    subject_name = os.path.splitext(os.path.basename(excel_path))[0].replace("AD ", "").strip()
                    report_filename_md = f"Relatorio_Oficial_AVALIA_{subject_name}.md"
                    report_filename_docx = f"Relatorio_Oficial_AVALIA_{subject_name}.docx"

                    # 1. Gerar Markdown
                    report_md = f"# Relatório Oficial de Lançamento de Questões — {subject_name}\n\n"
                    report_md += "| # | Identificador Original | Código / ID no AVALIA | Resposta Correta | Tipo de Questão |\n"
                    report_md += "|---|---|---|---|---|\n"
                    for r in results:
                        report_md += f"| {r['num']} | `{r['ident']}` | **{r['ava_id']}** | Alternativa {r['correct']} | {r['tipo']} ({r['tipo_cod']}) |\n"

                    with open(report_filename_md, "w", encoding="utf-8") as f:
                        f.write(report_md)

                    # 2. Gerar Microsoft Word (.docx)
                    docx_saved = self.save_report_docx(results, subject_name, report_filename_docx)

                    self.log(f"\n🎉 LOTE PROCESSADO COM SUCESSO!")
                    self.log(f"✨ Relatório Word gerado: {report_filename_docx}")
                    self.log(f"✨ Relatório Markdown gerado: {report_filename_md}")
                    self.set_badge("🟢 CONCLUÍDO", self.BG_INPUT, self.ACCENT_GREEN)
                    
                    self.show_completion_guide(report_filename_docx, report_filename_md, subject_name, len(results))

        except Exception as e:
            self.log(f"❌ Ocorreu um erro durante a execução: {e}")
            self.set_badge("🔴 ERRO", self.BG_INPUT, self.ACCENT_RED)
            messagebox.showerror("Erro de Execução", str(e))
        finally:
            self.is_running = False
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")

    def save_report_docx(self, results, subject_name, docx_filename):
        try:
            import docx
            from docx.shared import Pt, RGBColor, Inches
            from docx.enum.table import WD_TABLE_ALIGNMENT
            from docx.oxml import parse_xml
            from docx.oxml.ns import nsdecls

            doc = docx.Document()
            sections = doc.sections
            for section in sections:
                section.top_margin = Inches(1)
                section.bottom_margin = Inches(1)
                section.left_margin = Inches(1)
                section.right_margin = Inches(1)

            # Título
            p = doc.add_paragraph()
            run = p.add_run(f"Relatório Oficial de Lançamento de Questões — {subject_name}")
            run.font.name = 'Segoe UI'
            run.font.size = Pt(18)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
            p.paragraph_format.space_after = Pt(14)

            # Tabela
            headers = ["#", "Identificador Original", "Código / ID no AVALIA", "Resposta Correta", "Tipo de Questão"]
            table = doc.add_table(rows=len(results) + 1, cols=len(headers))
            table.alignment = WD_TABLE_ALIGNMENT.CENTER

            # Bordas da Tabela
            tblPr = table._tbl.tblPr
            borders = parse_xml(f'''
                <w:tblBorders {nsdecls("w")}>
                    <w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
                    <w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
                    <w:left w:val="none"/>
                    <w:right w:val="none"/>
                    <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
                    <w:insideV w:val="none"/>
                </w:tblBorders>
            ''')
            tblPr.append(borders)

            # Cabeçalho da Tabela
            hdr_row = table.rows[0]
            for c_idx, h_text in enumerate(headers):
                cell = hdr_row.cells[c_idx]
                cell.text = ""
                p = cell.paragraphs[0]
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.space_before = Pt(4)
                run = p.add_run(h_text)
                run.font.name = 'Segoe UI'
                run.font.size = Pt(9.5)
                run.font.bold = True
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                tcPr = cell._tc.get_or_add_tcPr()
                tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="1E3A8A"/>'))

            # Linhas de Dados
            for r_idx, r in enumerate(results, start=1):
                row = table.rows[r_idx]
                row_vals = [
                    str(r['num']),
                    str(r['ident']),
                    str(r['ava_id']),
                    f"Alternativa {r['correct']}",
                    f"{r['tipo']} ({r['tipo_cod']})"
                ]
                bg_color = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
                for c_idx, val in enumerate(row_vals):
                    cell = row.cells[c_idx]
                    cell.text = ""
                    p = cell.paragraphs[0]
                    p.paragraph_format.space_after = Pt(4)
                    p.paragraph_format.space_before = Pt(4)
                    run = p.add_run(val)
                    run.font.name = 'Segoe UI'
                    run.font.size = Pt(9)
                    tcPr = cell._tc.get_or_add_tcPr()
                    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_color}"/>'))

            doc.save(docx_filename)
            return True
        except Exception as e:
            self.log(f"⚠️ Erro ao gerar Word (.docx): {e}")
            return False

    def process_single_question(self, page, row, index, total, last_net_id):
        context = page.context
        # Helper para buscar valor da planilha ignorando variações de nome de coluna (com/sem acento, da/de, etc.)
        def get_field(row_data, target_keys):
            for k in target_keys:
                for col in row_data.index:
                    col_clean = str(col).lower().replace(" ", "").replace("_", "").replace("-", "").replace("ç", "c").replace("ã", "a").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
                    k_clean = k.lower().replace(" ", "").replace("_", "").replace("-", "").replace("ç", "c").replace("ã", "a").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
                    if k_clean in col_clean:
                        val = str(row_data[col]).strip()
                        if val and val.lower() != "nan":
                            return val
            return ""

        ident = get_field(row, ['identificacao', 'identificador', 'questao', 'nome']) or f"QUESTAO_{index+1}"
        is_last = (index == total - 1)

        # ---------------------------------------------------------------------
        # 📌 PASSO 0: Garantir Posicionamento na Etapa 4 e Limpeza de Modais
        # ---------------------------------------------------------------------
        # Fechar abas extras e focar a página principal
        for p_extra in list(context.pages):
            if p_extra != page:
                try: p_extra.close()
                except Exception: pass
        try: page.bring_to_front()
        except Exception: pass

        # Purga de modais remanescentes no DOM se houver
        try:
            page.evaluate("""() => {
                document.querySelectorAll('.modal, .modal-backdrop, [class*="modal-backdrop"]').forEach(el => {
                    try { el.remove(); } catch(e) {}
                });
                if (document.body) {
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = 'auto';
                    document.body.style.paddingRight = '0px';
                }
            }""")
        except Exception:
            pass

        # Garantir que a página esteja fisicamente na Etapa 4 de Inserção de Questão (#Questao_Nome visível)
        is_on_step4 = page.evaluate("""() => {
            const el = document.getElementById('Questao_Nome');
            return el && el.offsetWidth > 0 && el.offsetHeight > 0;
        }""")

        if not is_on_step4:
            self.log("  🔄 Navegador fora da Etapa 4. Retornando para a tela de inserção de questão...")

            # 1. Tentar clicar em botões de "Elabore Novas Questões" ou links de Inserir na página
            page.evaluate("""() => {
                const btns = Array.from(document.querySelectorAll('a, button, input')).filter(el => {
                    const txt = (el.innerText || el.textContent || el.value || '').trim().toLowerCase();
                    const href = (el.getAttribute('href') || '').toLowerCase();
                    return txt.includes('elabore novas') || txt.includes('criar nova') || href.includes('questao/inserir');
                });
                if (btns.length > 0) {
                    try { btns[0].click(); } catch(e) {}
                }
            }""")
            time.sleep(1.5)

            # 2. Verificar se já carregou a Etapa 4
            is_on_step4 = page.evaluate("""() => {
                const el = document.getElementById('Questao_Nome');
                return el && el.offsetWidth > 0 && el.offsetHeight > 0;
            }""")

            # 3. Se ainda não estiver na Etapa 4, redirecionar diretamente para a URL de inserção
            if not is_on_step4:
                curr_url = page.url
                if "avalia" in curr_url.lower():
                    parts = curr_url.split("/")
                    base_domain = parts[0] + "//" + parts[2]
                    target_url = base_domain + "/Questao/Inserir"
                    self.log(f"  📍 Redirecionando diretamente para a URL da Etapa 4: {target_url}")
                    try:
                        page.goto(target_url, timeout=12000)
                        time.sleep(1.8)
                    except Exception:
                        pass

        # ---------------------------------------------------------------------
        # 📌 PASSO 1: Preenchimento de campos (Nome, Palavras-chave, Tipo, Nível Cognitivo, Enunciado, Alternativas A-D, Feedback)
        # ---------------------------------------------------------------------
        self.log("  📍 [PASSO 1] Limpando campos anteriores e preenchendo novos dados da questão...")

        # Limpeza e preenchimento de Identificação
        try:
            page.wait_for_selector("#Questao_Nome", timeout=15000)
            page.locator("#Questao_Nome").fill("")
            page.locator("#Questao_Nome").fill(ident)
        except Exception:
            page.evaluate(r"""(val) => {
                const el = document.getElementById('Questao_Nome');
                if (el) {
                    el.value = '';
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                    el.value = val;
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }""", ident)

        # 1. Limpeza rigorosa de Palavras-chave anteriores e inserção das novas
        palavra = get_field(row, ['palavra chave', 'palavra-chave', 'palavras chave', 'keywords', 'tags'])
        page.evaluate(r"""(p) => {
            // A. Remover tags existentes via plugins jQuery se disponíveis
            if (typeof $ !== 'undefined') {
                try { $('#PalavrasChave, input[name="PalavrasChave"]').importTags(''); } catch(e) {}
                try { $('#PalavrasChave, input[name="PalavrasChave"]').tagsinput('removeAll'); } catch(e) {}
            }
            // B. Clicar no botão 'x' de cada tag pill existente no DOM
            const removeBtns = document.querySelectorAll('.tag [data-role="remove"], .tag a, .tag .x, span.tag a, .tag span');
            removeBtns.forEach(btn => { try { btn.click(); } catch(e) {} });
            
            document.querySelectorAll('.tag, .tag-item, span.tag').forEach(el => {
                try { el.remove(); } catch(e) {}
            });

            const inputTag = document.querySelector('input[id$="_tag"]') || 
                             document.getElementById('PalavrasChave') || 
                             document.querySelector('input[name="PalavrasChave"]') ||
                             document.querySelector('input[name*="Tag"]');
            if (inputTag) {
                inputTag.value = '';
                inputTag.dispatchEvent(new Event('input', { bubbles: true }));
                inputTag.dispatchEvent(new Event('change', { bubbles: true }));
            }

            // C. Inserir novas palavras-chave
            if (p && inputTag) {
                const tags = p.split(/[,;]/).map(t => t.trim()).filter(t => t.length > 0);
                for (let tag of tags) {
                    if (typeof $ !== 'undefined' && $.fn && $.fn.addTag) {
                        try { $('#PalavrasChave, input[name="PalavrasChave"]').addTag(tag); } catch(e) {}
                    }
                    inputTag.value = tag;
                    inputTag.dispatchEvent(new Event('input', { bubbles: true }));
                    inputTag.dispatchEvent(new Event('change', { bubbles: true }));
                    inputTag.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', keyCode: 13, which: 13, bubbles: true }));
                    inputTag.dispatchEvent(new KeyboardEvent('keyup', { key: 'Enter', keyCode: 13, which: 13, bubbles: true }));
                }
            }
        }""", palavra)

        # 2. Tipo da Questão (Desbloqueio prévio do campo, reset e seleção dinâmica por texto)
        tipo_raw = get_field(row, ['tipo da questao', 'tipo de questao', 'tipo questao', 'tipo', 'tipo da questão', 'tipo de questão'])
        page.evaluate(r"""(tipoText) => {
            const select = document.getElementById('Questao_IdTipoQuestao') || document.querySelector('select[name*="TipoQuestao"]');
            if (!select) return;

            // Desbloquear o campo de seleção de tipo caso a plataforma tenha desativado
            select.removeAttribute('disabled');
            select.disabled = false;
            select.removeAttribute('readonly');
            select.readOnly = false;
            if (typeof $ !== 'undefined') {
                try { $(select).prop('disabled', false).removeClass('disabled'); } catch(e) {}
            }

            // Reset prévio do valor
            select.selectedIndex = 0;
            select.dispatchEvent(new Event('change', { bubbles: true }));

            if (!tipoText) return;
            
            function norm(s) { return (s || '').normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim(); }
            const target = norm(tipoText);
            
            let matchedOpt = null;
            for (let opt of select.options) {
                const optTxt = norm(opt.text);
                if (optTxt && (optTxt.includes(target) || target.includes(optTxt))) {
                    matchedOpt = opt;
                    break;
                }
            }

            if (!matchedOpt) {
                for (let opt of select.options) {
                    const optTxt = norm(opt.text);
                    if (target.includes('multipla') || target.includes('resposta m')) {
                        if (optTxt.includes('multipla') || optTxt.includes('resposta m')) { matchedOpt = opt; break; }
                    } else if (target.includes('asser') || target.includes('razao')) {
                        if (optTxt.includes('asser') || optTxt.includes('razão')) { matchedOpt = opt; break; }
                    } else if (target.includes('complement')) {
                        if (optTxt.includes('complement')) { matchedOpt = opt; break; }
                    } else if (target.includes('interpret')) {
                        if (optTxt.includes('interpret')) { matchedOpt = opt; break; }
                    }
                }
            }

            if (matchedOpt) {
                select.value = matchedOpt.value;
                select.dispatchEvent(new Event('input', { bubbles: true }));
                select.dispatchEvent(new Event('change', { bubbles: true }));
                select.dispatchEvent(new Event('blur', { bubbles: true }));

                const hiddenTipo = document.querySelector('input[name="Questao.IdTipoQuestao"], input[name="IdTipoQuestao"], #IdTipoQuestao');
                if (hiddenTipo) {
                    hiddenTipo.value = matchedOpt.value;
                    hiddenTipo.dispatchEvent(new Event('change', { bubbles: true }));
                }

                if (typeof $ !== 'undefined') {
                    try { $(select).val(matchedOpt.value).trigger('change').trigger('chosen:updated'); } catch(e) {}
                }
            }
        }""", tipo_raw)

        # 3. Nível Cognitivo (Reset prévio e seleção dinâmica por nível/sinônimos)
        nivel = get_field(row, ['nivel cognitivo', 'nivel', 'cognitivo', 'dificuldade'])
        page.evaluate(r"""(nivelText) => {
            const select = document.getElementById('Questao_IdNivelCognitivo') || document.getElementById('IdHabilidadeQuestao');
            if (!select) return;

            // Reset prévio da seleção
            select.selectedIndex = 0;
            select.dispatchEvent(new Event('change', { bubbles: true }));

            if (!nivelText) return;

            function norm(s) { return (s || '').normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim(); }
            const target = norm(nivelText);

            let matchedOpt = null;
            for (let opt of select.options) {
                const optTxt = norm(opt.text);
                if (optTxt && (optTxt.includes(target) || target.includes(optTxt))) {
                    matchedOpt = opt;
                    break;
                }
            }

            // Mapeamento de sinônimos cognitivos comuns
            if (!matchedOpt) {
                const mapSynonyms = {
                    'reconhecimento': ['conhecimento', 'lembrar', 'reconhecimento'],
                    'compreensao': ['entendimento', 'compreender', 'compreensao'],
                    'aplicacao': ['aplicar', 'aplicacao'],
                    'analise': ['analisar', 'analise'],
                    'sintese': ['sintetizar', 'criar', 'sintese'],
                    'julgamento': ['avaliar', 'julgamento', 'avaliacao']
                };
                for (let category in mapSynonyms) {
                    if (mapSynonyms[category].some(syn => target.includes(syn))) {
                        for (let opt of select.options) {
                            const optTxt = norm(opt.text);
                            if (mapSynonyms[category].some(syn => optTxt.includes(syn))) {
                                matchedOpt = opt;
                                break;
                            }
                        }
                        if (matchedOpt) break;
                    }
                }
            }

            if (matchedOpt) {
                select.value = matchedOpt.value;
                select.dispatchEvent(new Event('change', { bubbles: true }));
                if (typeof $ !== 'undefined') $(select).trigger('change');
            }
        }""", nivel)

        # 4. TinyMCE Editors & Sincronização de Textareas (Preservação 1:1 de parágrafos e quebras de linha das células do Excel)
        texto_q = get_field(row, ['texto da questao', 'enunciado', 'texto'])
        alt_a = get_field(row, ['alternativa a', 'afirmativa a', 'opcao a'])
        alt_b = get_field(row, ['alternativa b', 'afirmativa b', 'opcao b'])
        alt_c = get_field(row, ['alternativa c', 'afirmativa c', 'opcao c'])
        alt_d = get_field(row, ['alternativa d', 'afirmativa d', 'opcao d'])
        alt_e = get_field(row, ['alternativa e', 'afirmativa e', 'opcao e'])
        feedback = get_field(row, ['feedback da questao', 'feedback', 'justificativa', 'gabarito comentado'])

        def cell_to_html(text_val):
            if not text_val:
                return ""
            s = str(text_val).strip()
            if not s:
                return ""
            if re.search(r'<[a-z][\s\S]*>', s, re.IGNORECASE):
                return s
            lines = s.replace('\r\n', '\n').replace('\r', '\n').split('\n')
            p_list = []
            for line in lines:
                t = line.strip()
                if t:
                    p_list.append(f"<p>{t}</p>")
                else:
                    p_list.append("<p>&nbsp;</p>")
            return "".join(p_list)

        texto_q_html = cell_to_html(texto_q)
        alt_a_html = cell_to_html(alt_a)
        alt_b_html = cell_to_html(alt_b)
        alt_c_html = cell_to_html(alt_c)
        alt_d_html = cell_to_html(alt_d)
        alt_e_html = cell_to_html(alt_e)
        feedback_html = cell_to_html(feedback)

        page.evaluate(r"""(data) => {
            const map = {
                'TextoQuestao': data.texto_q,
                'TextoAfirmativaA': data.alt_a,
                'TextoAfirmativaB': data.alt_b,
                'TextoAfirmativaC': data.alt_c,
                'TextoAfirmativaD': data.alt_d,
                'TextoAfirmativaE': data.alt_e,
                'TextoPadraoResposta': data.feedback,
                'TextoFeedbackQuestao': data.feedback,
                'PadraoResposta': data.feedback,
                'Questao_TextoPadraoResposta': data.feedback
            };

            if (typeof tinymce !== 'undefined') {
                for (let id in map) {
                    if (!map[id]) continue;
                    let inst = tinymce.get(id);
                    if (inst) {
                        inst.setContent(map[id]);
                        inst.save();
                        if (typeof inst.fire === 'function') {
                            try { inst.fire('change'); } catch(e) {}
                        }
                    }
                }
                if (typeof tinymce.triggerSave === 'function') {
                    tinymce.triggerSave();
                }
            }

            for (let id in map) {
                if (!map[id]) continue;
                let el = document.getElementById(id) || document.querySelector(`[name="${id}"]`) || document.querySelector(`[name$="${id}"]`);
                if (el) {
                    el.value = map[id];
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                    el.dispatchEvent(new Event('blur', { bubbles: true }));
                }
            }
        }""", {
            "texto_q": texto_q_html,
            "alt_a": alt_a_html,
            "alt_b": alt_b_html,
            "alt_c": alt_c_html,
            "alt_d": alt_d_html,
            "alt_e": alt_e_html,
            "feedback": feedback_html
        })

        # ---------------------------------------------------------------------
        # 📌 PASSO 2: Remoção da Opção E (se a planilha contiver 4 alternativas)
        # ---------------------------------------------------------------------
        if not alt_e:
            self.log("  📍 [PASSO 2] Verificando e removendo 5ª alternativa (E)...")
            page.evaluate("""() => {
                const altEField = document.getElementById('TextoAfirmativaE') || 
                                   document.querySelector('[name*="Afirmativas[4]"]') || 
                                   document.querySelector('[id*="TextoAfirmativaE"]') ||
                                   document.querySelector('#afE, #AfirmativaE');
                const optionsCount = document.querySelectorAll('textarea[name*="Afirmativas"], input[name*="Afirmativas"], [id*="TextoAfirmativa"]').length;
                
                // Remover rigorosamente APENAS se a 5ª alternativa (E - índice 4) existir na tela
                if (altEField || optionsCount >= 5) {
                    if (typeof removerAfirmativa === 'function') {
                        try { removerAfirmativa(4); } catch(e) {}
                    }
                    
                    const btn4 = Array.from(document.querySelectorAll('button, a, .btn, i, span')).find(el => {
                        const onclick = (el.getAttribute('onclick') || '').toLowerCase();
                        return onclick.includes('removerafirmativa(4)') || (onclick.includes('removerafirmativa') && onclick.includes('4'));
                    });
                    if (btn4) {
                        try { btn4.click(); } catch(e) {}
                    } else {
                        const allRemoveBtns = Array.from(document.querySelectorAll('button, a, .btn, span, i')).filter(el => {
                            const txt = (el.innerText || el.textContent || '').toLowerCase();
                            const onclick = (el.getAttribute('onclick') || '').toLowerCase();
                            return txt.includes('remover alternativa') || txt.includes('remover afirmativa') || onclick.includes('removerafirmativa');
                        });
                        if (allRemoveBtns.length >= 5) {
                            try { allRemoveBtns[4].click(); } catch(e) {}
                        }
                    }

                    const remainingE = document.getElementById('TextoAfirmativaE') || document.querySelector('[name*="Afirmativas[4]"]');
                    if (remainingE) {
                        if (typeof tinymce !== 'undefined') {
                            try { tinymce.remove('#TextoAfirmativaE'); } catch(e) {}
                        }
                        const container = remainingE.closest('.form-group, .row, .item-afirmativa, div[class*="afirmativa"], tr');
                        if (container) {
                            container.remove();
                        } else {
                            remainingE.remove();
                        }
                    }
                }
            }""")
            time.sleep(0.6)

        # ---------------------------------------------------------------------
        # 📌 PASSO 3: Gabarito (Seleção da alternativa correta no iCheck)
        # ---------------------------------------------------------------------
        self.log("  📍 [PASSO 3] Marcando gabarito da resposta correta (iCheck)...")
        feedback_lower = feedback.lower()
        alts = [alt_a.lower().rstrip('.'), alt_b.lower().rstrip('.'), alt_c.lower().rstrip('.'), alt_d.lower().rstrip('.')]
        correct_idx = 0
        letters = ["a", "b", "c", "d"]
        for i, l in enumerate(letters):
            if f"resposta certa é {alts[i]}" in feedback_lower or f"alternativa {l}" in feedback_lower or f"resposta certa é a alternativa {l}" in feedback_lower or f"resposta certa é {l}" in feedback_lower:
                correct_idx = i
                break
        else:
            for i, text_alt in enumerate(alts):
                if text_alt and text_alt in feedback_lower[:120]:
                    correct_idx = i
                    break

        page.evaluate("""(idx) => {
            const selector = 'input[name="Afirmativas[' + idx + '].Verdadeira"]';
            if (typeof $ !== 'undefined' && $.fn && $.fn.iCheck) {
                $(selector).iCheck('check');
            } else {
                const el = document.querySelector(selector);
                if (el) { el.checked = true; el.dispatchEvent(new Event('change', { bubbles: true })); }
            }
        }""", correct_idx)
        letter_name = ["A", "B", "C", "D"][correct_idx]
        self.log(f"  ✅ Gabarito identificado: Alternativa {letter_name}")

        last_net_id['id'] = None

        # ---------------------------------------------------------------------
        # ---------------------------------------------------------------------
        # 📌 PASSO 4: Salvar Formulário (Clicar em "Salvar formulário" #submitFormQuestao)
        # ---------------------------------------------------------------------
        self.log("  📍 [PASSO 4] Salvando formulário da Etapa 4 (#submitFormQuestao)...")
        page.evaluate("""() => {
            const s = document.getElementById('Questao_IdTipoQuestao');
            if (s && (s.value === '0' || !s.value)) s.value = '60';
            const b = document.getElementById('submitFormQuestao') || document.querySelector('button[type="submit"]');
            if (b) b.click();
        }""")
        time.sleep(1.5)

        # Prevenção de navegação acidental
        try:
            page.evaluate("""() => {
                window.onbeforeunload = null;
                if (typeof $ !== 'undefined') {
                    try { $(window).unbind('beforeunload'); } catch(e) {}
                    try { $(window).off('beforeunload'); } catch(e) {}
                }
            }""")
        except:
            pass

        # Helper para tratamento da Regra 1: 'Sugestões de correções' (se existir e estiver visível)
        def handle_corrections_if_present():
            has_corrections = page.evaluate("""() => {
                const visibleIgnoreBtns = Array.from(document.querySelectorAll('button, a, input, .btn')).filter(el => {
                    const txt = (el.innerText || el.textContent || el.value || '').trim().toLowerCase();
                    const onclick = (el.getAttribute('onclick') || '').toLowerCase();
                    const isIgnorar = (txt === 'ignorar' || onclick.includes('ignorar') || onclick.includes('ignorarcorrecao'));
                    return isIgnorar && el.offsetWidth > 0 && el.offsetHeight > 0;
                });

                const activeHeader = document.querySelector('h1, h2, h3, h4, .step-title, .box-title, .panel-title');
                const headerTxt = activeHeader ? (activeHeader.innerText || '').toLowerCase() : '';
                const isCorrectionStep = headerTxt.includes('sugestões de correções') || headerTxt.includes('sugestoes de correcoes');

                return isCorrectionStep || visibleIgnoreBtns.length > 0;
            }""")

            if has_corrections:
                self.log("  ⚠️ Tela 'Sugestões de correções' visível detectada. Clicando em 'Ignorar' em todas as correções...")
                page.evaluate("""() => {
                    const ignoreBtns = Array.from(document.querySelectorAll('button, a, input, .btn')).filter(el => {
                        const txt = (el.innerText || el.textContent || el.value || '').trim().toLowerCase();
                        const onclick = (el.getAttribute('onclick') || '').toLowerCase();
                        return (txt === 'ignorar' || txt.includes('ignorar') || onclick.includes('ignorar')) && el.offsetWidth > 0 && el.offsetHeight > 0;
                    });
                    for (let b of ignoreBtns) {
                        try { b.click(); } catch(e) {}
                    }
                }""")
                time.sleep(1.0)

                self.log("  💾 Clicando no botão 'Salvar' das correções...")
                page.evaluate("""() => {
                    const saveBtns = Array.from(document.querySelectorAll('button, a, input, .btn')).filter(el => {
                        const txt = (el.innerText || el.textContent || el.value || '').trim().toLowerCase();
                        const id = (el.id || '').toLowerCase();
                        return (txt === 'salvar' || id.includes('salvarcorrecoes')) && !id.includes('submitformquestao') && el.offsetWidth > 0 && el.offsetHeight > 0;
                    });
                    if (saveBtns.length > 0) {
                        try { saveBtns[0].click(); } catch(e) {}
                    }
                }""")
                time.sleep(1.2)

                self.log("  ⏩ Avançando após correções (Etapa ➔ Próximo)...")
                self.click_element_safely(page, "#buttonProximo")
                time.sleep(1.5)

        # Helper para acionar 'Visualizar digital' e Fechar Modal (Regra 2)
        def trigger_preview_and_close():
            self.log("  📍 [PASSO 7] Acionando pré-visualização 'Visualizar digital'...")
            page.evaluate("""() => {
                window.onbeforeunload = null;
                if (typeof $ !== 'undefined') {
                    try { $(window).unbind('beforeunload'); } catch(e) {}
                    try { $(window).off('beforeunload'); } catch(e) {}
                }

                let triggered = false;
                if (typeof visualizarDigital === 'function') {
                    try { visualizarDigital(); triggered = true; } catch(e) {}
                }
                if (!triggered && typeof previewDigital === 'function') {
                    try { previewDigital(); triggered = true; } catch(e) {}
                }
                if (!triggered && typeof CarregarVisualizacaoDigital === 'function') {
                    try { CarregarVisualizacaoDigital(); triggered = true; } catch(e) {}
                }

                if (!triggered) {
                    const btns = Array.from(document.querySelectorAll('button, a, input, .btn')).filter(el => {
                        const txt = (el.innerText || el.textContent || '').trim().toLowerCase();
                        const onclick = (el.getAttribute('onclick') || '').toLowerCase();
                        const id = (el.id || '').toLowerCase();
                        return txt === 'digital' || txt.includes('digital') || onclick.includes('digital') || id.includes('digital');
                    });
                    if (btns.length > 0) {
                        const targetBtn = btns[0];
                        if (targetBtn.tagName === 'A' && targetBtn.getAttribute('target') === '_blank') {
                            targetBtn.removeAttribute('target');
                        }
                        try { targetBtn.click(); } catch(e) {}
                    }
                }
            }""")
            time.sleep(1.2)

            # Fechar qualquer aba/janela secundária que tenha sido aberta pelo navegador
            try:
                for p_extra in list(context.pages):
                    if p_extra != page:
                        try: p_extra.close()
                        except Exception: pass
            except Exception:
                pass

            try: page.bring_to_front()
            except Exception: pass

            self.log("  📍 [PASSO 8] Fechando modal de visualização...")
            # 1. Pressionar a tecla ESC no teclado virtual
            try:
                page.keyboard.press("Escape")
                time.sleep(0.3)
                page.keyboard.press("Escape")
            except Exception:
                pass

            # 2. Fechamento total e remoção física de overlays do DOM
            page.evaluate("""() => {
                if (typeof $ !== 'undefined') {
                    try { $('.modal').modal('hide'); } catch(e) {}
                    try { $('.modal-backdrop').remove(); } catch(e) {}
                    try { $('body').removeClass('modal-open'); } catch(e) {}
                }

                // Clicar em botões de fechar conhecidos
                const closeBtns = document.querySelectorAll('.modal .close, .modal [data-dismiss="modal"], .modal [data-bs-dismiss="modal"], .modal button.close, .modal .btn-close, #btnFecharModal, #btnFechar, #btn-close, button.close, .close');
                closeBtns.forEach(btn => { try { btn.click(); } catch(e) {} });

                // Remoção completa de elementos modal e backdrops do DOM
                document.querySelectorAll('.modal, .modal-backdrop, [class*="modal-backdrop"]').forEach(el => {
                    try { el.remove(); } catch(e) {}
                });

                if (document.body) {
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = 'auto';
                    document.body.style.paddingRight = '0px';
                }
            }""")
            time.sleep(0.8)

        # ---------------------------------------------------------------------
        # 📌 PASSO 5: Avançar Etapa 4 ➔ Etapa 5 (#buttonProximo)
        # ---------------------------------------------------------------------
        self.log("  📍 [PASSO 5] Avançando wizard (Etapa 4 ➔ Etapa 5)...")
        self.click_element_safely(page, "#buttonProximo")
        time.sleep(1.5)

        # Checar Regra 1: Sugestões de correções (se houver)
        handle_corrections_if_present()

        # ---------------------------------------------------------------------
        # 📌 PASSO 6: Avançar Etapa 5 ➔ Etapa 6 (#buttonProximo)
        # ---------------------------------------------------------------------
        self.log("  📍 [PASSO 6] Avançando wizard (Etapa 5 ➔ Etapa 6)...")
        self.click_element_safely(page, "#buttonProximo")
        time.sleep(1.5)

        # Checar Regra 1: Sugestões de correções (se houver na Etapa 6)
        handle_corrections_if_present()

        # ---------------------------------------------------------------------
        # 📌 PASSO 7 & 8: Executar 'Visualizar digital' e 'Fechar Modal' na Etapa 6
        # ---------------------------------------------------------------------
        trigger_preview_and_close()

        # ---------------------------------------------------------------------
        # 📌 PASSO 9: Avançar Etapa 6 ➔ Etapa 7 (#buttonProximo com Verificação de Visibilidade)
        # ---------------------------------------------------------------------
        self.log("  📍 [PASSO 9] Avançando wizard (Etapa 6 ➔ Etapa 7)...")
        target_btn_id = "btnEnviarQuestaoCriarNova" if is_last else "btnEnviarQuestaoCriarNovaMesmosParametros"

        for nav_attempt in range(5):
            is_step7 = page.evaluate(f"""(btnId) => {{
                const btn = document.getElementById(btnId) || 
                            document.getElementById('btnEnviarQuestaoCriarNovaMesmosParametros') || 
                            document.getElementById('btnEnviarQuestaoCriarNova');
                return btn && btn.offsetWidth > 0 && btn.offsetHeight > 0;
            }}""", target_btn_id)
            if is_step7:
                break
            self.click_element_safely(page, "#buttonProximo")
            time.sleep(1.2)

        # ---------------------------------------------------------------------
        # 📌 PASSO 10 e 11: Envio na Etapa 7 com Verificação Rigorosa e Confirmação de ID Numérico
        # ---------------------------------------------------------------------
        last_net_id['id'] = None
        captured_id = None
        target_btn_id = "btnEnviarQuestaoCriarNova" if is_last else "btnEnviarQuestaoCriarNovaMesmosParametros"
        btn_label = "'Enviar e criar nova Questão'" if is_last else "'Enviar e criar nova questão com os mesmos conteúdos e disciplinas'"

        self.log(f"  📍 [PASSO 10 - QUESTÃO {index + 1}/{total}] Clicando em {btn_label} ({target_btn_id})...")

        max_submit_retries = 3
        for attempt in range(1, max_submit_retries + 1):
            if attempt > 1:
                self.log(f"  🔄 [TENTATIVA {attempt}/{max_submit_retries}] Re-tentando envio da Questão {index + 1}...")

            # 1. Clicar no botão correspondente
            clicked = False
            for sel in [
                f"#{target_btn_id}",
                "button:has-text('mesmos conteúdos')" if not is_last else "button:has-text('Enviar e criar nova Questão')",
                "button:has-text('mesmos parâmetros')" if not is_last else "button:has-text('criar nova questão')",
                "input[value*='mesmos']" if not is_last else "input[value*='criar']"
            ]:
                try:
                    loc = page.locator(sel)
                    if loc.count() > 0 and loc.first.is_visible():
                        loc.first.click(timeout=4000)
                        clicked = True
                        break
                except Exception:
                    pass

            if not clicked:
                try:
                    page.evaluate(f"""(btnId) => {{
                        const btn = document.getElementById(btnId) || 
                                    Array.from(document.querySelectorAll('button, a')).find(b => {{
                                        const txt = (b.innerText || b.textContent || '').toLowerCase();
                                        return btnId.includes('Mesmos') ? txt.includes('mesmos') : txt.includes('criar nova');
                                    }});
                        if (btn) btn.click();
                    }}""", target_btn_id)
                except Exception:
                    pass

            # 2. Monitorar resposta de rede, redirecionamento ou DOM por até 10 segundos
            self.log("  📍 [PASSO 11] Capturando o código ID numérico oficial gerado pelo AVALIA...")
            for sec in range(25):
                time.sleep(0.4)

                # Extração via Listener de Rede
                if last_net_id.get('id'):
                    captured_id = str(last_net_id['id'])
                    break

                # Extração via DOM, URL ou Toasts da Plataforma
                h_val = page.evaluate(r"""() => {
                    const h = document.getElementById('Questao_IdQuestao') || document.querySelector('input[name="IdQuestao"]');
                    if (h && h.value && h.value !== '0') return h.value;

                    const m_url = window.location.href.match(/\/Questao\/(?:Editar|Visualizar|Detalhes)\/(\d+)/i) || window.location.href.match(/idQuestao=(\d+)/i);
                    if (m_url) return m_url[1];

                    // Procurar número de ID em mensagens toast/pnotify da plataforma (ex: "Questão cadastrada com sucesso! (ID: 1871912)")
                    const toasts = Array.from(document.querySelectorAll('.ui-pnotify-text, .alert-success, .toast-message, #toast-container, .alert-info'));
                    for (let t of toasts) {
                        const txt = (t.innerText || t.textContent || '');
                        const m_toast = txt.match(/\b(1\d{6,7})\b/);
                        if (m_toast) return m_toast[1];
                    }
                    return null;
                }""")
                if h_val and h_val not in ["0", ""]:
                    captured_id = str(h_val)
                    break

                # Detectar erro 504 / falha de servidor AVALIA
                has_error_504 = page.evaluate("""() => {
                    const txts = Array.from(document.querySelectorAll('.ui-pnotify-text, .alert-danger, .toast-message')).map(el => el.innerText || '');
                    return txts.some(t => t.includes('504') || t.includes('Response status code') || t.includes('Object reference'));
                }""")
                if has_error_504 and sec > 3:
                    self.log(f"  ⚠️ Detectada instabilidade/Erro 504 do Servidor AVALIA no envio da Questão {index + 1}.")
                    break

            if captured_id:
                break

        # 3. Confirmação Final do Registro
        if captured_id:
            self.log(f"  ✨ [SUCESSO] Questão {index + 1} cadastrada com sucesso! Código AVALIA: {captured_id}")
            return {
                "num": index + 1,
                "ident": ident,
                "correct": letter_name,
                "tipo": tipo_raw,
                "tipo_cod": tipo_raw or "Objetiva",
                "ava_id": captured_id,
                "status": "SUCESSO"
            }
        else:
            self.log(f"  ❌ [FALHA] Questão {index + 1} NÃO foi salva no AVALIA! (Servidor retornou Erro 504/Timeout e não gerou ID numérico).")
            return {
                "num": index + 1,
                "ident": ident,
                "correct": letter_name,
                "tipo": tipo_raw,
                "tipo_cod": tipo_raw or "Objetiva",
                "ava_id": "❌ FALHA NO SERVIDOR (Não Salva)",
                "status": "ERRO"
            }

    def click_element_safely(self, page, selector_or_text):
        try:
            if selector_or_text.startswith("#") or selector_or_text.startswith("."):
                loc = page.locator(selector_or_text)
                if loc.count() > 0 and loc.first.is_visible():
                    loc.first.click()
                    return True
            else:
                loc = page.locator("#formQuestao, .wizard, .wizard-actions").locator("button, a, input").filter(has_text=re.compile(f"^{selector_or_text}$", re.IGNORECASE))
                if loc.count() > 0 and loc.first.is_visible():
                    loc.first.click()
                    return True
        except:
            pass
        try:
            page.evaluate(f"""(sel) => {{
                const el = document.querySelector(sel) || 
                           document.getElementById('buttonProximo') ||
                           document.getElementById('btnProximo') ||
                           Array.from(document.querySelectorAll('#formQuestao button, #formQuestao a, .wizard button, .wizard a, .wizard-actions button')).find(b => {{
                               const txt = (b.innerText || b.textContent || '').trim().toLowerCase();
                               return txt === 'próximo' || txt === 'proximo';
                           }});
                if (el) el.click();
            }}""", selector_or_text)
            return True
        except:
            pass
        return False

if __name__ == "__main__":
    root = tk.Tk()
    app = AvaliaIHCApp(root)
    root.mainloop()
