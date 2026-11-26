"""Botão Tkinter com cantos arredondados e sombra, sem dependência visual extra."""
import tkinter as tk
from tkinter import font, ttk


BACKGROUND = "#f3f6f8"


def rounded_polygon(canvas, bounds, radius, *, fill, outline=""):
    x1, y1, x2, y2 = bounds
    radius = min(radius, max(0, (x2 - x1) / 2), max(0, (y2 - y1) / 2))
    return canvas.create_polygon(x1+radius,y1, x2-radius,y1, x2,y1, x2,y1+radius,
                                 x2,y2-radius, x2,y2, x2-radius,y2, x1+radius,y2,
                                 x1,y2, x1,y2-radius, x1,y1+radius, x1,y1,
                                 smooth=True, splinesteps=30, fill=fill, outline=outline)


class RoundedSurface(tk.Frame):
    """Fundo arredondado atrás dos widgets, preservando a geometria do Tk."""
    def __init__(self, parent, *, fill=BACKGROUND, border="#b6c4ce", radius=20, padding=12, text="", **kwargs):
        top_padding = max(padding, 36) if text else padding
        super().__init__(parent, background=BACKGROUND, padx=padding, pady=top_padding, **kwargs)
        self.surface_fill = fill
        self.surface_border = border
        self.surface_radius = radius
        self.surface_title = text
        self.backdrop = tk.Canvas(self, background=BACKGROUND, highlightthickness=0, bd=0, takefocus=False)
        # "inside" desconta padx/pady do Frame e corta o desenho sob os
        # campos. Desenhar sobre toda a superfície externa mantém a borda.
        self.backdrop.place(x=0, y=0, relwidth=1, relheight=1, bordermode="outside")
        self.backdrop.tk.call("lower", self.backdrop._w)
        self.backdrop.bind("<Configure>", self.draw_surface)
        if text:
            self.title_label = tk.Label(self, text=text, background=BACKGROUND, foreground="#24556b", font=("Segoe UI", 12, "bold"), padx=5)
            self.title_label.place(x=16, y=8, bordermode="outside")

    def draw_surface(self, event=None):
        self.backdrop.delete("all")
        width, height = self.backdrop.winfo_width(), self.backdrop.winfo_height()
        rounded_polygon(self.backdrop, (1, 1, width-2, height-2), self.surface_radius,
                        fill=self.surface_fill, outline=self.surface_border)


class RoundedEntry(RoundedSurface):
    def __init__(self, parent, *, textvariable, state="normal", width=25, **kwargs):
        super().__init__(parent, fill="#ffffff", radius=18, padding=10, **kwargs)
        self.columnconfigure(0, weight=1)
        self.field = tk.Entry(self, textvariable=textvariable, state=state, width=width, relief="flat", bd=0,
                              highlightthickness=0, background="#ffffff", readonlybackground="#ffffff",
                              disabledbackground="#ffffff", font=("Segoe UI", 10), disabledforeground="#89939d")
        self.field.grid(row=0, column=0, sticky="ew", padx=4)
        self.backdrop.bind("<Button-1>", lambda _: self.field.focus_set())

    def configure(self, cnf=None, **kwargs):
        if hasattr(self, "field"):
            field_options = {key: kwargs.pop(key) for key in tuple(kwargs) if key in {"state", "textvariable", "width"}}
            if field_options:
                self.field.configure(**field_options)
        if kwargs or cnf:
            return super().configure(cnf, **kwargs)
    config = configure

    def bind(self, sequence=None, func=None, add=None):
        return self.field.bind(sequence, func, add) if hasattr(self, "field") else super().bind(sequence, func, add)

    def event_generate(self, sequence, **kwargs):
        return self.field.event_generate(sequence, **kwargs)

    def get(self):
        return self.field.get()

    def focus_set(self):
        return self.field.focus_set()


class RoundedCombobox(RoundedEntry):
    def __init__(self, parent, *, textvariable, values=(), state="normal", width=25):
        RoundedSurface.__init__(self, parent, fill="#ffffff", radius=18, padding=10)
        self.columnconfigure(0, weight=1)
        self.field = ttk.Combobox(self, textvariable=textvariable, values=values, state=state, width=width, style="Rounded.TCombobox")
        self.field.grid(row=0, column=0, sticky="ew", padx=4)
        self.backdrop.bind("<Button-1>", lambda _: self.field.focus_set())

    def configure(self, cnf=None, **kwargs):
        if hasattr(self, "field") and "values" in kwargs:
            self.field.configure(values=kwargs.pop("values"))
        return super().configure(cnf, **kwargs)
    config = configure


class RoundedButton(tk.Canvas):
    def __init__(self, parent, *, text, command=None, state="normal", **kwargs):
        self.text = text
        self.command = command
        self.button_state = state
        self.hover = False
        self.label_font = font.Font(family="Segoe UI", size=10, weight="bold")
        width = self.label_font.measure(text) + 38
        super().__init__(parent, width=width, height=48, highlightthickness=0, bd=0, background="#f3f6f8", takefocus=True, **kwargs)
        self.bind("<Enter>", lambda _: self.highlight(True))
        self.bind("<Leave>", lambda _: self.highlight(False))
        self.bind("<ButtonRelease-1>", self.activate)
        self.bind("<Return>", self.activate)
        self.bind("<space>", self.activate)
        self.bind("<FocusIn>", lambda _: self.draw())
        self.bind("<FocusOut>", lambda _: self.draw())
        self.draw()

    def configure(self, cnf=None, **kwargs):
        if "state" in kwargs:
            self.button_state = kwargs.pop("state")
            self.draw()
        if kwargs or cnf:
            return super().configure(cnf, **kwargs)
    config = configure

    def rounded(self, x1, y1, x2, y2, radius, color):
        return self.create_polygon(x1+radius,y1, x2-radius,y1, x2,y1, x2,y1+radius,
                                   x2,y2-radius, x2,y2, x2-radius,y2, x1+radius,y2,
                                   x1,y2, x1,y2-radius, x1,y1+radius, x1,y1,
                                   smooth=True, fill=color, outline=color)

    def draw(self):
        self.delete("all")
        width = int(self.cget("width"))
        disabled = self.button_state == "disabled"
        self.configure_cursor(disabled)
        self.rounded(3, 6, width-1, 46, 19, "#dde3e9" if disabled else "#c6d2dc")
        color = "#e3e9ee" if disabled else ("#346d85" if self.hover else "#24556b")
        self.rounded(0, 1, width-4, 41, 19, color)
        self.create_text((width-4)/2, 21, text=self.text, font=self.label_font, fill="#8795a0" if disabled else "#ffffff")
        has_focus = False
        try:
            has_focus = (self.focus_get() == self)
        except Exception:
            has_focus = False
        if has_focus and not disabled:
            self.create_line(16, 35, width-20, 35, fill="#9fd5e7", width=2)

    def configure_cursor(self, disabled):
        super().configure(cursor="arrow" if disabled else "hand2")

    def highlight(self, value):
        self.hover = value
        self.draw()

    def activate(self, event=None):
        if self.button_state != "disabled" and self.command:
            self.focus_set()
            self.command()
