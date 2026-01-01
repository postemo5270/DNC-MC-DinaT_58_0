import math

# --- CONSTANTES Y TABLAS NEC ---

# Tabla 310.15(B)(16) (Ahora 310.16 en NEC 2020/2023) - 75°C y 90°C
# Formato: "Calibre": (Amp_75C, Amp_90C)
TABLA_310_16_CU = {
    "14": (20, 25), "12": (25, 30), "10": (35, 40), "8": (50, 55),
    "6": (65, 75), "4": (85, 95), "3": (100, 115), "2": (115, 130),
    "1": (130, 145), "1/0": (150, 170), "2/0": (175, 195),
    "3/0": (200, 225), "4/0": (230, 260), "250": (255, 290),
    "300": (285, 320), "350": (310, 350), "500": (380, 430),
    "600": (420, 475), "750": (475, 535)
}

TABLA_310_16_AL = {
    "12": (20, 25), "10": (30, 35), "8": (40, 45), "6": (50, 55),
    "4": (65, 75), "3": (75, 85), "2": (90, 100), "1": (100, 115),
    "1/0": (120, 135), "2/0": (135, 150), "3/0": (155, 175),
    "4/0": (180, 205), "250": (205, 230), "300": (230, 255),
    "350": (250, 280), "500": (310, 350), "600": (340, 385),
    "750": (385, 435)
}

# Tabla 250.122 - Conductor de Puesta a Tierra (Min Size GND)
# Basado en el Rating del Breaker (Amperios) -> Calibre AWG/kcmil (Cobre, Aluminio)
TABLA_250_122 = [
    (15, "14", "12"), (20, "12", "10"), (60, "10", "8"), (100, "8", "6"),
    (200, "6", "4"), (300, "4", "2"), (400, "3", "1"), (500, "2", "1/0"),
    (600, "1", "2/0"), (800, "1/0", "3/0"), (1000, "2/0", "4/0"),
    (1200, "3/0", "250"), (1600, "4/0", "350"), (2000, "250", "400"),
    (2500, "350", "600"), (3000, "400", "600"), (4000, "500", "800"),
    (5000, "700", "1200"), (6000, "800", "1200")
]

ORDEN_CALIBRES = ["14", "12", "10", "8", "6", "4", "3", "2", "1", 
                  "1/0", "2/0", "3/0", "4/0", "250", "300", "350", "500", "600", "750"]

# Datos Físicos (Resistencia/Reactancia aprox NEC Cap 9 Tabla 8 y 9)
# R_Ohm/km a 75C aprox para tubería acero (peor caso)
DATOS_FISICOS = {
    "14": {"r_cu": 10.2, "x_cu": 0.19, "r_al": 16.7, "x_al": 0.19},
    "12": {"r_cu": 6.6, "x_cu": 0.18, "r_al": 10.8, "x_al": 0.18},
    "10": {"r_cu": 3.9, "x_cu": 0.16, "r_al": 6.4, "x_al": 0.16},
    "8":  {"r_cu": 2.56, "x_cu": 0.17, "r_al": 4.2, "x_al": 0.17},
    "6":  {"r_cu": 1.61, "x_cu": 0.16, "r_al": 2.66, "x_al": 0.16},
    "4":  {"r_cu": 1.02, "x_cu": 0.15, "r_al": 1.67, "x_al": 0.15},
    "3":  {"r_cu": 0.82, "x_cu": 0.15, "r_al": 1.35, "x_al": 0.15},
    "2":  {"r_cu": 0.62, "x_cu": 0.14, "r_al": 1.05, "x_al": 0.14},
    "1":  {"r_cu": 0.51, "x_cu": 0.14, "r_al": 0.82, "x_al": 0.14},
    "1/0": {"r_cu": 0.39, "x_cu": 0.13, "r_al": 0.66, "x_al": 0.13},
    "2/0": {"r_cu": 0.31, "x_cu": 0.13, "r_al": 0.52, "x_al": 0.13},
    "3/0": {"r_cu": 0.25, "x_cu": 0.12, "r_al": 0.43, "x_al": 0.12},
    "4/0": {"r_cu": 0.20, "x_cu": 0.12, "r_al": 0.33, "x_al": 0.12},
    "250": {"r_cu": 0.17, "x_cu": 0.12, "r_al": 0.28, "x_al": 0.12},
    "300": {"r_cu": 0.14, "x_cu": 0.11, "r_al": 0.23, "x_al": 0.11},
    "350": {"r_cu": 0.12, "x_cu": 0.11, "r_al": 0.20, "x_al": 0.11},
    "500": {"r_cu": 0.089, "x_cu": 0.11, "r_al": 0.14, "x_al": 0.11},
    "600": {"r_cu": 0.075, "x_cu": 0.11, "r_al": 0.12, "x_al": 0.11},
    "750": {"r_cu": 0.062, "x_cu": 0.11, "r_al": 0.10, "x_al": 0.11},
}

# --- ENUMS ---
class TipoInstalacion:
    DUCTO = "Ducto"
    BANDEJA = "Bandeja"
    AIRE = "Aire Libre"
    BANCO_DUCTOS = "Banco de Ductos"
    TRENZADA = "Red Trenzada"
    AGRUP = "Agrupado"
    ENTER = "Enterrado Directo"

class TipoOperacion:
    CONTINUA = "Continua" # >= 3 horas (125%)
    NO_CONTINUA = "No Continua" # (100%)
    RESPALDO = "Respaldo/Standby"

# --- MEMORIA GLOBAL ---
MEMORIA_TABLEROS = []
SISTEMA_PROYECTO = None

# --- CLASES ---
class Circuito:
    def __init__(self, tag, descripcion, potencia_nominal_kw, voltaje, fases, 
                 factor_potencia=0.9, tipo_operacion=TipoOperacion.CONTINUA, 
                 longitud_mts=10.0, calibre_usuario="12", material_conductor="CU",
                 tipo_instalacion=TipoInstalacion.DUCTO,
                 eficiencia=1.0, temp_ambiente=30, factor_agrupamiento=1.0,
                 aislamiento="THHN/THWN-2"):
        
        # Datos Entrada Usuario
        self.tag = tag
        self.descripcion = descripcion
        self.potencia_nominal_kw = float(potencia_nominal_kw)
        self.voltaje = int(voltaje)
        self.fases = int(fases)
        self.factor_potencia = float(factor_potencia)
        self.tipo_operacion = tipo_operacion
        self.longitud_mts = float(longitud_mts)
        self.calibre_usuario = calibre_usuario
        self.material_conductor = material_conductor.upper()
        self.tipo_instalacion = tipo_instalacion
        self.eficiencia = float(eficiencia)
        self.temp_ambiente = int(temp_ambiente)
        self.factor_agrupamiento = float(factor_agrupamiento)
        self.aislamiento = aislamiento

        # Resultados Cálculo
        self._res_conductor = None

    def calcular_corriente_nominal(self):
        # I = kW * 1000 / (V * FP * Eff * raiz3)
        denom = self.voltaje * self.factor_potencia * self.eficiencia
        if self.fases == 3:
            denom *= math.sqrt(3)
        elif self.fases == 2:
            denom *= 1 # Depende config, asumimos L-L simple
        # Monofasico L-N o L-L ya considerado en voltaje input
        
        if denom == 0: return 0.0
        return (self.potencia_nominal_kw * 1000.0) / denom

    def calcular_corriente_diseno(self):
        inom = self.calcular_corriente_nominal()
        # NEC 210.19(A)(1): 125% para cargas continuas
        factor = 1.25 if self.tipo_operacion == TipoOperacion.CONTINUA else 1.0
        return inom * factor

    def obtener_tierra_nec_250_122(self, amperios_proteccion):
        # Retorna calibre string (ej: "10")
        # Busca en la tabla el primer valor donde rating >= proteccion
        col_idx = 1 if self.material_conductor == "CU" else 2
        for fila in TABLA_250_122:
            rating = fila[0]
            if rating >= amperios_proteccion:
                return fila[col_idx]
        return "750" # Default gigante si se pasa

    def ejecutar_seleccion_conductor(self):
        i_diseno = self.calcular_corriente_diseno()
        
        # 1. Factores de Corrección (Derating)
        # Temp (NEC 310.15(B)(2)(a)) - Simplificado para 90C base (THHN)
        # Rango 30C base.
        t = self.temp_ambiente
        f_temp = 1.0
        if 26 <= t <= 30: f_temp = 1.0
        elif 31 <= t <= 35: f_temp = 0.96
        elif 36 <= t <= 40: f_temp = 0.91
        elif 41 <= t <= 45: f_temp = 0.87
        elif 46 <= t <= 50: f_temp = 0.82
        elif 51 <= t <= 55: f_temp = 0.76
        elif 56 <= t <= 60: f_temp = 0.71
        elif 61 <= t <= 70: f_temp = 0.58
        elif 71 <= t <= 80: f_temp = 0.41
        
        # Agrupamiento
        f_agrup = self.factor_agrupamiento # Viene del input (slider o excel)
        
        f_total = f_temp * f_agrup
        
        # 2. Iteración de Calibres
        tabla_amp = TABLA_310_16_CU if self.material_conductor == "CU" else TABLA_310_16_AL
        
        calibre_elegido = None
        n_conductores = 1
        reg_pct = 0.0
        v_caida = 0.0
        nota = ""
        amp_real_cable = 0.0
        
        # Loop para encontrar conductor
        encontrado = False
        idx_cal = 0
        
        while not encontrado:
            cal_actual = ORDEN_CALIBRES[idx_cal]
            # Usamos columna 90C (indice 1) para Ampacidad Base (XHHW-2/THHN)
            amp_base = tabla_amp[cal_actual][1] 
            
            # Capacidad Real del Cable en sitio
            amp_sitio = amp_base * n_conductores * f_total
            
            # Criterio 1: Ampacidad
            if amp_sitio >= i_diseno:
                # Criterio 2: Caída de Tensión
                # dV = I * L * Z_eff
                # Z_eff aprox = R * FP + X * sen(acos(FP))
                # Simplificado a DC para tramos cortos o R_eff
                datos = DATOS_FISICOS.get(cal_actual, {"r_cu":0.2, "x_cu":0.1})
                r_key = f"r_{self.material_conductor.lower()}"
                x_key = f"x_{self.material_conductor.lower()}"
                r_linea = datos.get(r_key, 0.2)
                x_linea = datos.get(x_key, 0.1)
                
                # Formula Aprox AC: dV_fase_neutro = I * (R*cos + X*sen) * L/1000
                # Si es trifasico dV_linea = sqrt(3) * dV_fn
                
                phi = math.acos(self.factor_potencia)
                z_eff = (r_linea * self.factor_potencia) + (x_linea * math.sin(phi))
                
                dv_unit = z_eff * i_diseno * (self.longitud_mts / 1000.0)
                if self.fases == 3:
                    v_caida = math.sqrt(3) * dv_unit / n_conductores # Dividido N hilos
                else:
                    v_caida = 2 * dv_unit / n_conductores # Monofasico (ida y vuelta)
                
                reg_pct = (v_caida / self.voltaje) * 100.0
                
                if reg_pct <= 3.0: # Cumple 3%
                    calibre_elegido = cal_actual
                    amp_real_cable = amp_sitio
                    encontrado = True
                else:
                    # Falla regulación, subir calibre
                    idx_cal += 1
            else:
                idx_cal += 1
            
            # Si se acaban los calibres, duplicar conductor
            if idx_cal >= len(ORDEN_CALIBRES):
                n_conductores += 1
                idx_cal = 0 # Reiniciar búsqueda con 2 conductores
                if n_conductores > 4: # Safety break
                    calibre_elegido = "750"
                    nota = "Max Iter (Necesita Busbar)"
                    encontrado = True

        # Selección de Tierra (NEC 250.122)
        # Asumimos protección = siguiente estándar comercial arriba de I_diseno
        # Lista simple protecciones: 15, 20, 30, 40, 50, 60, 70, 80, 100...
        # Simplificación: Usamos I_diseno directo para buscar en tabla (lado seguro)
        cal_tierra = self.obtener_tierra_nec_250_122(i_diseno)

        self._res_conductor = {
            "I_Nominal": round(self.calcular_corriente_nominal(), 1),
            "I_Diseno": round(i_diseno, 1),
            "Calibre": calibre_elegido,
            "N_Hilos": n_conductores,
            "Tierra": cal_tierra,
            "Amp_Real": round(amp_real_cable, 1),
            "V_Caida": round(v_caida, 2),
            "Reg_Pct": round(reg_pct, 2),
            "Config": f"{n_conductores}x{calibre_elegido} AWG/kcmil + {cal_tierra}(GND)",
            "Nota": nota,
            "Factores": f"Ft={f_temp} Fa={f_agrup}"
        }
        return self._res_conductor

class Tablero:
    def __init__(self, nombre, voltaje, fases):
        self.nombre = nombre
        self.voltaje = voltaje
        self.fases = fases
        self.circuitos = [] # Lista de objetos Circuito (Cargas finales)
        self.sub_tableros = [] # Lista de objetos Tablero (Hijos)
        self.es_subtablero = False
        self.padre = None

    def agregar_c(self, circuito):
        self.circuitos.append(circuito)

    def agregar_subtablero(self, tablero_hijo):
        tablero_hijo.es_subtablero = True
        tablero_hijo.padre = self.nombre
        self.sub_tableros.append(tablero_hijo)

    def calcular_carga_total_kw(self):
        # Suma cargas propias
        total = sum(c.potencia_nominal_kw for c in self.circuitos)
        # Suma cargas de subtableros (recursivo)
        for sub in self.sub_tableros:
            total += sub.calcular_carga_total_kw()
        return total
