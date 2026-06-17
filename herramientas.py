import os
import pywhatkit
import time
import requests
from ddgs import DDGS
from base_datos import listar_inventario_completo as _listar_inventario_completo, buscar_inventario_por_categoria as _buscar_por_cat, actualizar_inventario as _actualizar_inventario, buscar_articulo as _buscar_articulo

SANDBOX_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "sandbox"))

def es_ruta_segura(ruta: str) -> bool:
    """Valida que la ruta absoluta resultante siga estando dentro del sandbox."""
    ruta_absoluta = os.path.abspath(os.path.join(SANDBOX_DIR, ruta))
    return ruta_absoluta.startswith(SANDBOX_DIR)

def crear_archivo_sandbox(nombre_archivo: str, contenido: str) -> str:
    """Crea un archivo dentro del directorio seguro 'sandbox'.
    Args:
        nombre_archivo: El nombre del archivo a crear (ej. hola.txt)
        contenido: El texto que se guardará en el archivo
    """
    if not es_ruta_segura(nombre_archivo):
        return "Error: Acceso denegado. No puedes crear archivos fuera del sandbox."
    
    ruta_final = os.path.join(SANDBOX_DIR, nombre_archivo)
    try:
        with open(ruta_final, "w", encoding="utf-8") as f:
            f.write(contenido)
        return f"Éxito: Archivo '{nombre_archivo}' creado correctamente."
    except Exception as e:
        return f"Error al crear el archivo: {e}"

def leer_archivo_sandbox(nombre_archivo: str) -> str:
    """Lee el contenido de un archivo dentro del directorio seguro 'sandbox'.
    Args:
        nombre_archivo: El nombre del archivo a leer (ej. notas.txt)
    """
    if not es_ruta_segura(nombre_archivo):
        return "Error: Acceso denegado. No puedes leer archivos fuera del sandbox."
    
    ruta_final = os.path.join(SANDBOX_DIR, nombre_archivo)
    if not os.path.exists(ruta_final):
        return f"Error: El archivo '{nombre_archivo}' no existe en el sandbox."
        
    try:
        with open(ruta_final, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error al leer el archivo: {e}"

def explorar_directorio(ruta_absoluta: str) -> str:
    """Explora una ruta del sistema del usuario y lista sus archivos y carpetas. Útil para ubicar archivos de proyectos de FRC.
    Args:
        ruta_absoluta: La ruta absoluta de la carpeta a explorar (ej. 'C:\\Users\\Crist\\Desktop\\newswerve').
    """
    try:
        if not os.path.exists(ruta_absoluta):
            return f"Error: La ruta '{ruta_absoluta}' no existe."
        archivos = os.listdir(ruta_absoluta)
        return f"Contenido de {ruta_absoluta}:\n" + "\n".join(archivos)
    except Exception as e:
        return f"Error al explorar directorio: {e}"

def leer_archivo_absoluto(ruta_absoluta: str) -> str:
    """Lee el contenido de cualquier archivo en la computadora del usuario usando su ruta absoluta.
    Args:
        ruta_absoluta: La ruta completa del archivo (ej. 'C:\\Users\\Crist\\Desktop\\newswerve\\Robot.java').
    """
    try:
        if not os.path.exists(ruta_absoluta):
            return f"Error: El archivo '{ruta_absoluta}' no existe."
        with open(ruta_absoluta, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error al leer archivo: {e}"

def escribir_archivo_absoluto(ruta_absoluta: str, contenido: str) -> str:
    """Sobrescribe o crea un archivo en cualquier parte de la computadora del usuario. Úsalo para programar el robot del usuario en sus directorios.
    Args:
        ruta_absoluta: La ruta completa del archivo (ej. 'C:\\Users\\Crist\\Desktop\\newswerve\\Robot.java').
        contenido: El código o texto a guardar.
    """
    try:
        os.makedirs(os.path.dirname(ruta_absoluta), exist_ok=True)
        with open(ruta_absoluta, "w", encoding="utf-8") as f:
            f.write(contenido)
        print(f"\n[SISTEMA] Javier modificó un archivo externo: {ruta_absoluta}")
        return f"Archivo guardado/modificado exitosamente en: {ruta_absoluta}"
    except Exception as e:
        return f"Error al escribir archivo: {e}"

CONTACTOS = {
    "max": "+528112114677",
    "cris": "+521234567890"  
}

def enviar_whatsapp(numero: str, mensaje: str) -> str:
    """Envía un mensaje de WhatsApp automatizado a un número telefónico o contacto.
    Args:
        numero: El número telefónico o el nombre del contacto (ej. 'Max')
        mensaje: El texto del mensaje a enviar
    """
    # Verificar si el "numero" que nos dio Gemini es en realidad un nombre guardado
    destinatario = numero.strip().lower()
    numero_real = CONTACTOS.get(destinatario, numero) # Si no es contacto, usa lo que le pasamos como número

    try:
        print(f"\n[SISTEMA] Preparando envío de WhatsApp a {numero_real} (Contacto: {destinatario})...")
        # wait_time=15 segundos para cargar WhatsApp Web. tab_close=True para cerrarlo al terminar.
        pywhatkit.sendwhatmsg_instantly(numero_real, mensaje, wait_time=15, tab_close=True, close_time=4)
        return f"Éxito: WhatsApp enviado a {numero_real}."
    except Exception as e:
        return f"Error al intentar enviar el WhatsApp: {e}"

import wikipedia

def buscar_wikipedia(consulta: str) -> str:
    """Busca un resumen en Wikipedia en español. Útil para información general.
    Args:
        consulta: Lo que se desea buscar (ej. 'FIRST Robotics Competition').
    """
    try:
        import wikipedia
        wikipedia.set_lang("es")
        resumen = wikipedia.summary(consulta, sentences=2)
        return resumen
    except Exception as e:
        return f"Error buscando en Wikipedia: {e}"

def buscar_internet_vivo(consulta: str) -> str:
    """Busca en internet en tiempo real usando el motor de búsqueda DuckDuckGo.
    Útil para buscar noticias, reglas de juegos de FRC recientes (como Reefscape), y manuales.
    Args:
        consulta: Lo que se desea buscar en internet (ej. 'FRC Reefscape manual en español').
    """
    try:
        resultados = DDGS().text(consulta, max_results=3)
        if not resultados:
            return "No se encontraron resultados en internet."
        texto_resultados = []
        for i, res in enumerate(resultados):
            texto_resultados.append(f"Resultado {i+1}:\nTítulo: {res.get('title')}\nEnlace: {res.get('href')}\nResumen: {res.get('body')}")
        return "\n\n".join(texto_resultados)
    except Exception as e:
        return f"Error buscando en internet: {e}"

def listar_inventario() -> str:
    """Lista todos los artículos y herramientas que tiene el equipo en el inventario del taller."""
    print("\n[SISTEMA] Cargando inventario completo del taller...")
    return _listar_inventario_completo()

def buscar_inventario_categoria(categoria: str) -> str:
    """Busca y cuenta artículos del inventario local que pertenecen a una categoría específica.
    Args:
        categoria: La categoría a buscar (ej. 'herramientas', 'electronica', 'motores', 'tornilleria', 'llantas', etc.)
    """
    try:
        return _buscar_por_cat(categoria)
    except Exception as e:
        return f"Error filtrando inventario: {e}"

def buscar_articulo_inventario(nombre_articulo: str) -> str:
    """Busca un artículo específico en el inventario.
    Usa esta herramienta cuando el usuario pregunte si tienen algún material, herramienta, chasis, o componente.
    Args:
        nombre_articulo: El nombre del artículo a buscar (ej. 'kraken', 'chasis', 'pinzas').
    """
    try:
        return _buscar_articulo(nombre_articulo)
    except Exception as e:
        return f"Error buscando artículo: {e}"

def actualizar_inventario(nombre_articulo: str, cantidad: str) -> str:
    """Modifica o agrega un artículo al inventario (archivo excel) del taller.
    Usa esta herramienta cuando el usuario te pida agregar material nuevo o actualizar las cantidades de un artículo existente.
    Args:
        nombre_articulo: El nombre del artículo (ej. 'motores kraken x60').
        cantidad: La cantidad a establecer (ej. '5').
    """
    try:
        print(f"\n[SISTEMA] Actualizando inventario: {nombre_articulo} -> {cantidad}...")
        return _actualizar_inventario(nombre_articulo, cantidad)
    except Exception as e:
        return f"Error actualizando inventario: {e}"

# ─── THE BLUE ALLIANCE API ────────────────────────────────────────────
TBA_API_KEY = "TSjClENCvNITHaM7E4yB8GMsmR0lhnzs0umAIdaOabls503sTqSFhlgFBouCVTDN"
TBA_BASE_URL = "https://www.thebluealliance.com/api/v3"

def tba_info_equipo(numero_equipo: str) -> str:
    """Obtiene informacion basica de un equipo FRC desde The Blue Alliance.
    Args:
        numero_equipo: El número de equipo FRC (ej. '8290').
    """
    if not TBA_API_KEY or TBA_API_KEY == "PON_TU_LLAVE_AQUI":
        return "Error: La API Key de The Blue Alliance no está configurada."
    headers = {"X-TBA-Auth-Key": TBA_API_KEY}
    try:
        r = requests.get(f"{TBA_BASE_URL}/team/frc{numero_equipo}", headers=headers)
        if r.status_code == 404:
            return f"Equipo {numero_equipo} no encontrado en TBA."
        r.raise_for_status()
        data = r.json()
        return f"Equipo {numero_equipo} ({data.get('nickname')}): De {data.get('city')}, {data.get('state_prov')}, {data.get('country')}. Escuela: {data.get('school_name')}. Año de novato: {data.get('rookie_year')}."
    except Exception as e:
        return f"Error consultando TBA: {e}"

def tba_eventos_equipo(numero_equipo: str, anio: str) -> str:
    """Obtiene los eventos a los que asistira o asistio un equipo FRC en un año especifico.
    Args:
        numero_equipo: El número de equipo FRC (ej. '8290').
        anio: El año de la competencia (ej. '2024').
    """
    if not TBA_API_KEY or TBA_API_KEY == "PON_TU_LLAVE_AQUI":
        return "Error: La API Key de The Blue Alliance no está configurada."
    headers = {"X-TBA-Auth-Key": TBA_API_KEY}
    try:
        r = requests.get(f"{TBA_BASE_URL}/team/frc{numero_equipo}/events/{anio}/simple", headers=headers)
        if r.status_code == 404:
            return f"No se encontraron eventos para el equipo {numero_equipo} en el año {anio}."
        r.raise_for_status()
        data = r.json()
        if not data:
            return f"El equipo no tiene eventos registrados en el año {anio}."
        eventos = [f"- {e.get('name')} (en {e.get('city')}, inicio: {e.get('start_date')})" for e in data]
        return f"Eventos del equipo {numero_equipo} en {anio}:\n" + "\n".join(eventos)
    except Exception as e:
        return f"Error consultando TBA: {e}"

def tba_ranking_evento(codigo_evento: str) -> str:
    """Obtiene el Top 5 de un evento especifico.
    Args:
        codigo_evento: El código de evento de TBA (ej. '2024mxmo').
    """
    if not TBA_API_KEY or TBA_API_KEY == "PON_TU_LLAVE_AQUI":
        return "Error: La API Key de The Blue Alliance no está configurada."
    headers = {"X-TBA-Auth-Key": TBA_API_KEY}
    try:
        r = requests.get(f"{TBA_BASE_URL}/event/{codigo_evento}/rankings", headers=headers)
        if r.status_code == 404:
            return f"Evento {codigo_evento} no encontrado."
        r.raise_for_status()
        data = r.json()
        rankings = data.get("rankings", [])
        if not rankings:
            return f"Todavía no hay rankings disponibles para el evento {codigo_evento}."
        top5 = [f"#{r['rank']}: Equipo {r['team_key'].replace('frc', '')} (Record: {r['record']['wins']}-{r['record']['losses']}-{r['record']['ties']})" for r in rankings[:5]]
        return f"Top 5 del evento {codigo_evento}:\n" + "\n".join(top5)
    except Exception as e:
        return f"Error consultando TBA: {e}"

# ─── SISTEMA DE MEMORIA PERSISTENTE ──────────────────────────────────
import json

MEMORIA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "memoria"))
APRENDIZAJES_FILE = os.path.join(MEMORIA_DIR, "aprendizajes.json")

def _cargar_aprendizajes():
    """Carga los aprendizajes del disco."""
    try:
        with open(APRENDIZAJES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def _guardar_aprendizajes(datos):
    """Guarda los aprendizajes al disco."""
    os.makedirs(MEMORIA_DIR, exist_ok=True)
    with open(APRENDIZAJES_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def guardar_aprendizaje(tema: str, contenido: str) -> str:
    """Guarda una nota o aprendizaje en la memoria persistente de JAVIER para recordarlo en el futuro.
    Usa esta herramienta cuando aprendas algo nuevo, corrijas un error, o el usuario te enseñe algo importante.
    Args:
        tema: Título corto del aprendizaje (ej. 'Reefscape 2025', 'Preferencias de Cris').
        contenido: El dato o lección aprendida que quieres recordar.
    """
    from datetime import datetime
    datos = _cargar_aprendizajes()
    entrada = {
        "tema": tema,
        "contenido": contenido,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    datos.append(entrada)
    _guardar_aprendizajes(datos)
    print(f"\n[MEMORIA] Aprendizaje guardado: {tema}")
    return f"Aprendizaje guardado exitosamente: '{tema}'."

def leer_aprendizajes() -> str:
    """Lee todos los aprendizajes y notas que JAVIER ha guardado previamente en su memoria persistente.
    Usa esta herramienta al inicio de una conversación o cuando necesites recordar algo del pasado.
    """
    datos = _cargar_aprendizajes()
    if not datos:
        return "No tengo aprendizajes guardados aún."
    lineas = []
    for d in datos:
        lineas.append(f"[{d['fecha']}] {d['tema']}: {d['contenido']}")
    return "Mis aprendizajes guardados:\n" + "\n".join(lineas)

# ─── SISTEMA DE AUTO-DESARROLLO (PLUGINS) ────────────────────────────
import re

PLUGINS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "plugins"))

# Archivos que JAVIER NUNCA puede modificar
ARCHIVOS_PROTEGIDOS = {
    "main.py", "cerebro.py", "motor_voz.py", "gui.py", "splash.py",
    "base_datos.py", "herramientas.py"
}

# Imports peligrosos que JAVIER no puede usar en sus plugins
IMPORTS_PROHIBIDOS = {"subprocess", "shutil", "ctypes", "sys", "socket", "http.server", "smtplib"}

def crear_plugin(nombre_plugin: str, codigo_python: str) -> str:
    """Crea una nueva herramienta/plugin de Python para JAVIER en la carpeta segura 'plugins'.
    El plugin puede contener funciones de utilidad que se ejecutarán con 'ejecutar_plugin'.
    NO puedes modificar archivos del sistema (main.py, cerebro.py, etc.).
    Args:
        nombre_plugin: Nombre del archivo del plugin sin extensión (ej. 'calculadora_engranajes').
        codigo_python: El código Python completo del plugin. Debe contener al menos una función.
    """
    # Validar nombre
    nombre_limpio = re.sub(r'[^a-z0-9_]', '', nombre_plugin.lower())
    if not nombre_limpio:
        return "Error: El nombre del plugin no es válido. Usa solo letras, números y guiones bajos."
    
    if nombre_limpio in ARCHIVOS_PROTEGIDOS or f"{nombre_limpio}.py" in ARCHIVOS_PROTEGIDOS:
        return f"Error: No tienes permiso para crear o modificar '{nombre_limpio}'. Es un archivo protegido del sistema."
    
    # Validar que no use imports peligrosos
    for imp_prohibido in IMPORTS_PROHIBIDOS:
        if imp_prohibido in codigo_python:
            return f"Error: El plugin no puede usar '{imp_prohibido}' por seguridad."
    
    # Guardar el plugin
    ruta_plugin = os.path.join(PLUGINS_DIR, f"{nombre_limpio}.py")
    try:
        os.makedirs(PLUGINS_DIR, exist_ok=True)
        with open(ruta_plugin, "w", encoding="utf-8") as f:
            f.write(codigo_python)
        print(f"\n[PLUGINS] Plugin creado: {nombre_limpio}.py")
        return f"Plugin '{nombre_limpio}.py' creado exitosamente en la carpeta plugins. Usa 'ejecutar_plugin' para probarlo."
    except Exception as e:
        return f"Error al crear plugin: {e}"

def ejecutar_plugin(nombre_plugin: str, nombre_funcion: str, argumentos: str) -> str:
    """Ejecuta una función de un plugin previamente creado por JAVIER.
    Args:
        nombre_plugin: Nombre del plugin sin extensión (ej. 'calculadora_engranajes').
        nombre_funcion: Nombre de la función a ejecutar dentro del plugin (ej. 'calcular_rpm').
        argumentos: Argumentos para la función en formato JSON (ej. '{"gear_ratio": 10, "motor_rpm": 6000}').
    """
    nombre_limpio = re.sub(r'[^a-z0-9_]', '', nombre_plugin.lower())
    ruta_plugin = os.path.join(PLUGINS_DIR, f"{nombre_limpio}.py")
    
    if not os.path.exists(ruta_plugin):
        return f"Error: El plugin '{nombre_limpio}' no existe. Créalo primero con 'crear_plugin'."
    
    try:
        # Cargar el módulo dinámicamente
        import importlib.util
        spec = importlib.util.spec_from_file_location(nombre_limpio, ruta_plugin)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        
        # Buscar la función
        if not hasattr(modulo, nombre_funcion):
            funciones_disponibles = [f for f in dir(modulo) if not f.startswith('_') and callable(getattr(modulo, f))]
            return f"Error: La función '{nombre_funcion}' no existe en '{nombre_limpio}'. Funciones disponibles: {funciones_disponibles}"
        
        funcion = getattr(modulo, nombre_funcion)
        
        # Parsear argumentos
        args_dict = json.loads(argumentos) if argumentos and argumentos.strip() != "{}" else {}
        
        resultado = funcion(**args_dict)
        print(f"\n[PLUGINS] Ejecutado: {nombre_limpio}.{nombre_funcion}()")
        return str(resultado)
    except json.JSONDecodeError:
        return "Error: Los argumentos no están en formato JSON válido."
    except Exception as e:
        return f"Error al ejecutar plugin: {e}"

def listar_plugins() -> str:
    """Lista todos los plugins (herramientas) que JAVIER ha creado para sí mismo."""
    try:
        archivos = [f for f in os.listdir(PLUGINS_DIR) if f.endswith('.py') and f != '__init__.py']
        if not archivos:
            return "No hay plugins creados todavía."
        
        info_plugins = []
        for archivo in archivos:
            ruta = os.path.join(PLUGINS_DIR, archivo)
            with open(ruta, 'r', encoding='utf-8') as f:
                contenido = f.read()
            # Extraer funciones del plugin
            funciones = re.findall(r'def\s+(\w+)\s*\(', contenido)
            funciones = [fn for fn in funciones if not fn.startswith('_')]
            info_plugins.append(f"- {archivo}: Funciones: {', '.join(funciones) if funciones else 'ninguna'}")
        
        return "Plugins disponibles:\n" + "\n".join(info_plugins)
    except Exception as e:
        return f"Error al listar plugins: {e}"
