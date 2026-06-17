"""
splash.py — Pantalla de carga JAVIER v3.0
Muestra verificaciones animadas de sistema antes de abrir la GUI principal.
"""
import tkinter as tk
import threading
import socket
import time
import psutil

BG       = "#050508"
CYAN     = "#00E5FF"
CYAN_DIM = "#004455"
GREEN    = "#00FF88"
RED      = "#FF3333"
ORANGE   = "#FF8800"


def _check_sys():
    """CPU y RAM."""
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    if cpu < 90 and ram < 90:
        return "OK", f"CPU {cpu:.0f}%  RAM {ram:.0f}%"
    return "WARN", f"CPU {cpu:.0f}%  RAM {ram:.0f}% — RECURSOS ALTOS"


def _check_net():
    """Verifica conexión a internet."""
    try:
        socket.setdefaulttimeout(3)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return "OK", "CONEXIÓN ACTIVA"
    except Exception:
        return "FAIL", "SIN CONEXIÓN A INTERNET"


def _check_mem():
    """RAM disponible."""
    mem = psutil.virtual_memory()
    avail_gb = mem.available / (1024 ** 3)
    total_gb = mem.total / (1024 ** 3)
    if mem.percent < 85:
        return "OK", f"{avail_gb:.1f} GB LIBRE / {total_gb:.1f} GB TOTAL"
    return "WARN", f"MEMORIA BAJA: {avail_gb:.1f} GB LIBRE"


def _check_ai():
    """Verifica si la API de OpenCode responde."""
    try:
        from cerebro import client
        # Petición mínima para verificar conectividad
        client.models.list()
        return "OK", "OPENCODE API CONECTADA"
    except Exception as e:
        err = str(e)
        if "429" in err:
            return "WARN", "API ACTIVA — CUOTA LIMITADA"
        return "FAIL", f"API NO DISPONIBLE: {e}"


class SplashScreen:
    CHECKS = [
        ("INICIALIZANDO NÚCLEO DE IA",    None,       0.8),
        ("SYS  — VERIFICANDO HARDWARE",   _check_sys, 0.0),
        ("MEM  — ANALIZANDO MEMORIA RAM", _check_mem, 0.0),
        ("NET  — PROBANDO CONECTIVIDAD",  _check_net, 0.0),
        ("AI   — CONTACTANDO OPENCODE API", _check_ai,  0.0),
        ("CARGANDO MÓDULOS DE VOZ",       None,       0.6),
        ("INICIALIZANDO HERRAMIENTAS",    None,       0.5),
        ("CALIBRANDO REACTOR ARC",        None,       0.7),
        ("SISTEMAS LISTOS",               None,       0.4),
    ]

    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)        # Sin borde de ventana
        self.root.attributes("-topmost", True)  # Siempre encima
        W, H = 640, 420
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x  = (sw - W) // 2
        y  = (sh - H) // 2
        self.root.geometry(f"{W}x{H}+{x}+{y}")
        self.root.configure(bg=BG)

        self.canvas = tk.Canvas(self.root, width=W, height=H, bg=BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self._draw_border()
        self._draw_static()

        # Barra de progreso base
        self.bar_bg  = self.canvas.create_rectangle(40, 340, 600, 360, outline=CYAN_DIM, width=1)
        self.bar_fill= self.canvas.create_rectangle(40, 340, 40,  360, fill=CYAN_DIM, outline="")
        self.lbl_pct = self.canvas.create_text(320, 372, text="0%", fill=CYAN_DIM,
                                               font=("Consolas", 10))

        # Línea de estado actual
        self.lbl_status = self.canvas.create_text(320, 310, text="", fill=CYAN,
                                                  font=("Consolas", 11, "bold"))
        # Log de resultados
        self.log_y = 180
        self.log_items = []

        self._anim_tick = 0
        self._running = True
        self._pulse()

        threading.Thread(target=self._run_checks, daemon=True).start()
        self.root.mainloop()

    def _draw_border(self):
        c = self.canvas
        W, H = 640, 420
        # Marco exterior
        c.create_rectangle(2, 2, W-2, H-2, outline=CYAN_DIM, width=1)
        c.create_rectangle(6, 6, W-6, H-6, outline="#001a22", width=1)
        # Esquinas decorativas
        for (x1,y1,x2,y2) in [(2,2,40,2),(2,2,2,40),(W-2,2,W-40,2),(W-2,2,W-2,40),
                               (2,H-2,40,H-2),(2,H-2,2,H-40),(W-2,H-2,W-40,H-2),(W-2,H-2,W-2,H-40)]:
            c.create_line(x1,y1,x2,y2, fill=CYAN, width=2)

    def _draw_static(self):
        c = self.canvas
        c.create_text(320, 38, text="J . A . V . I . E . R .", fill=CYAN,
                      font=("Consolas", 28, "bold"))
        c.create_text(320, 72, text="Joint Automated Vehicle Intelligence Enabled Robot",
                      fill=CYAN_DIM, font=("Consolas", 8))
        c.create_text(320, 90, text="─" * 64, fill="#001a22", font=("Consolas", 7))
        c.create_text(320, 108, text="JAEGERS60  ·  FRC #8290  ·  CETIS 60  ·  RAMOS ARIZPE, COAH.",
                      fill="#003344", font=("Consolas", 9))
        c.create_text(320, 125, text="INICIANDO DIAGNÓSTICO DE SISTEMAS...",
                      fill="#004455", font=("Consolas", 9))
        # Separador
        c.create_line(40, 145, 600, 145, fill=CYAN_DIM)

    def _add_log(self, label, status, detail):
        color = {"OK": GREEN, "WARN": ORANGE, "FAIL": RED, None: CYAN_DIM}[status]
        badge = {"OK": "[ OK ]", "WARN": "[WARN]", "FAIL": "[FAIL]", None: "[  ·  ]"}[status]
        txt = f"{badge}  {label:<30} {detail}"
        self.canvas.create_text(50, self.log_y, text=txt, fill=color,
                                font=("Consolas", 10), anchor="w")
        self.log_y += 18

    def _set_progress(self, pct, status_text):
        x2 = 40 + int(560 * pct)
        self.canvas.coords(self.bar_fill, 40, 340, x2, 360)
        self.canvas.itemconfig(self.bar_fill, fill=CYAN if pct < 1.0 else GREEN)
        self.canvas.itemconfig(self.lbl_pct, text=f"{int(pct*100)}%",
                               fill=CYAN if pct < 1.0 else GREEN)
        self.canvas.itemconfig(self.lbl_status, text=status_text)

    def _pulse(self):
        if not self._running:
            return
        t = self._anim_tick
        # Hacer que la barra de progreso tenga un brillo que va y viene
        alpha = int(40 + 20 * abs((t % 30) - 15) / 15)
        scan_color = f"#00{alpha:02x}{alpha+10:02x}"
        # Pequeño scanner horizontal en la barra
        scan_x = 40 + (t * 8) % 560
        # Solo actualizar si la barra aún no está al 100%
        self._anim_tick += 1
        self.root.after(60, self._pulse)

    def _run_checks(self):
        n = len(self.CHECKS)
        for i, (label, fn, wait) in enumerate(self.CHECKS):
            self.root.after(0, lambda l=label, p=i/n: self._set_progress(p, l + "..."))
            time.sleep(max(wait, 0.1))

            if fn:
                status, detail = fn()
            else:
                status, detail = None, "COMPLETADO"

            self.root.after(0, lambda l=label, s=status, d=detail: self._add_log(l, s, d))
            time.sleep(0.15)

        self.root.after(0, lambda: self._set_progress(1.0, "▸  TODOS LOS SISTEMAS OPERATIVOS  ◂"))
        time.sleep(1.2)
        self.root.after(0, self._close)

    def _close(self):
        self._running = False
        self.root.destroy()


def mostrar_splash():
    """Muestra la pantalla de carga. Bloquea hasta que termina."""
    SplashScreen()
