from motor_voz import hablar, escuchar_comando
from base_datos import buscar_articulo
from cerebro import pensar_respuesta

callback_ui = None

def procesar_comando(comando):
    """Procesa el comando y decide qué acción tomar."""
    global callback_ui

    comando_low = comando.lower()

    if "salir" in comando_low or "apagar" in comando_low or "descansa" in comando_low:
        hablar("Apagando sistemas. Hasta luego Jaegers.")
        return False

    # Palabras que indican una consulta al inventario
    palabras_inventario = ["dónde está", "dónde están", "donde esta", "donde estan",
                           "busca", "encuentra", "dónde quedó", "cuántas", "cuantas",
                           "cuántos", "cuantos", "hay", "tenemos", "tienen"]

    es_consulta_inventario = any(p in comando_low for p in palabras_inventario)

    if es_consulta_inventario:
        articulo = comando_low
        # Limpiar palabras clave del inventario
        for p in palabras_inventario:
            articulo = articulo.replace(p, "")
        # Limpiar palabras de relleno y tiempo
        palabras_relleno = ["el ", "la ", "los ", "las ", "un ", "una ",
                            "actualmente", "ahora", "en este momento",
                            "disponibles", "disponible", "en el taller",
                            "en inventario", "?", "¿", "qué ", "cuál "]
        for p in palabras_relleno:
            articulo = articulo.replace(p, "")
        articulo = articulo.strip()

        # Si quedó muy poco (pregunta vaga), pasar directo a Gemini
        if len(articulo) <= 2:
            respuesta_ia = pensar_respuesta(comando, callback_consola=callback_ui)
            hablar(respuesta_ia)
            return True

        resultado = buscar_articulo(articulo)

        # Si no se encontró en inventario, usar Gemini como respaldo
        if resultado.startswith("Lo siento"):
            respuesta_ia = pensar_respuesta(comando, callback_consola=callback_ui)
            hablar(respuesta_ia)
        else:
            hablar(resultado)
        return True

    # Para cualquier otra pregunta, usar el cerebro Gemini
    respuesta_ia = pensar_respuesta(comando, callback_consola=callback_ui)
    hablar(respuesta_ia)
    return True


def iniciar_javier(callback_chat=None):
    global callback_ui
    callback_ui = callback_chat
    corriendo = True
    while corriendo:
        comando = escuchar_comando()

        if comando != "none":
            if callback_chat:
                callback_chat("Tú (voz)", comando)
            corriendo = procesar_comando(comando)

if __name__ == "__main__":
    # 1) Mostrar pantalla de carga con diagnósticos reales
    from splash import mostrar_splash
    mostrar_splash()

    # 2) Arrancar la interfaz gráfica principal
    import gui
    import customtkinter as ctk

    app = ctk.CTk()
    mi_javier = gui.JavierGUI(app)
    app.mainloop()

