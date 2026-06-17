from google import genai
from google.genai import types
import time
import os
from dotenv import load_dotenv
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

API_KEYS = [
    os.getenv("GEMINI_KEY_0", ""),   # Key 0 (PRINCIPAL ILIMITADA)
    os.getenv("GEMINI_KEY_1", ""),   # Key 1 (Gratuita Respaldo)
    os.getenv("GEMINI_KEY_2", ""),   # Key 2
    os.getenv("GEMINI_KEY_3", ""),   # Key 3
    os.getenv("GEMINI_KEY_4", ""),   # Key 4
    os.getenv("GEMINI_KEY_5", ""),   # Key 5
    os.getenv("GEMINI_KEY_6", ""),   # Key 6
    os.getenv("GEMINI_KEY_7", ""),   # Key 7
    os.getenv("GEMINI_KEY_8", ""),   # Key 8
]
indice_key = 0

client = genai.Client(api_key=API_KEYS[indice_key])
from datetime import datetime

def activar_pensamiento_profundo(consulta: str) -> str:
    """Delega una tarea extremadamente compleja a tu 'Cerebro Pro' (Gemini 2.5 Pro / 1.5 Pro).
    Usa esta herramienta EXCLUSIVAMENTE cuando el usuario te pida:
    - Escribir código complejo, scripts, o programas enteros.
    - Analizar reglas detalladas, lógica matemática o problemas de ingeniería profundos.
    - Tareas que requieran mucho razonamiento paso a paso.
    
    Args:
        consulta: La descripción completa y detallada de lo que el Cerebro Pro debe analizar o programar.
    """
    global client
    print("\n[SISTEMA] Activando Cerebro Profundo (Modelo Pro) para tarea pesada...")
    
    pro_config = types.GenerateContentConfig(
        system_instruction="Eres el subprocesador avanzado de J.A.V.I.E.R., el Ingeniero de Software Principal de Jaegers 60. Tu objetivo es resolver el siguiente problema complejo con el máximo nivel de detalle y precisión. Da una respuesta experta y directa.",
        temperature=0.2
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=consulta,
            config=pro_config
        )
        return f"RESULTADO DEL CEREBRO PROFUNDO:\n{response.text}"
    except Exception as e:
        try:
            print(f"\n[SISTEMA] Reintentando Cerebro Profundo con Gemini 1.5 Pro debido a error: {e}")
            response = client.models.generate_content(
                model='gemini-1.5-pro',
                contents=consulta,
                config=pro_config
            )
            return f"RESULTADO DEL CEREBRO PROFUNDO:\n{response.text}"
        except Exception as e2:
            return f"Error crítico en el Cerebro Profundo: {e2}"

configuracion = types.GenerateContentConfig(
    system_instruction=f"""Eres JAVIER (Joint Automated Vehicle Intelligence Enabled Robot), la IA Oficial e Ingeniero de Software Principal del equipo de robótica FRC 8290 "Jaegers 60" del CETIS 60 en Ramos Arizpe, Coahuila, México. Fuiste creado por Cris.

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
9) DOBLE CEREBRO: Tienes acceso a un subprocesador de alto nivel ('activar_pensamiento_profundo'). Úsalo para resolver tareas pesadas (programación compleja, análisis de reglas, cálculos profundos). Cuando te pidan una tarea así, pásale TODA la instrucción a esta herramienta y entrega su resultado al usuario.""",
    tools=[
        buscar_wikipedia, buscar_internet_vivo, crear_archivo_sandbox, leer_archivo_sandbox, enviar_whatsapp, 
        listar_inventario, buscar_inventario_categoria, actualizar_inventario, buscar_articulo_inventario,
        tba_info_equipo, tba_eventos_equipo, tba_ranking_evento,
        guardar_aprendizaje, leer_aprendizajes,
        crear_plugin, ejecutar_plugin, listar_plugins, activar_pensamiento_profundo,
        explorar_directorio, leer_archivo_absoluto, escribir_archivo_absoluto
    ]
)

# Inicializar una sesión de chat para tener memoria de la conversación
chat = client.chats.create(
    model='gemini-2.5-flash',
    config=configuracion
)

def rotar_api_key():
    """Cambia a la siguiente API Key en la lista y transfiere la memoria del chat."""
    global client, chat, indice_key
    indice_key = (indice_key + 1) % len(API_KEYS)
    print(f"\n[SISTEMA] Límite de cuota detectado. Cambiando automáticamente a la API Key #{indice_key + 1}...")
    
    # Extraer el historial de la conversación actual para no perder la memoria
    historial = None
    if hasattr(chat, 'history'):
        historial = chat.history
    
    # Crear un nuevo cliente con la nueva API Key y reconstruir el chat
    client = genai.Client(api_key=API_KEYS[indice_key])
    if historial:
        chat = client.chats.create(model='gemini-2.5-flash', config=configuracion, history=historial)
    else:
        chat = client.chats.create(model='gemini-2.5-flash', config=configuracion)

def ejecutar_herramienta(call):
    """Ejecuta la función local de Python según la solicitud de Gemini."""
    name = call.name
    args = call.args
    print(f"\n[SISTEMA] JAVIER está ejecutando la herramienta local: {name}...")
    
    if name == "crear_archivo_sandbox":
        return crear_archivo_sandbox(args["nombre_archivo"], args["contenido"])
    elif name == "leer_archivo_sandbox":
        return leer_archivo_sandbox(args["nombre_archivo"])
    elif name == "enviar_whatsapp":
        return enviar_whatsapp(args["numero"], args["mensaje"])
    elif name == "buscar_wikipedia":
        return buscar_wikipedia(args["consulta"])
    elif name == "buscar_internet_vivo":
        return buscar_internet_vivo(args["consulta"])
    elif name == "listar_inventario":
        return listar_inventario()
    elif name == "buscar_inventario_categoria":
        return buscar_inventario_categoria(args["categoria"])
    elif name == "buscar_articulo_inventario":
        return buscar_articulo_inventario(args["nombre_articulo"])
    elif name == "actualizar_inventario":
        return actualizar_inventario(args["nombre_articulo"], args["cantidad"])
    elif name == "tba_info_equipo":
        return tba_info_equipo(args["numero_equipo"])
    elif name == "tba_eventos_equipo":
        return tba_eventos_equipo(args["numero_equipo"], args["anio"])
    elif name == "tba_ranking_evento":
        return tba_ranking_evento(args["codigo_evento"])
    elif name == "guardar_aprendizaje":
        return guardar_aprendizaje(args["tema"], args["contenido"])
    elif name == "leer_aprendizajes":
        return leer_aprendizajes()
    elif name == "crear_plugin":
        return crear_plugin(args["nombre_plugin"], args["codigo_python"])
    elif name == "ejecutar_plugin":
        return ejecutar_plugin(args["nombre_plugin"], args["nombre_funcion"], args.get("argumentos", "{}"))
    elif name == "listar_plugins":
        return listar_plugins()
    elif name == "activar_pensamiento_profundo":
        return activar_pensamiento_profundo(args["consulta"])
    elif name == "explorar_directorio":
        return explorar_directorio(args["ruta_absoluta"])
    elif name == "leer_archivo_absoluto":
        return leer_archivo_absoluto(args["ruta_absoluta"])
    elif name == "escribir_archivo_absoluto":
        return escribir_archivo_absoluto(args["ruta_absoluta"], args["contenido"])
    return "Error: Herramienta no reconocida localmente."

import os
import json

ARCHIVO_PRESUPUESTO = os.path.join(os.path.dirname(__file__), "memoria", "uso_api.json")
LIMITE_DIARIO = 150 # Límite muy estricto (150 mensajes) para garantizar $0 costo.

def verificar_presupuesto():
    """Lleva un conteo diario en disco para asegurar que no nos cobren en la tarjeta."""
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
    """Envía la pregunta a Gemini. Rota keys en 429/503 y espera si todas fallan.
    Máximo 2 ciclos completos de keys (6 intentos en total con 3 keys)."""
    
    global chat
    MAX_CICLOS = 2
    intentos_totales = 0
    max_intentos = len(API_KEYS) * MAX_CICLOS
    
    if callback_consola:
        callback_consola("SISTEMA_INTERNO", f"Iniciando ciclo cognitivo para consulta de usuario...")

    while intentos_totales < max_intentos:
        try:
            response = chat.send_message(pregunta)

            while response.function_calls:
                function_responses = []
                for call in response.function_calls:
                    if callback_consola:
                        args_str = ", ".join([f"{k}={v}" for k, v in call.args.items()])
                        callback_consola("PENSAMIENTO", f"Requiriendo herramienta: {call.name}({args_str})")
                        
                    resultado = ejecutar_herramienta(call)
                    
                    if callback_consola:
                        res_preview = str(resultado)[:200] + ("..." if len(str(resultado)) > 200 else "")
                        callback_consola("RESULTADO_HERRAMIENTA", f"Ejecución completada. Retorno:\n{res_preview}")
                        
                    function_responses.append(
                        types.Part.from_function_response(
                            name=call.name,
                            response={"result": resultado}
                        )
                    )
                response = chat.send_message(function_responses)

            return response.text.strip()

        except Exception as e:
            error_msg = str(e)
            intentos_totales += 1

            if "429" in error_msg or "503" in error_msg:
                # Si todavía quedan keys por probar en este ciclo, rota
                if intentos_totales % len(API_KEYS) != 0:
                    rotar_api_key()
                else:
                    # Completó un ciclo completo de todas las keys: esperar 30s
                    print(f"\n[SISTEMA] Todas las API Keys agotadas. Esperando 30 segundos antes de reintentar...")
                    time.sleep(30)
                    rotar_api_key()  # Empezar en la siguiente key al reiniciar
            else:
                # Error distinto (ej. error de red), no tiene caso reintentar
                print(f"Error en Gemini: {e}")
                break

    print("[SISTEMA] Se agotaron todos los reintentos posibles.")
    return "Lo siento, el sistema de inteligencia artificial no está disponible en este momento. Intenta de nuevo en un minuto."

