import tkinter as tk
import customtkinter as ctk
import threading
import math
import random
import socket
import time as _time
from datetime import datetime
import psutil
import motor_voz
from main import procesar_comando, iniciar_javier
from motor_voz import hablar

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ─── Paleta de colores ────────────────────────────────────────────
BG          = "#050508"
CYAN        = "#00E5FF"
CYAN_DIM    = "#004455"
CYAN_DARK   = "#001a22"
GREEN       = "#00FF88"
ORANGE      = "#FF8800"
YELLOW      = "#FFCC00"
RED         = "#FF3333"
GRID_COLOR  = "#0a1a1f"
HUD_COLOR   = "#003344"



class JavierGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("J.A.V.I.E.R. OS v3.0 — JAEGERS60 FRC #8290")
        
        # Configuración de Ventana
        self.screen_w = 1280
        self.screen_h = 800
        self.root.geometry(f"{self.screen_w}x{self.screen_h}")
        self.root.configure(fg_color=BG)
        self.root.resizable(False, False)
        
        # Tecla para salir
        self.root.bind("<Escape>", lambda e: self.salir())

        # Estado interno
        self.estado_actual   = "listo"
        self.anim_tick       = 0
        self.anim_running    = True
        self.grid_offset     = 0
        self.scan_y          = 0
        self.ticker_x        = self.screen_w
        self.bar_heights     = [5] * 22
        self.reactor_x       = 250
        self.reactor_target_x = 250

        # Paletas por estado
        self.PALETAS = {
            "listo":       {"scan": GREEN,  "core": "#004444", "glow": CYAN,   "mid": "#008888"},
            "escuchando":  {"scan": CYAN,   "core": "#003388", "glow": "#00CCFF", "mid": "#0055BB"},
            "procesando":  {"scan": ORANGE, "core": "#883300", "glow": ORANGE,  "mid": "#BB5500"},
            "hablando":    {"scan": GREEN,  "core": "#004422", "glow": GREEN,   "mid": "#007755"},
        }

        self._build_ui()
        motor_voz.on_estado_cambio = self.actualizar_estado
        self._animar()
        self._actualizar_hud()  # Iniciar monitoreo de HUD
        threading.Thread(target=self.arrancar_javier, daemon=True).start()

    # ══════════════════════════════════════════════════════════════
    # CONSTRUCCIÓN DE LA INTERFAZ
    # ══════════════════════════════════════════════════════════════

    def _build_ui(self):
        w, h = self.screen_w, self.screen_h
        
        # ── Canvas de fondo (cuadrícula + scanlines + HUD corners) ──
        self.bg_canvas = tk.Canvas(self.root, width=w, height=h,
                                   bg=BG, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0)

        # Dibujar cuadrícula fija (líneas base)
        for x in range(0, w, 40):
            self.bg_canvas.create_line(x, 0, x, h, fill=GRID_COLOR, width=1)
        for y in range(0, h, 40):
            self.bg_canvas.create_line(0, y, w, y, fill=GRID_COLOR, width=1)

        # HUD corners — superior izquierdo
        self.bg_canvas.create_line(0, 0, 80, 0,  fill=CYAN_DIM, width=2)
        self.bg_canvas.create_line(0, 0, 0,  80, fill=CYAN_DIM, width=2)
        self.bg_canvas.create_line(15, 15, 60, 15, fill=CYAN_DIM, width=1)
        self.bg_canvas.create_line(15, 15, 15, 60, fill=CYAN_DIM, width=1)
        self.hud_sys = self.bg_canvas.create_text(22, 22, text="SYS:...", fill=CYAN_DIM,
                                   font=("Consolas", 7), anchor="nw")

        # HUD corners — superior derecho
        self.bg_canvas.create_line(w, 0, w-80, 0,  fill=CYAN_DIM, width=2)
        self.bg_canvas.create_line(w, 0, w, 80, fill=CYAN_DIM, width=2)
        self.bg_canvas.create_line(w-15, 15, w-60, 15, fill=CYAN_DIM, width=1)
        self.bg_canvas.create_line(w-15, 15, w-15, 60, fill=CYAN_DIM, width=1)
        self.hud_mem = self.bg_canvas.create_text(w-20, 22, text="MEM:...", fill=CYAN_DIM,
                                   font=("Consolas", 7), anchor="ne")

        # HUD corners — inferior izquierdo
        self.bg_canvas.create_line(0, h, 80, h,  fill=CYAN_DIM, width=2)
        self.bg_canvas.create_line(0, h, 0,  h-80,  fill=CYAN_DIM, width=2)
        self.hud_net = self.bg_canvas.create_text(22, h-7, text="NET:...", fill=CYAN_DIM,
                                   font=("Consolas", 7), anchor="sw")

        # HUD corners — inferior derecho
        self.bg_canvas.create_line(w, h, w-80, h, fill=CYAN_DIM, width=2)
        self.bg_canvas.create_line(w, h, w, h-80, fill=CYAN_DIM, width=2)
        self.hud_ai = self.bg_canvas.create_text(w-20, h-7, text="AI:...", fill=CYAN_DIM,
                                   font=("Consolas", 7), anchor="se")

        # Línea de escaneo (scanline) animada
        self.scanline = self.bg_canvas.create_line(0, 0, w, 0, fill="#003322", width=3)

        # ── Reactor Arc ──────────────────────────────────────────
        self.reactor_canvas = tk.Canvas(self.root, width=200, height=200,
                                        bg=BG, highlightthickness=0)
        self.reactor_canvas.place(x=self.reactor_x, y=h//2 - 250)

        self.r_outer  = self.reactor_canvas.create_oval(  5,  5, 195, 195, outline=CYAN_DIM, width=2)
        self.r_mid    = self.reactor_canvas.create_oval( 22, 22, 178, 178, outline=HUD_COLOR, width=7)
        self.r_inner  = self.reactor_canvas.create_oval( 42, 42, 158, 158, outline=CYAN_DIM, width=2)
        self.r_core   = self.reactor_canvas.create_oval( 62, 62, 138, 138, fill="#002222", outline=CYAN, width=2)
        self.r_scan   = self.reactor_canvas.create_arc(  22, 22, 178, 178,
                                                         start=0, extent=70,
                                                         outline=GREEN, width=3, style="arc")
        self.r_glow   = self.reactor_canvas.create_oval( 82, 82, 118, 118, fill="#003333", outline="")
        self.r_text   = self.reactor_canvas.create_text(100, 100, text="J",
                                                         fill=CYAN, font=("Consolas", 22, "bold"))

        # ── Contenedor Dinámico Izquierdo (Para el título y controles) ──────────────────
        self.frame_izq = ctk.CTkFrame(self.root, fg_color="transparent", width=600, height=300)
        self.frame_izq.place(x=self.reactor_x - 200, y=h//2 - 20)

        # ── Título ────────────────────────────────────────────────
        self.lbl_titulo = ctk.CTkLabel(self.frame_izq, text="J.A.V.I.E.R.  O S  v 3 . 0",
                                       font=("Consolas", 22, "bold"), text_color=CYAN)
        self.lbl_titulo.place(x=300, y=20, anchor="center")

        self.lbl_sub = ctk.CTkLabel(self.frame_izq,
                                    text="Joint Automated Vehicle Intelligence Enabled Robot",
                                    font=("Consolas", 8), text_color=CYAN_DIM)
        self.lbl_sub.place(x=300, y=42, anchor="center")

        self.lbl_estado = ctk.CTkLabel(self.frame_izq,
                                       text="[ S I S T E M A   E N   L Í N E A ]",
                                       font=("Consolas", 12, "bold"), text_color=GREEN)
        self.lbl_estado.place(x=300, y=65, anchor="center")

        # Separador decorativo
        self.separador = tk.Canvas(self.frame_izq, width=500, height=2, bg=BG, highlightthickness=0)
        self.separador.place(x=50, y=85)
        self.separador.create_line(0, 1, 500, 1, fill=CYAN_DIM, width=1)

        # ── Visualizador de audio (barras) ────────────────────────
        self.viz_canvas = tk.Canvas(self.frame_izq, width=440, height=50,
                                    bg=BG, highlightthickness=0)
        self.viz_canvas.place(x=80, y=95)
        self.viz_bars = []
        for i in range(22):
            x1 = i * 20 + 2
            bar = self.viz_canvas.create_rectangle(x1, 48, x1 + 14, 48,
                                                   fill=CYAN_DIM, outline="")
            self.viz_bars.append(bar)

        # ── Nueva Gran Consola Derecha (Matrix/Logs) ───────────────────────────
        self.consola_w = w // 2 - 100
        self.consola_h = h - 200
        self.consola_frame = ctk.CTkFrame(self.root, fg_color="#07070F", border_color=CYAN_DIM, border_width=1, corner_radius=8, width=self.consola_w, height=self.consola_h)
        self.consola_frame.place(x=w // 2 + 50, y=100) # Inicia siempre visible
        
        lbl_con = ctk.CTkLabel(self.consola_frame, text="█ CONSOLA DE SISTEMAS EN TIEMPO REAL", font=("Consolas", 14, "bold"), text_color=GREEN)
        lbl_con.place(x=15, y=10)
        
        self.consola_area = ctk.CTkTextbox(
            self.consola_frame, width=self.consola_w - 30, height=self.consola_h - 50,
            font=("Consolas", 12), fg_color="#030308",
            text_color=GREEN, border_color=CYAN_DIM,
            border_width=0, corner_radius=4,
            scrollbar_button_color=CYAN_DIM
        )
        self.consola_area.place(x=15, y=40)
        self.consola_area.configure(state="disabled")

        # ── Chat / Log (Oculto, reemplazado por la consola) ───────────────────
        self.chat_area = None

        # ── Botón PTT ─────────────────────────────────────────────
        self.btn_ptt = ctk.CTkButton(
            self.frame_izq, text="◉  MANTENER PRESIONADO PARA HABLAR",
            font=("Consolas", 13, "bold"), width=500, height=54,
            fg_color="#002233", hover_color="#005577",
            border_color=CYAN, border_width=2,
            corner_radius=8, text_color=CYAN
        )
        self.btn_ptt.place(x=300, y=190, anchor="center")
        self.btn_ptt.bind("<ButtonPress-1>",   self.on_ptt_press)
        self.btn_ptt.bind("<ButtonRelease-1>", self.on_ptt_release)

        # ── Entrada manual ────────────────────────────────────────
        self.lbl_prompt = ctk.CTkLabel(self.frame_izq, text="JAVIER>",
                                       font=("Consolas", 12, "bold"), text_color=CYAN_DIM)
        self.lbl_prompt.place(x=30, y=240)

        self.entrada_comando = ctk.CTkEntry(
            self.frame_izq, font=("Consolas", 12), width=480, height=36,
            placeholder_text="Escribe un comando...",
            fg_color="#0A0A14", text_color=CYAN,
            border_color=CYAN_DIM, placeholder_text_color="#224444"
        )
        self.entrada_comando.place(x=90, y=240)
        self.entrada_comando.bind("<Return>", self.enviar_comando_texto)

        # ── Ticker inferior ───────────────────────────────────────
        self.bg_canvas.create_line(0, h-50, w, h-50, fill=CYAN_DIM, width=1)
        self.ticker_canvas = tk.Canvas(self.root, width=w-40, height=22,
                                       bg=BG, highlightthickness=0)
        self.ticker_canvas.place(x=20, y=h-42)
        self.ticker_text_id = self.ticker_canvas.create_text(
            w, 11, text="", fill=CYAN_DIM,
            font=("Consolas", 9), anchor="w"
        )

    # ══════════════════════════════════════════════════════════════
    # ANIMACIONES (~30fps)
    # ══════════════════════════════════════════════════════════════

    def _animar(self):
        if not self.anim_running:
            return
        t = self.anim_tick
        paleta = self.PALETAS.get(self.estado_actual, self.PALETAS["listo"])

        # 1) Arc scanner giratorio
        vel  = {"listo": 2, "escuchando": 6, "procesando": 11, "hablando": 4}[self.estado_actual]
        ext  = {"listo": 55, "escuchando": 90, "procesando": 130, "hablando": 70}[self.estado_actual]
        ang  = (t * vel) % 360
        self.reactor_canvas.itemconfig(self.r_scan, start=ang, extent=ext, outline=paleta["scan"])

        # 2) Glow central pulsante
        pulso = (math.sin(t * 0.09) + 1) / 2
        r = int(14 + 6 * pulso)
        cx = cy = 100
        self.reactor_canvas.coords(self.r_glow, cx-r, cy-r, cx+r, cy+r)
        glow_c = self._lerp_color("#002222", paleta["glow"], pulso)
        self.reactor_canvas.itemconfig(self.r_glow, fill=glow_c)

        # 3) Anillo central con respiración
        mid_c = self._lerp_color(CYAN_DIM, paleta["mid"], (math.sin(t*0.05)+1)/2)
        self.reactor_canvas.itemconfig(self.r_mid, outline=mid_c)
        txt_a = int(150 + 105 * pulso)
        self.reactor_canvas.itemconfig(self.r_text, fill=f"#00{txt_a:02x}{txt_a:02x}")

        # 3.5) Consola y reactor permanentemente visibles para poder leer el chat/logs en todo momento
        self.reactor_target_x = 250

        self.reactor_x += (self.reactor_target_x - self.reactor_x) * 0.1
        self.reactor_canvas.place(x=self.reactor_x)
        self.frame_izq.place(x=self.reactor_x - 200)

        # 4) Scanline descendente
        self.scan_y = (self.scan_y + 2) % self.screen_h
        self.bg_canvas.coords(self.scanline, 0, self.scan_y, self.screen_w, self.scan_y)

        # 5) Visualizador de audio
        target_h = 3
        if self.estado_actual == "hablando":
            target_h = random.randint(8, 45)
        elif self.estado_actual == "escuchando":
            target_h = random.randint(4, 18)
        elif self.estado_actual == "procesando":
            target_h = int(8 + 12 * abs(math.sin(t * 0.15 + random.uniform(0, 1))))

        bar_color = paleta["scan"]
        for i, bar in enumerate(self.viz_bars):
            self.bar_heights[i] = self.bar_heights[i] * 0.7 + target_h * 0.3 + random.uniform(-1, 1)
            h = max(2, int(self.bar_heights[i]))
            x1 = i * 20 + 2
            self.viz_canvas.coords(bar, x1, 50 - h, x1 + 14, 50)
            self.viz_canvas.itemconfig(bar, fill=bar_color)

        # 6) Ticker inferior
        now = datetime.now()
        ticker_str = (f"  ◈  {now.strftime('%H:%M:%S')}  ·  {now.strftime('%d/%m/%Y')}  ·  "
                      f"EQUIPO FRC #8290 JAEGERS60  ·  CETIS 60  ·  RAMOS ARIZPE, COAH.  ·  "
                      f"SISTEMA: {self.estado_actual.upper()}  ◈  ")
        self.ticker_x -= 2
        self.ticker_canvas.coords(self.ticker_text_id, self.ticker_x, 11)
        self.ticker_canvas.itemconfig(self.ticker_text_id, text=ticker_str * 2)
        # Reiniciar cuando salga completamente del canvas
        text_bbox = self.ticker_canvas.bbox(self.ticker_text_id)
        if text_bbox and text_bbox[2] < 0:
            self.ticker_x = self.screen_w

        self.anim_tick += 1
        self.root.after(33, self._animar)

    def _lerp_color(self, a: str, b: str, t: float) -> str:
        t = max(0.0, min(1.0, t))
        try:
            ra,ga,ba = int(a[1:3],16), int(a[3:5],16), int(a[5:7],16)
            rb,gb,bb = int(b[1:3],16), int(b[3:5],16), int(b[5:7],16)
            return f"#{int(ra+(rb-ra)*t):02x}{int(ga+(gb-ga)*t):02x}{int(ba+(bb-ba)*t):02x}"
        except Exception:
            return b

    def _actualizar_hud(self):
        """Lee estado real del sistema y actualiza los indicadores HUD cada 3 segundos."""
        def _task():
            # SYS: CPU
            cpu = psutil.cpu_percent(interval=0.3)
            sys_txt  = f"SYS:{cpu:.0f}%CPU"
            sys_col  = GREEN if cpu < 75 else ORANGE if cpu < 90 else RED

            # MEM: RAM
            ram = psutil.virtual_memory().percent
            mem_txt  = f"MEM:{ram:.0f}%RAM"
            mem_col  = GREEN if ram < 75 else ORANGE if ram < 90 else RED

            # NET: internet
            try:
                socket.setdefaulttimeout(2)
                socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
                net_txt, net_col = "NET:ACTIVA", GREEN
            except Exception:
                net_txt, net_col = "NET:OFFLINE", RED

            # AI: estado de la API actual
            from cerebro import indice_key, API_KEYS
            ai_txt = f"AI:KEY#{indice_key+1}/{len(API_KEYS)}"
            ai_col = GREEN if self.estado_actual != "procesando" else ORANGE

            def _apply():
                self.bg_canvas.itemconfig(self.hud_sys, text=sys_txt, fill=sys_col)
                self.bg_canvas.itemconfig(self.hud_mem, text=mem_txt, fill=mem_col)
                self.bg_canvas.itemconfig(self.hud_net, text=net_txt, fill=net_col)
                self.bg_canvas.itemconfig(self.hud_ai,  text=ai_txt,  fill=ai_col)
            self.root.after(0, _apply)

        threading.Thread(target=_task, daemon=True).start()
        if self.anim_running:
            self.root.after(3000, self._actualizar_hud)

    # ══════════════════════════════════════════════════════════════
    # ESTADOS
    # ══════════════════════════════════════════════════════════════

    def on_ptt_press(self, event):
        motor_voz.PTT_PRESIONADO = True
        self.btn_ptt.configure(fg_color="#005577", text="◉  [ GRABANDO AUDIO... ]")
        self.estado_actual = "escuchando"

    def on_ptt_release(self, event):
        motor_voz.PTT_PRESIONADO = False
        self.btn_ptt.configure(fg_color="#002233", text="◉  MANTENER PRESIONADO PARA HABLAR")
        self.estado_actual = "procesando"

    def actualizar_estado(self, estado):
        def _update():
            self.estado_actual = estado
            textos = {
                "escuchando": ("[ E S C U C H A N D O . . . ]", CYAN),
                "procesando":  ("[ P R O C E S A N D O . . . ]", ORANGE),
                "hablando":    ("[ H A B L A N D O . . . ]",     GREEN),
                "listo":       ("[ S I S T E M A   E N   L Í N E A ]", GREEN),
            }
            txt, color = textos.get(estado, textos["listo"])
            self.lbl_estado.configure(text=txt, text_color=color)
        self.root.after(0, _update)

    # ══════════════════════════════════════════════════════════════
    # CHAT, CONSOLA Y COMANDOS
    # ══════════════════════════════════════════════════════════════

    def escribir_en_chat(self, emisor, mensaje):
        def _write():
            self.consola_area.configure(state="normal")
            
            # Formatear el texto tipo Matrix si es JAVIER
            if emisor == "Tú":
                self.consola_area.insert("end", f"\n[USUARIO]> {mensaje}\n", "user")
            elif emisor == "J.A.V.I.E.R.":
                self.consola_area.insert("end", f"\n[JAVIER_OS]> {mensaje}\n", "ai")
            else:
                self.consola_area.insert("end", f"[{emisor}] {mensaje}\n", "system")
                
            self.consola_area.see("end")
            self.consola_area.configure(state="disabled")
        self.root.after(0, _write)
        
    def salir(self):
        self.anim_running = False
        self.root.destroy()

    def arrancar_javier(self):
        motor_voz.on_estado_cambio = self.actualizar_estado
        msg = "Sistemas en línea. Soy Javier. ¿En qué te puedo ayudar?"
        self.escribir_en_chat("J.A.V.I.E.R.", msg)
        self.actualizar_estado("hablando")
        hablar(msg)
        self.actualizar_estado("listo")
        iniciar_javier(callback_chat=self.escribir_en_chat)

    def procesar_respuesta_texto(self, comando):
        self.entrada_comando.configure(state="disabled")
        self.actualizar_estado("procesando")
        corriendo = procesar_comando(comando)
        self.actualizar_estado("listo")
        if not corriendo:
            self.anim_running = False
            self.root.quit()
        self.root.after(0, lambda: self.entrada_comando.configure(state="normal"))
        self.root.after(0, self.entrada_comando.focus)

    def enviar_comando_texto(self, event):
        comando = self.entrada_comando.get().strip()
        if comando:
            self.escribir_en_chat("Tú", comando)
            self.entrada_comando.delete(0, "end")
            threading.Thread(target=self.procesar_respuesta_texto, args=(comando,), daemon=True).start()


if __name__ == "__main__":
    app = ctk.CTk()
    gui = JavierGUI(app)
    app.mainloop()
