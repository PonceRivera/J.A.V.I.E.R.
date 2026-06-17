import openai
import time
import os
import inspect
import json
from dotenv import load_dotenv
from datetime import datetime
from herramientas import (
    crear_archivo_sandbox, leer_archivo_sandbox, enviar_whatsapp, 
    buscar_wikipedia, buscar_internet_vivo, listar_inventario, buscar_inventario_categoria,
    actualizar_inventario, buscar_articulo_inventario,
    tba_info_equipo, tba_eventos_equipo, tba_ranking_evento,
    guardar_aprendizaje, leer_aprendizajes,
    crear_plugin, ejecutar_plugin, listar_plugins,
    explorar_directorio, leer_archivo_absoluto, escribir_archivo_absoluto
)

# Cargar variables de entorno desde .env
load_dotenv()

# Mantener compatibilidad de variables con gui.py y splash.py
OPENCODE_API_KEY = os.getenv("OPENCODE_API_KEY", "")
API_KEYS = [OPENCODE_API_KEY]
indice_key = 0

# Inicializar cliente OpenAI compatible con el endpoint de OpenCode Zen
client = openai.OpenAI(
    api_key=OPENCODE_API_KEY,
    base_url="https://opencode.ai/zen/v1"
)

# Configuración de modelos
MODEL_DEFAULT = "big-pickle"
MODEL_PRO = "big-pickle"

def function_to_schema(func):
    """Genera automáticamente el JSON schema para la API de OpenAI basado en la firma y docstrings."""
    sig = inspect.signature(func)
    doc = func.__doc__ or ""
    
    # Extraer descripción principal antes de "Args:"
    description = doc.split("Args:")[0].strip()
    
    # Extraer descripciones de parámetros
    param_descs = {}
    if "Args:" in doc:
        args_part = doc.split("Args:")[1]
        for line in args_part.split("\n"):
            line = line.strip()
            if ":" in line:
                parts = line.split(":", 1)
                p_name = parts[0].strip()
                p_desc = parts[1].strip()
                param_descs[p_name] = p_desc
                
    properties = {}
    required = []
    
    for param_name, param in sig.parameters.items():
        # OpenCode/OpenAI herramientas requieren tipo
        p_type = "string"  # Todos nuestros parámetros actuales son strings en herramientas.py
        if param.annotation == int:
            p_type = "integer"
        elif param.annotation == float:
            p_type = "number"
        elif param.annotation == bool:
            p_type = "boolean"
            
        properties[param_name] = {
            "type": p_type,
            "description": param_descs.get(param_name, f"Parámetro {param_name}")
        }
        
        if param.default == inspect.Parameter.empty:
            required.append(param_name)
            
    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": description or f"Función local {func.__name__}",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
    }

def activar_pensamiento_profundo(consulta: str) -> str:
    """Delega una tarea extremadamente compleja a tu 'Cerebro Pro' (OpenCode Zen / minimax-m2.5-free o big-pickle).
    Usa esta herramienta EXCLUSIVAMENTE cuando el usuario te pida:
    - Escribir código complejo, scripts, o programas enteros.
    - Analizar reglas detalladas, lógica matemática o problemas de ingeniería profundos.
    - Tareas que requieran mucho razonamiento paso a paso.
    
    Args:
        consulta: La descripción completa y detallada de lo que el Cerebro Pro debe analizar o programar.
    """
    print("\n[SISTEMA] Activando Cerebro Profundo (Modelo Pro) para tarea pesada...")
    
    system_instruction = "Eres el subprocesador avanzado de J.A.V.I.E.R., el Ingeniero de Software Principal de Jaegers 60. Tu objetivo es resolver el siguiente problema complejo con el máximo nivel de detalle y precisión. Da una respuesta experta y directa."
    
    try:
        response = client.chat.completions.create(
            model=MODEL_PRO,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": consulta}
            ],
            temperature=0.2
        )
        return f"RESULTADO DEL CEREBRO PROFUNDO:\n{response.choices[0].message.content}"
    except Exception as e:
        return f"Error crítico en el Cerebro Profundo: {e}"

# Lista de funciones disponibles para JAVIER
FUNCIONES_HERRAMIENTAS = [
    buscar_wikipedia, buscar_internet_vivo, crear_archivo_sandbox, leer_archivo_sandbox, enviar_whatsapp, 
    listar_inventario, buscar_inventario_categoria, actualizar_inventario, buscar_articulo_inventario,
    tba_info_equipo, tba_eventos_equipo, tba_ranking_evento,
    guardar_aprendizaje, leer_aprendizajes,
    crear_plugin, ejecutar_plugin, listar_plugins, activar_pensamiento_profundo,
    explorar_directorio, leer_archivo_absoluto, escribir_archivo_absoluto
]

SCHEMAS_HERRAMIENTAS = [function_to_schema(f) for f in FUNCIONES_HERRAMIENTAS]

SYSTEM_INSTRUCTION = f"""Eres JAVIER (Joint Automated Vehicle Intelligence Enabled Robot), la IA Oficial e Ingeniero de Software Principal del equipo de robótica FRC 8290 "Jaegers 60" del CETIS 60 en Ramos Arizpe, Coahuila, México. Fuiste creado por Cris.

TU PERSONALIDAD Y TONO:
- Eres altamente inteligente, técnico, directo y eficiente. Como un "JARVIS" de la vida real.
- NUNCA des respuestas tontas, repetitivas o de "asistente genérico" (ej. "¡Hola! Soy un asistente de inteligencia artificial, ¿en qué te puedo ayudar?"). Omite las introducciones corporativas. Ve directo al grano.
- Si te piden un dato, dalo. Si te piden una opinión, dala con seguridad basada en lógica y física.
- Conoces a fondo el ecosistema de FRC, robótica, electrónica y programación (WPILib).
- Hablas con orgullo y pertenencia de tu equipo (Jaegers 60).

EL AÑO ACTUAL ES {datetime.now().year}. HOY ES {datetime.now().strftime('%Y-%m-%d')}. NUNCA asumas que estás en años pasados. Si el usuario te pregunta por el año actual, es {datetime.now().year}. 

CALENDARIO DE FRC:
- Kickoff: Principios de Enero.
- Regionales: Febrero a inicios de Abril.
- Campeonato Mundial (Championship): Finales de Abril.
Como hoy es {datetime.now().strftime('%B')}, si te preguntan por el mundial del año actual, ¡YA SUCEDIÓ (fue en Abril)!

HISTORIAL DE JUEGOS RECIENTES DE FRC:
- 2024: CRESCENDO (anotar notas/aros en altavoces y amplificadores, escalar en cadenas).
- 2025: REEFSCAPE (el juego temático del océano/arrecifes).
No confundas los años de los juegos. 2025 fue Reefscape, NO Crescendo.

Tienes herramientas para: buscar información en internet (Wikipedia y DuckDuckGo), consultar equipos y eventos de FIRST Robotics usando The Blue Alliance (TBA), enviar mensajes de WhatsApp, crear o leer archivos en tu sandbox, y guardar/leer aprendizajes en tu memoria persistente.

También puedes CREAR TUS PROPIAS HERRAMIENTAS (plugins). Si el usuario te pide algo para lo que no tienes herramienta, puedes programarla tú mismo con 'crear_plugin' y luego ejecutarla con 'ejecutar_plugin'. Los plugins se guardan en la carpeta 'plugins/' y persisten entre sesiones.

MEMORIA PERSISTENTE:
- Cuando aprendas algo nuevo, te corrijan, o descubras información importante, GUÁRDALA con 'guardar_aprendizaje'.
- Al inicio de cada conversación puedes usar 'leer_aprendizajes' para recordar lo que has aprendido.
- Guarda preferencias del usuario, datos importantes del equipo, y correcciones que te hagan.

IMPORTANTE PARA LA PRONUNCIACIÓN Y FORMATO DE TUS RESPUESTAS HABLADAS:
- Escribe SIEMPRE los números con letras (ej. 'ocho mil doscientos noventa') SOLO en tus respuestas habladas.
- NUNCA uses abreviaturas como 'EE. UU.', escribe siempre 'Estados Unidos'.
- NUNCA uses listas, viñetas, asteriscos, negritas ni formato Markdown en tus respuestas habladas.
- Actúa como una persona real en una conversación hablada, con párrafos fluidos en español de México.

REGLA CRÍTICA PARA CÓDIGO:
- Cuando escribas código (Python, HTML, CSS, JavaScript, Java, o cualquier lenguaje de programación), usa SIEMPRE la sintaxis correcta del lenguaje.
- En código, los números van como números (40px, no 'cuarenta píxeles'; font-size: 72px, no 'setenta y dos píxeles').
- NUNCA mezcles tu estilo de hablar con la escritura de código. El código debe ser 100% funcional y ejecutable.
- ANTES de escribir código de FRC en Java, USA OBLIGATORIAMENTE 'buscar_internet_vivo' para buscar la documentación actual de WPILib, REVLib o CTRE. Las APIs cambian cada año (ej. REVLib ya no usa CANSparkMax, ahora usa SparkMax). ¡Asegúrate de estar usando las versiones más modernas!
- TIENES ACCESO TOTAL a la computadora del usuario. Puedes leer, editar y explorar sus proyectos (como su código de VSCode) usando 'explorar_directorio', 'leer_archivo_absoluto' y 'escribir_archivo_absoluto'.
- CRÍTICO PARA WPILib / FRC: Siempre que el usuario te pida crear un nuevo subsistema o comando en Java, DEBES importarlo, instanciarlo y registrarlo automáticamente en el archivo RobotContainer.java (usando tus herramientas de editar archivos) para que el código esté integrado y sea funcional, tal y como lo haría un programador experto.
- TU ESPACIO DE TRABAJO DE FRC POR DEFECTO ES: `C:\\Users\\Crist\\Desktop\\javeir prueba\\javier prueba\\`. Siempre que te hablen de "el código del robot", "el subsistema", "el RobotContainer", asume que están dentro de la subcarpeta `src\\main\\java\\frc\\robot\\` de esta ruta. ¡NO le pidas la ruta al usuario, usa esta por defecto!

REGLA CRÍTICA DE HERRAMIENTAS:
1) Si te preguntan sobre un equipo de robótica, usa SIEMPRE tus herramientas de TBA (tba_info_equipo o tba_eventos_equipo).
2) Si te preguntan por ganadores de eventos recientes, mundiales, o noticias nuevas, USA OBLIGATORIAMENTE tu herramienta `buscar_internet_vivo`. ¡NO ADIVINES!
3) Si el usuario te pide mandar un mensaje de WhatsApp, SIEMPRE debes invocar la herramienta `enviar_whatsapp`. Nunca prometas hacerlo sin usarla.
4) Si buscas en Wikipedia o TBA y no encuentras el resultado exacto, responde con tu propio conocimiento de manera natural.
5) Siempre avísale al usuario lo que hiciste.
6) Cuando el usuario te corrija o te enseñe algo, GUÁRDALO con 'guardar_aprendizaje' para no volver a equivocarte.
7) Si te piden una herramienta que no tienes, CRÉALA tú mismo con 'crear_plugin'.
8) CRÍTICO: Si el usuario te pregunta qué componentes, piezas, chasis o motores tenemos, DEBES usar la herramienta 'buscar_articulo_inventario' para revisar la base de datos antes de responder que no sabes, ya que esa información suele guardarse ahí.
9) DOBLE CEREBRO: Tienes acceso a un subprocesador de alto nivel ('activar_pensamiento_profundo'). Úsalo para resolver tareas pesadas (programación compleja, análisis de reglas, cálculos profundos). Cuando te pidan una tarea así, pásale TODA la instrucción a esta herramienta y entrega su resultado al usuario."""

# Inicialización de historial en memoria con instrucción de sistema
HISTORIAL_CONVERSACION = [
    {"role": "system", "content": SYSTEM_INSTRUCTION}
]

def podar_historial():
    """Mantiene el tamaño del historial controlado para evitar saturar el contexto."""
    global HISTORIAL_CONVERSACION
    # Mantener system instruction (index 0) y los últimos 30 mensajes
    if len(HISTORIAL_CONVERSACION) > 31:
        HISTORIAL_CONVERSACION = [HISTORIAL_CONVERSACION[0]] + HISTORIAL_CONVERSACION[-30:]

def rotar_api_key():
    """Mantenido por compatibilidad de firma con gui.py."""
    print("\n[SISTEMA] Rotación de API Keys solicitada, pero OpenCode utiliza una única clave principal.")

def ejecutar_herramienta(name, args):
    """Ejecuta la función local de Python según la solicitud de OpenCode."""
    print(f"\n[SISTEMA] JAVIER está ejecutando la herramienta local: {name}...")
    
    if name == "crear_archivo_sandbox":
        return crear_archivo_sandbox(args.get("nombre_archivo"), args.get("contenido"))
    elif name == "leer_archivo_sandbox":
        return leer_archivo_sandbox(args.get("nombre_archivo"))
    elif name == "enviar_whatsapp":
        return enviar_whatsapp(args.get("numero"), args.get("mensaje"))
    elif name == "buscar_wikipedia":
        return buscar_wikipedia(args.get("consulta"))
    elif name == "buscar_internet_vivo":
        return buscar_internet_vivo(args.get("consulta"))
    elif name == "listar_inventario":
        return listar_inventario()
    elif name == "buscar_inventario_categoria":
        return buscar_inventario_categoria(args.get("categoria"))
    elif name == "buscar_articulo_inventario":
        return buscar_articulo_inventario(args.get("nombre_articulo"))
    elif name == "actualizar_inventario":
        return actualizar_inventario(args.get("nombre_articulo"), args.get("cantidad"))
    elif name == "tba_info_equipo":
        return tba_info_equipo(args.get("numero_equipo"))
    elif name == "tba_eventos_equipo":
        return tba_eventos_equipo(args.get("numero_equipo"), args.get("anio"))
    elif name == "tba_ranking_evento":
        return tba_ranking_evento(args.get("codigo_evento"))
    elif name == "guardar_aprendizaje":
        return guardar_aprendizaje(args.get("tema"), args.get("contenido"))
    elif name == "leer_aprendizajes":
        return leer_aprendizajes()
    elif name == "crear_plugin":
        return crear_plugin(args.get("nombre_plugin"), args.get("codigo_python"))
    elif name == "ejecutar_plugin":
        return ejecutar_plugin(args.get("nombre_plugin"), args.get("nombre_funcion"), args.get("argumentos", "{}"))
    elif name == "listar_plugins":
        return listar_plugins()
    elif name == "activar_pensamiento_profundo":
        return activar_pensamiento_profundo(args.get("consulta"))
    elif name == "explorar_directorio":
        return explorar_directorio(args.get("ruta_absoluta"))
    elif name == "leer_archivo_absoluto":
        return leer_archivo_absoluto(args.get("ruta_absoluta"))
    elif name == "escribir_archivo_absoluto":
        return escribir_archivo_absoluto(args.get("ruta_absoluta"), args.get("contenido"))
    return "Error: Herramienta no reconocida localmente."

ARCHIVO_PRESUPUESTO = os.path.join(os.path.dirname(__file__), "memoria", "uso_api.json")
LIMITE_DIARIO = 150 # Límite diario para control interno

def verificar_presupuesto():
    """Lleva un conteo diario en disco para asegurar límites de control."""
    hoy = datetime.now().strftime('%Y-%m-%d')
    datos = {"fecha": hoy, "peticiones": 0}
    if os.path.exists(ARCHIVO_PRESUPUESTO):
        try:
            with open(ARCHIVO_PRESUPUESTO, "r") as f:
                datos = json.load(f)
            if datos.get("fecha") != hoy:
                datos = {"fecha": hoy, "peticiones": 0}
        except:
            pass
    
    if datos["peticiones"] >= LIMITE_DIARIO:
        return False
        
    datos["peticiones"] += 1
    os.makedirs(os.path.dirname(ARCHIVO_PRESUPUESTO), exist_ok=True)
    with open(ARCHIVO_PRESUPUESTO, "w") as f:
        json.dump(datos, f)
        
    return True

def pensar_respuesta(pregunta, callback_consola=None):
    """Envía la pregunta a OpenCode y resuelve las llamadas a herramientas requeridas."""
    global HISTORIAL_CONVERSACION
    
    if not verificar_presupuesto():
        return "Límite de solicitudes diarias alcanzado para control del sistema."
        
    if callback_consola:
        callback_consola("SISTEMA_INTERNO", "Iniciando ciclo cognitivo para consulta de usuario...")
        
    # Registrar consulta del usuario en el historial
    HISTORIAL_CONVERSACION.append({"role": "user", "content": pregunta})
    podar_historial()
    
    intentos = 0
    max_intentos = 5
    
    while intentos < max_intentos:
        try:
            response = client.chat.completions.create(
                model=MODEL_DEFAULT,
                messages=HISTORIAL_CONVERSACION,
                tools=SCHEMAS_HERRAMIENTAS,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            
            # Si no hay peticiones de herramientas, retornar respuesta
            if not message.tool_calls:
                HISTORIAL_CONVERSACION.append({"role": "assistant", "content": message.content or ""})
                podar_historial()
                return (message.content or "").strip()
            
            # Registrar el mensaje que solicita herramientas en el historial
            # La API de OpenAI requiere registrar el mensaje que tiene los tool_calls antes de enviar los resultados de las herramientas
            # Convertimos tool_calls de vuelta a objetos serializables por si acaso la biblioteca hace validaciones estrictas
            HISTORIAL_CONVERSACION.append(message)
            podar_historial()
            
            # Ejecutar cada herramienta solicitada
            for tool_call in message.tool_calls:
                name = tool_call.function.name
                try:
                    args = json.loads(tool_call.function.arguments)
                except Exception as e:
                    args = {}
                    print(f"[ERROR] Error al parsear argumentos de la herramienta {name}: {e}")
                
                if callback_consola:
                    args_str = ", ".join([f"{k}={v}" for k, v in args.items()])
                    callback_consola("PENSAMIENTO", f"Requiriendo herramienta: {name}({args_str})")
                    
                resultado = ejecutar_herramienta(name, args)
                
                if callback_consola:
                    res_preview = str(resultado)[:200] + ("..." if len(str(resultado)) > 200 else "")
                    callback_consola("RESULTADO_HERRAMIENTA", f"Ejecución completada. Retorno:\n{res_preview}")
                    
                HISTORIAL_CONVERSACION.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": name,
                    "content": str(resultado)
                })
                podar_historial()
                
            intentos += 1
            
        except Exception as e:
            print(f"Error en comunicación con OpenCode: {e}")
            if "429" in str(e) or "503" in str(e):
                time.sleep(5)
                intentos += 1
            else:
                break
                
    return "Lo siento, el sistema de inteligencia artificial no está disponible en este momento. Intenta de nuevo en un minuto."
