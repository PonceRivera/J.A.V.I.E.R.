
def sumar(a, b):
    return a + b

def restar(a, b):
    return a - b

def multiplicar(a, b):
    return a * b

def dividir(a, b):
    if b == 0:
        return "Error: División por cero"
    return a / b

# Para integrales y derivadas, necesitaríamos una librería de cálculo simbólico.
# Por ahora, estas serían funciones placeholder.
def integral_indefinida(expresion, variable):
    return f"Calculando la integral indefinida de {expresion} con respecto a {variable} (requiere librería de cálculo simbólico)."

def derivada(expresion, variable):
    return f"Calculando la derivada de {expresion} con respecto a {variable} (requiere librería de cálculo simbólico)."
