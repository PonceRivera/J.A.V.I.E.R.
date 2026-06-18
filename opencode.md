# J.A.V.I.E.R. — Análisis y Mejoras por OpenCode

**Fecha:** Junio 2026  
**Proyecto:** Asistente de voz con IA para taller de robótica FRC #8290 Jaegers  
**Autor del análisis:** OpenCode AI

---

## Índice

1. [Resumen del Análisis](#1-resumen-del-análisis)
2. [Mejora #1 — Seguridad: API Keys fuera del código fuente](#2-mejora-1--seguridad-api-keys-fuera-del-código-fuente)
3. [Mejora #2 — Eliminación de código muerto e imports duplicados](#3-mejora-2--eliminación-de-código-muerto-e-imports-duplicados)
4. [Mejora #3 — requirements.txt actualizado](#4-mejora-3--requirementstxt-actualizado)
5. [Mejora #4 — Bugfixes](#5-mejora-4--bugfixes)
6. [Mejora #5 — Documentación actualizada](#6-mejora-5--documentación-actualizada)
7. [Mejora #6 — Inicialización temprana de variables de entorno](#7-mejora-6--inicialización-temprana-de-variables-de-entorno)
8. [Archivos Modificados](#8-archivos-modificados)
9. [Recomendaciones a Futuro](#9-recomendaciones-a-futuro)

---

## 1. Resumen del Análisis

Se analizó el código fuente completo del proyecto J.A.V.I.E.R. (~1,500 líneas en total) y se encontraron **5 categorías de mejoras** que van desde **seguridad crítica** (API keys hardcodeadas) hasta **calidad de código** (imports duplicados, dependencias faltantes, bugs potenciales).

---

## 2. Mejora #1 — Seguridad: API Keys fuera del código fuente

### Problema

Dos API keys estaban hardcodeadas directamente en el código fuente, visibles en el repositorio:

| Archivo | Línea | Key | Servicio |
|---------|-------|-----|----------|
| `motor_voz.py` | 22 | `sk_d6dd97...` | ElevenLabs TTS |
| `herramientas.py` | 186 | `TSjClEN...` | The Blue Alliance |

Además, el archivo `.env` contained **9 llaves de Gemini** (`GEMINI_KEY_0` a `GEMINI_KEY_8`) que **ya no se usan** porque el proyecto migró a OpenCode AI. Esto era confuso y daba la impresión de que el proyecto seguía usando Gemini.

### Solución aplicada

1. **`motor_voz.py`**: Se eliminó la key hardcodeada y se reemplazó por:
   ```python
   API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
   if not API_KEY:
       print("[SISTEMA] ADVERTENCIA: No hay ELEVENLABS_API_KEY en .env. Se usará respaldo Edge TTS.")
   ```

2. **`herramientas.py`**: Se eliminó la key hardcodeada de TBA y se reemplazó por:
   ```python
   TBA_API_KEY = os.getenv("TBA_API_KEY", "")
   ```

3. **`.env`**: Se limpiaron las 9 keys obsoletas de Gemini y se agregaron las 3 únicas que el proyecto realmente necesita:
   - `OPENCODE_API_KEY` — Cerebro principal
   - `ELEVENLABS_API_KEY` — Voz premium
   - `TBA_API_KEY` — Consultas de The Blue Alliance

### Beneficio

- Las API keys ya no se exponen en el repositorio (`.env` está en `.gitignore`)
- Si alguien clona el repo, solo necesita crear su propio `.env` con sus llaves
- El código es más limpio y mantenible

---

## 3. Mejora #2 — Eliminación de código muerto e imports duplicados

### Problemas encontrados

| Archivo | Problema | Impacto |
|---------|----------|---------|
| `herramientas.py:114` | `import wikipedia` a nivel módulo + otro dentro de `buscar_wikipedia()`  | El import de módulo sombreaba al import local. Código confuso |
| `gui.py:7` | `import time as _time` no se usaba en ninguna parte | Código muerto que confunde al lector |
| `splash.py:53` | `client.models.list()` no es compatible con OpenCode API | El splash screen daba "FAIL" aunque la API funcionara |

### Solución aplicada

- **`herramientas.py`**: Se eliminó el `import wikipedia` de nivel módulo (línea 114). Solo queda el import local dentro de la función `buscar_wikipedia()`
- **`gui.py`**: Se eliminó `import time as _time`
- **`splash.py`**: Se cambió la verificación de API de `client.models.list()` (no soportado por OpenCode) a un chat ping real:
  ```python
  client.chat.completions.create(
      model="big-pickle",
      messages=[{"role": "user", "content": "ping"}],
      max_tokens=1
  )
  ```

---

## 4. Mejora #3 — requirements.txt actualizado

### Problema

El `requirements.txt` original solo tenía 4 dependencias:

```
pyttsx3
pandas
openai
python-dotenv
```

Pero el proyecto realmente usa **muchas más** (pyaudio, SpeechRecognition, faster-whisper, customtkinter, psutil, pywhatkit, duckduckgo-search, wikipedia, openpyxl...). Esto significaba que:

- Alguien que clonara el repo e hiciera `pip install -r requirements.txt` se encontraría con un proyecto que no funciona
- Faltaban dependencias críticas como `pyaudio` (micrófono) y `customtkinter` (interfaz gráfica)

### Solución aplicada

Se reescribió `requirements.txt` completo con **12 dependencias reales** organizadas por categoría:

```
# Core
openai>=1.0.0
python-dotenv>=1.0.0
requests>=2.31.0

# Voz
SpeechRecognition>=3.10.0
pyaudio>=0.2.14
faster-whisper>=1.0.0

# Interfaz gráfica
customtkinter>=5.2.0
psutil>=5.9.0

# Inventario / Excel
pandas>=2.0.0
openpyxl>=3.1.0

# Herramientas
pywhatkit>=5.4.0
duckduckgo-search>=6.0.0
wikipedia>=1.4.0
```

---

## 5. Mejora #4 — Bugfixes

### 5.1 — Posible crash en ticker de GUI

**Archivo:** `gui.py:297`

**Problema:** El método `bbox()` de Tkinter puede devolver `None` si el canvas item no se ha renderizado aún. El código original hacía:

```python
text_bbox = self.ticker_canvas.bbox(self.ticker_text_id)
if text_bbox and text_bbox[2] < 0:
    self.ticker_x = self.screen_w
```

Aunque tenía un `if text_bbox`, aún podía fallar si `bbox()` devolvía una tupla con menos de 3 elementos.

**Solución:**

```python
text_bbox = self.ticker_canvas.bbox(self.ticker_text_id)
if text_bbox is not None and len(text_bbox) > 2 and text_bbox[2] < 0:
    self.ticker_x = self.screen_w
```

### 5.2 — explorar_directorio sin diferenciar archivos de carpetas

**Archivo:** `herramientas.py:50`

**Problema:** La función `explorar_directorio()` listaba archivos y carpetas sin distinción, usando `os.listdir()`:

```
Contenido de C:\Users\...:
archivo.py
mi_carpeta
otro.txt
```

**Solución:** Ahora diferencia entre `[DIR]` y `[FILE]` y muestra el tamaño de los archivos:

```
Contenido de C:\Users\...:
[DIR]  mi_carpeta\
[FILE] archivo.py  (2453 bytes)
[FILE] otro.txt    (128 bytes)
```

---

## 6. Mejora #5 — Documentación actualizada

### Problema

`JAVIER_DOCUMENTACION.md` estaba desactualizada. Mencionaba "Google Gemini" en múltiples lugares cuando el proyecto ya había migrado a OpenCode AI.

### Secciones corregidas

| Sección | Antes (incorrecto) | Después (correcto) |
|---------|-------------------|-------------------|
| ¿Qué es JAVIER? | "usando Google Gemini" | "usando OpenCode AI (modelo big-pickle)" |
| cerebro.py | "Inteligencia Artificial (Gemini)" | "Inteligencia Artificial (OpenCode AI)" |
| Detalles de cerebro.py | SDK `google-genai`, modelo `gemini-2.5-flash` | SDK `openai`, endpoint `opencode.ai/zen/v1`, modelo `big-pickle` |
| Reglas de diseño | "Gemini con google-genai" | "OpenCode AI como cerebro" |
| Tabla de API Keys | ElevenLabs + Gemini | ElevenLabs + OpenCode + TBA |

---

## 7. Mejora #6 — Inicialización temprana de variables de entorno

### Problema

`load_dotenv()` solo se llamaba en `cerebro.py`, pero `motor_voz.py` es el primer archivo importado por `main.py`. Como resultado, si `motor_voz.py` intentaba leer variables de entorno antes de que `cerebro.py` se importara, obtenía strings vacíos.

### Solución

Se agregó `load_dotenv()` al inicio de `motor_voz.py` (primer import) y también a `herramientas.py` por si se importa de forma independiente:

```python
from dotenv import load_dotenv
load_dotenv()
```

Como `load_dotenv()` es idempotente, las llamadas adicionales no tienen efecto negativo.

---

## 8. Archivos Modificados

| Archivo | Cambios |
|---------|---------|
| `.env` | Se eliminaron 9 keys de Gemini obsoletas. Se agregaron `ELEVENLABS_API_KEY` y `TBA_API_KEY` |
| `motor_voz.py` | Se agregó `load_dotenv()`. API_KEY ahora se carga de entorno. Advertencia si falta |
| `herramientas.py` | Se agregó `load_dotenv()`. TBA_API_KEY desde entorno. Se eliminó import duplicado de wikipedia. `explorar_directorio` ahora muestra DIR/FILE |
| `gui.py` | Se eliminó `import time as _time` muerto. Fix de seguridad en `bbox()` del ticker |
| `splash.py` | `_check_ai()` ahora usa chat ping en vez de `models.list()` |
| `requirements.txt` | Reescrito completo con las 12 dependencias reales |
| `JAVIER_DOCUMENTACION.md` | Actualizadas todas las referencias de Gemini → OpenCode |
| `opencode.md` | **Este archivo** |

---

## 9. Recomendaciones a Futuro

### 9.1 — Críticas (Seguridad)

- [ ] **Rotar las API keys actuales.** Las keys que estaban hardcodeadas (ElevenLabs, TBA) ahora están en `.env`, pero históricamente estuvieron expuestas en el código. Si este repo es o fue público, genera nuevas llaves en los dashboards correspondientes.

### 9.2 — Altas (Arquitectura)

- [ ] **Centralizar configuración.** Crear un `config.py` que cargue todas las variables de entorno en un solo lugar, en lugar de tener `load_dotenv()` disperso en 3 archivos. Ejemplo:
  ```python
  # config.py
  from dotenv import load_dotenv
  load_dotenv()
  OPENCODE_API_KEY = os.getenv("OPENCODE_API_KEY", "")
  ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
  TBA_API_KEY = os.getenv("TBA_API_KEY", "")
  ```
- [ ] **Migrar a Base de Datos real.** El inventario en Excel es funcional pero frágil (conflictos de escritura, sin concurrencia). Una base de datos SQLite (`inventario.db`) sería más robusta y permitiría consultas más complejas.
- [ ] **Sistema de logging.** Reemplazar los `print()` dispersos con el módulo `logging` de Python para tener control de niveles (DEBUG, INFO, ERROR) y rotación de logs.

### 9.3 — Medianas (Funcionalidad)

- [ ] **Wake word "Javier".** Implementar detección de palabra de activación con un micrófono de bajo consumo (ej. usando `porcupine` o `snowboy`) para no depender del botón PTT.
- [ ] **Modo escucha continua.** Alternativa al PTT: un toggle que active escucha continua con detección de silencio automática.
- [ ] **Inventario con ubicaciones.** Agregar columna "Ubicación" (ej. "Estante 3", "Caja B") para que JAVIER pueda responder "dónde está X".
- [ ] **Integración con Discord.** Reutilizar el mismo cerebro (`cerebro.py`) para un bot de Discord, compartiendo inventario y memoria.

### 9.4 — Bajas (Calidad de vida)

- [ ] **Type hints completos.** Agregar tipado a todas las funciones siguiendo el estándar PEP 484.
- [ ] **Tests automatizados.** Agregar tests unitarios para `base_datos.py` y `herramientas.py` usando `pytest`.
- [ ] **Pre-commit hooks.** Configurar hooks para formateo automático (`black`), linting (`ruff`) y detección de secrets (`detect-secrets`).
- [ ] **Async/await para voz.** El TTS y la transcripción de whisper son operaciones bloqueantes. Migrar a asyncio permitiría que la UI no se congele durante tareas pesadas.

### 9.5 — Archivos a limpiar

- [ ] `test.py`, `test2.py`, `test_tools.py`, `scratch.py`, `listar_voces.py` — scripts de prueba que ya no se usan y ensucian la raíz del proyecto. Moverlos a una carpeta `tests/` o eliminarlos.

---

*Documento generado por OpenCode AI como parte del análisis y mejora del proyecto J.A.V.I.E.R.*
