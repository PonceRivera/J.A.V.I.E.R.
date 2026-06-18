# J.A.V.I.E.R. — Documentación Técnica Completa

**Proyecto:** Asistente de voz con IA para el taller de robótica FRC  
**Equipo:** 8290 Jaegers (México)  
**Ubicación del proyecto:** `C:\Users\Crist\.gemini\antigravity-ide\scratch\javier_bot`  
**Fecha de creación:** Junio 2026  
**Python requerido:** 3.12 (el entorno virtual usa esta versión)

---

## 1. ¿Qué es J.A.V.I.E.R.?

Un asistente de voz estilo JARVIS (Iron Man) diseñado para el taller de robótica del equipo 8290 Jaegers. Puede:

- **Escuchar por micrófono** y transcribir lo que el usuario dice (español de México).
- **Responder con voz hiperrealista** usando ElevenLabs (voz "Callum", ronca y calmada).
- **Buscar herramientas y piezas** en el inventario del taller (archivo Excel).
- **Responder preguntas generales** sobre robótica, FRC, programación, etc. usando OpenCode AI (modelo big-pickle).
- **Mostrar una interfaz gráfica** estilo terminal/hacker con indicadores de estado de color.

---

## 2. Arquitectura del Proyecto

```
javier_bot/
├── main.py              # Punto de entrada + lógica de decisiones
├── motor_voz.py         # Voz (ElevenLabs TTS) + Micrófono (SpeechRecognition)
├── cerebro.py           # Conexión a Google Gemini (IA generativa)
├── base_datos.py        # Lectura del inventario (Excel con pandas)
├── gui.py               # Interfaz gráfica (Tkinter)
├── Nuevo inventario 2026.xlsx  # Inventario REAL del taller (enero 2026)
├── inventario.csv       # Inventario de prueba original (ya no se usa)
├── requirements.txt     # Dependencias
├── venv/                # Entorno virtual Python 3.12
├── test.py              # Script de prueba (obsoleto)
└── test2.py             # Script de prueba (obsoleto)
```

### Diagrama de flujo

```
Usuario habla por micrófono
         │
         ▼
   motor_voz.escuchar_comando()  ← Google Speech API (es-MX)
         │
         ▼
   main.procesar_comando(texto)
         │
         ├── ¿Contiene "salir"/"apagar"? → Apagar
         │
         ├── ¿Contiene palabras de inventario?
         │       │
         │       ▼
         │   base_datos.buscar_articulo()  ← Lee Excel
         │       │
         │       ├── Encontrado → Responde con datos del Excel
         │       └── No encontrado → Pasa a Gemini como respaldo
         │
         └── Pregunta general → cerebro.pensar_respuesta()  ← Google Gemini
                                         │
                                         ▼
                               motor_voz.hablar(respuesta)  ← ElevenLabs TTS
                                         │
                                         ▼
                                  Reproduce audio por bocinas
```

---

## 3. Descripción de cada Archivo

### `main.py` — Cerebro de decisiones

- **Punto de entrada:** Cuando se ejecuta, lanza la GUI (`gui.py`).
- **`procesar_comando(comando)`:** Recibe texto del usuario y decide qué hacer:
  1. Si contiene "salir", "apagar" o "descansa" → Apaga JAVIER.
  2. Si contiene palabras de inventario (ver lista abajo) → Busca en el Excel.
  3. Si el inventario no encuentra nada → Pasa la pregunta a Gemini como respaldo.
  4. Si no es pregunta de inventario → Va directo a Gemini.
- **`iniciar_javier(callback_chat)`:** Bucle infinito que escucha → procesa → repite. Acepta un callback para escribir en el chat de la GUI.

**Palabras clave de inventario reconocidas:**
`dónde está`, `dónde están`, `donde esta`, `donde estan`, `busca`, `encuentra`, `dónde quedó`, `cuántas`, `cuantas`, `cuántos`, `cuantos`, `hay`, `tenemos`, `tienen`

**Palabras de relleno que se limpian del comando:**
`el`, `la`, `los`, `las`, `un`, `una`, `actualmente`, `ahora`, `en este momento`, `disponibles`, `en el taller`, `en inventario`, `qué`, `cuál`

---

### `motor_voz.py` — Oídos y Boca

**Voz (ElevenLabs):**
- API Key: `sk_5fcab749241fbfb268dbfa41c8036d814e5c5f78576e187b`
- Voice ID: `N2lVS1w4EtoT3dr4eOWO` (Callum — voz ronca y calmada)
- Modelo: `eleven_turbo_v2_5` (el más rápido disponible)
- Optimización de latencia activada (`optimize_streaming_latency=3`)
- **Regla:** Antes de enviar texto a ElevenLabs, reemplaza "J.A.V.I.E.R." por "Javier" para que la voz lo diga de forma natural.
- **Regla:** Usa archivos temporales con nombre único (`temp_{uuid}.mp3`) para evitar conflictos de `Permission denied`.
- **Regla:** Reproduce audio usando la API nativa de Windows (`ctypes.windll.winmm.mciSendStringW`), NO usa pygame ni ninguna librería externa de audio.

**Micrófono (SpeechRecognition):**
- Usa `sr.Microphone()` + `sr.Recognizer()` + `recognize_google()` con idioma `es-MX`.
- Timeout de escucha: 8 segundos. Límite de frase: 10 segundos.
- Ajuste de ruido ambiental: 0.5 segundos antes de cada escucha.

**Anti-eco (evitar que JAVIER se escuche a sí mismo):**
- Variable global `_hablando = True/False`.
- `hablar()` pone `_hablando = True` al empezar y `False` al terminar (con 0.8s de espera extra).
- `escuchar_comando()` espera con `while _hablando: sleep(0.1)` antes de abrir el micrófono.

**Callback de estado:**
- Variable global `on_estado_cambio` que el GUI registra.
- Se llama con: `"escuchando"`, `"procesando"`, o `"listo"`.

---

### `cerebro.py` — Inteligencia Artificial (OpenCode AI)

- SDK: `openai` (cliente compatible con endpoint de OpenCode)
- Endpoint: `https://opencode.ai/zen/v1`
- API Key: Cargada desde `.env` como `OPENCODE_API_KEY`
- Modelo por defecto: `big-pickle` / Modelo Pro: `big-pickle`
- **System Instruction (personalidad):** Ver `cerebro.py` línea 129 — instrucción detallada de personalidad tipo JARVIS para FRC.
- **Tool use:** JAVIER puede ejecutar herramientas locales (inventario, TBA, WhatsApp, plugins, etc.) mediante function calling de OpenAI API.

---

### `base_datos.py` — Inventario del Taller

- Lee el archivo `Nuevo inventario 2026.xlsx` (inventario real de enero 2026).
- Usa `pandas.read_excel()` con `header=1` (la fila 0 del Excel tiene un título).
- **Columnas del Excel:** `Herramienta`, `cantidad`, `Links de producto`, `Cantidad Por Pieza`, `Cantidad Total`.
- **Columna de Ubicación:** NO existe en este Excel. Solo se reporta la cantidad.
- La búsqueda es **case-insensitive** y bidireccional (`nombre_buscado in articulo or articulo in nombre_buscado`).
- Si no encuentra el artículo, retorna un string que empieza con "Lo siento" (esto es clave para que `main.py` sepa cuándo hacer fallback a Gemini).

**Artículos disponibles en el inventario (enero 2026):**
Pinzas Mecánicas, llave 3/8, llave 1/2, juego de allen, desarmador de puntas, juego de brocas, caja de desarmadores pretul, remachadora, ponchadora, bernier, juego de dados, juego de dados con matraca, martillo de goma, limas, cuter, pinzas de corte, cepillo de alambre, segueta, pinzas de presión, llave inglesa, pinzas de presión tipo C, brocha, desarmador estrella, desarmador plano, desarmadores para dados, kit FedEx care, Nivel Torpedo, cintas métricas, Formon, desarmadores torx, desarmadores estrella, desarmadores planos, deaarmadores de cruz, llantas (negras/azules/verdes/rojas/colson de varias pulgadas), conexiones wago, discos de corte, cinta de teflon, cinta de precaución, cinta aislante, cinta doble cara, cinta canela, motores neo v1.1, Motores neo 550, taladro pretul, taladro craftman, rotomartillo craftman, pulidor, mototool, pilas, radio, caja de tornillos, caja de baleros, bompers esquineros rojos, bompers esquineros Azules.

**NO están en el inventario:** Chasis, RoboRIO, PDP/PDH, Kraken X60, Spark Max (controller sí aparece en inventario.csv viejo pero NO en el Excel nuevo), radio de FRC.

---

### `gui.py` — Interfaz Gráfica

- Framework: **Tkinter** (incluido con Python, no requiere instalación).
- Tema: Fondo negro, texto verde neón, estilo "hacker/terminal".
- Fuente: Consolas (monoespaciada).

**Componentes:**
1. Título grande "J.A.V.I.E.R." (cambia de color según el estado).
2. Subtítulo "Asistente de Taller FRC".
3. Área de chat (ScrolledText) donde aparece el historial.
4. Indicador de estado con círculo de color.
5. Barra de texto para input manual (backup del micrófono).
6. Etiqueta de ayuda.

**Indicador de colores:**
| Color | Código Hex | Significado |
|-------|-----------|-------------|
| Verde | `#00ff00` | EN LÍNEA (listo para escuchar) |
| Azul marino | `#1a4fd6` | ESCUCHANDO (micrófono abierto) |
| Amarillo | `#ffaa00` | PROCESANDO (pensando respuesta) |

**Regla de threading:** Toda la lógica de voz corre en un thread daemon separado. Las actualizaciones de la GUI se hacen con `root.after(0, callback)` para evitar conflictos con el hilo principal de Tkinter.

---

## 4. Dependencias y Entorno

**Entorno virtual:** `venv/` creado con `py -3.12 -m venv venv`

**Librerías instaladas:**
```
pyaudio              # Captura de micrófono (requiere Python 3.12, NO funciona en 3.14)
SpeechRecognition    # Transcripción de voz (Google Speech API)
pandas               # Lectura de Excel
openpyxl             # Motor de lectura .xlsx para pandas
requests             # Comunicación HTTP con ElevenLabs
edge-tts             # TTS alternativo (instalado pero NO se usa actualmente)
elevenlabs           # SDK de ElevenLabs (instalado pero NO se usa, usamos requests directos)
google-genai         # SDK nuevo de Google Gemini
```

---

## 5. Cómo Ejecutar

```powershell
cd C:\Users\Crist\.gemini\antigravity-ide\scratch\javier_bot
.\venv\Scripts\python.exe main.py
```

> **IMPORTANTE:** Usar `.\venv\Scripts\python.exe` (NO `python` a secas) para asegurar que usa Python 3.12 del entorno virtual.

---

## 6. Reglas y Decisiones de Diseño Importantes

1. **Python 3.12 obligatorio.** PyAudio no tiene wheel para Python 3.14. El entorno virtual fue creado específicamente con `py -3.12`.
2. **ElevenLabs por HTTP directo.** El SDK oficial de ElevenLabs (`elevenlabs` pip) no funcionó correctamente con Python 3.14/3.12. Se usa `requests.post()` directamente contra la API REST.
3. **Audio nativo de Windows.** Se usa `ctypes.windll.winmm.mciSendStringW` para reproducir MP3. No se usa pygame (incompatible con 3.14) ni ningún reproductor externo.
4. **OpenCode AI como cerebro.** Se usa el cliente OpenAI-compatible apuntando a `https://opencode.ai/zen/v1` con el modelo `big-pickle`. Soporta function calling para herramientas locales.
5. **Evitar emojis en prints.** La consola de Windows (cp1252) no soporta emojis Unicode. Se usan marcadores ASCII como `[MIC]` y `[OK]`.
6. **Texto "J.A.V.I.E.R." → "Javier" antes de TTS.** Para que la voz no deletree cada letra.
7. **Archivos temporales únicos.** Cada audio generado usa `temp_{uuid}.mp3` para evitar `Permission denied` cuando hay respuestas consecutivas.
8. **Anti-eco con bandera `_hablando`.** El micrófono no se abre hasta que JAVIER termine de hablar + 0.8s de pausa.
9. **Fallback a Gemini.** Si el inventario no encuentra un artículo, la pregunta se reenvía a Gemini en lugar de decir "no encontré".
10. **Gemini no inventa inventario.** El system instruction le prohíbe expresamente inventar cantidades de piezas.

---

## 7. Problemas Conocidos y Soluciones Aplicadas

| Problema | Causa | Solución |
|----------|-------|----------|
| `ModuleNotFoundError: pygame` | pygame incompatible con Python 3.14 | Se eliminó pygame; se usa ctypes nativo de Windows |
| `Permission denied: temp.mp3` | Dos audios intentan usar el mismo archivo | Se usa UUID en el nombre del archivo temporal |
| JAVIER se escucha a sí mismo | El micrófono captura la salida de las bocinas | Bandera `_hablando` + pausa de 0.8s |
| Google reconoce "robó río" en vez de "RoboRIO" | Google Speech interpreta fonéticamente | Limitación del reconocimiento de voz de Google |
| Gemini inventa cantidades | Sin instrucciones, Gemini alucina datos | System instruction prohíbe inventar datos de inventario |
| `oimport requests` (typo) | Error de edición | Se corrigió a `import requests` |
| Emojis rompen la consola | Windows cp1252 no soporta Unicode | Reemplazados por `[MIC]`, `[OK]` |

---

## 8. Mejoras Futuras Pendientes

- [ ] Agregar columna "Ubicación" al Excel para responder "dónde está X".
- [ ] Agregar componentes del robot al inventario (RoboRIO, Kraken X60, chasis, etc.).
- [ ] Migrar el inventario a Google Sheets para edición desde celular.
- [ ] Crear un Bot de Discord conectado al mismo código.
- [ ] Implementar wake word real ("Javier") para activación por voz.
- [ ] Evaluar usar Whisper local en vez de Google Speech para funcionar sin internet.

---

## 9. API Keys en Uso

| Servicio | Key | Plan |
|----------|-----|------|
| ElevenLabs (voz) | Cargada desde `.env` como `ELEVENLABS_API_KEY` | Gratuito (10,000 chars/mes) |
| OpenCode AI (cerebro) | Cargada desde `.env` como `OPENCODE_API_KEY` | Gratuito / Pro |
| The Blue Alliance (TBA) | Cargada desde `.env` como `TBA_API_KEY` | Gratuito |

> **Nota de seguridad:** Las API keys están hardcodeadas en los archivos Python. Para producción se recomienda moverlas a variables de entorno.
