import math

# --- DOMINIO: LISTAS DE VALIDACIÓN Y TABLAS NEC (MC-ELE-Variables) ---

# Listas desplegables definidas en Excel [cite: 37, 38, 43, 46, 47, 48]
LISTA_TENSION = [120, 208, 220, 480, 4160, 6900, 13200, 34500]
LISTA_FASES = ["3F", "2F", "1F"]
LISTA_UNIDADES_POT = ["hp", "kW", "kVA"]
LISTA_TIPO_CARGA = ["Continua", "Respaldo"]
LISTA_INSTALACION = ["BD-Sub", "BD-Vista", "Bandeja", "Red aérea"]
LISTA_MAT_CANALIZACION = ["No Magnético", "Magnético"]
LISTA_MAT_CONDUCTOR = ["Cobre", "Aluminio"]
LISTA_AISLAMIENTO = ["TW", "THW", "THHN", "THWN-2", "XHHW-2"]
LISTA_TEMP_AISLAMIENTO = [60, 75, 90]
LISTA_CALIBRES = [ # [cite: 50] Lista estándar simplificada
    "14", "12", "10", "8", "6", "4", "3", "2", "1", "1/0", "2/0", "3/0", "4/0", 
    "250", "300", "350", "400", "500", "600", "750"
]

# --- LÓGICA DE NEGOCIO Y CÁLCULOS PRELIMINARES ---

def calcular_kva_entrada(potencia, unidad, eficiencia, fp):
    """
    Calcula los kVA según la unidad de entrada[cite: 40].
    """
    try:
        if unidad == "hp":
            return (potencia * 0.746) / (eficiencia * fp)
        elif unidad == "kW":
            return potencia / (eficiencia * fp)
        elif unidad == "kVA":
            return potencia
        else:
            return 0.0
    except ZeroDivisionError:
        return 0.0

def calcular_corriente_nominal(kva, tension, fases):
    """
    Calcula I.Nom según fases[cite: 40].
    """
    if tension == 0: return 0.0
    
    if fases == "3F":
        return (kva * 1000) / (1.732 * tension)
    elif fases in ["2F", "1F"]:
        return (kva * 1000) / tension
    return 0.0

def validar_requerimiento_magnetico(tipo_instalacion):
    """
    Define si se requiere preguntar por Material Canalización.
    Visible solo si es Tubería (BD).
    """
    return tipo_instalacion in ["BD-Sub", "BD-Vista"]

# Aquí irían las Tablas de Ampacidad y Factores (NEC 310.15) como diccionarios
# Se implementarán en la fase de cálculo detallado.
