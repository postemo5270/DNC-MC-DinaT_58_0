import math
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass

# =============================================================================
# CONSTANTES Y TABLAS NORMATIVAS (NEC / NTC 2050)
# =============================================================================

# NEC 240.6 - Amperios Estándar para Fusibles e Interruptores
BREAKERS_ESTANDAR: List[int] = [
    15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 
    110, 125, 150, 175, 200, 225, 250, 300, 350, 400, 450, 
    500, 600, 700, 800, 1000, 1200, 1600, 2000, 2500, 3000, 4000, 5000, 6000
]

# Tabla 310.16 (Ampacidades Base 90°C para XHHW-2, THHN, etc.) - Ajustado a Tabla
TABLA_310_16: Dict[str, Dict[str, float]] = { 
    # Calibre: { 'CU': Amp, 'AL': Amp } - Usando columna 90°C para dimensionamiento base
    "14":  {"CU": 25,  "AL": 0}, 
    "12":  {"CU": 30,  "AL": 25}, 
    "10":  {"CU": 40,  "AL": 35}, 
    "8":   {"CU": 55,  "AL": 45}, 
    "6":   {"CU": 75,  "AL": 55}, 
    "4":   {"CU": 95,  "AL": 75}, 
    "3":   {"CU": 115, "AL": 85}, 
    "2":   {"CU": 130, "AL": 100}, 
    "1":   {"CU": 145, "AL": 115}, 
    "1/0": {"CU": 170, "AL": 135}, 
    "2/0": {"CU": 195, "AL": 150}, 
    "3/0": {"CU": 225, "AL": 175}, 
    "4/0": {"CU": 260, "AL": 205}, 
    "250": {"CU": 290, "AL": 230}, 
    "300": {"CU": 320, "AL": 255}, 
    "350": {"CU": 350, "AL": 280}, 
    "500": {"CU": 430, "AL": 350}, 
    "600": {"CU": 475, "AL": 385}, 
    "750": {"CU": 535, "AL": 435} 
}

# Tabla 250.122 (Puesta a Tierra) - (Breaker, Cu, Al)
TABLA_250_122: List[Tuple[int, str, str]] = [ 
    (15, "14", "12"), (20, "12", "10"), (60, "10", "8"), (100, "8", "6"), 
    (200, "6", "4"), (300, "4", "2"), (400, "3", "1"), (500, "2", "1/0"), 
    (600, "1", "2/0"), (800, "1/0", "3/0"), (1000, "2/0", "4/0"), 
    (1200, "3/0", "250"), (1600, "4/0", "350"), (2000, "250", "400"), 
    (2500, "350", "600"), (3000, "400", "600"), (4000, "500", "800"), 
    (5000, "700", "1200"), (6000, "800", "1200") 
]

ORDEN_CALIBRES: List[str] = [
    "14", "12", "10", "8", "6", "4", "3", "2", "1", 
    "1/0", "2/0", "3/0", "4/0", "250", "300", "350", "500", "600", "750"
]

# Tabla 9 NEC (Resistencia y Reactancia Ohm/km) - Simplificada para lógica
DATOS_FISICOS: Dict[str, Dict[str, float]] = { 
    # r_cu_pvc, x_pvc, r_al_pvc (Asumiendo ducto PVC/No magnético por defecto)
    "14": {"r_cu": 10.2, "r_al": 16.7, "x": 0.19}, 
    "12": {"r_cu": 6.6,  "r_al": 10.8, "x": 0.18}, 
    "10": {"r_cu": 3.9,  "r_al": 6.4,  "x": 0.16}, 
    "8":  {"r_cu": 2.56, "r_al": 4.2,  "x": 0.17}, 
    "6":  {"r_cu": 1.61, "r_al": 2.66, "x": 0.16}, 
    "4":  {"r_cu": 1.02, "r_al": 1.67, "x": 0.15}, 
    "3":  {"r_cu": 0.82, "r_al": 1.35, "x": 0.15}, 
    "2":  {"r_cu": 0.62, "r_al": 1.05, "x": 0.14}, 
    "1":  {"r_cu": 0.51, "r_al": 0.82, "x": 0.14}, 
    "1/0": {"r_cu": 0.39, "r_al": 0.66, "x": 0.13}, 
    "2/0": {"r_cu": 0.31, "r_al": 0.52, "x": 0.13}, 
    "3/0": {"r_cu": 0.25, "r_al": 0.43, "x": 0.12}, 
    "4/0": {"r_cu": 0.20, "r_al": 0.33, "x": 0.12}, 
    "250": {"r_cu": 0.17, "r_al": 0.28, "x": 0.12}, 
    "300": {"r_cu": 0.14, "r_al": 0.23, "x": 0.11}, 
    "350": {"r_cu": 0.12, "r_al": 0.20, "x": 0.11}, 
    "500": {"r_cu": 0.089,"r_al": 0.14, "x": 0.11}, 
    "600": {"r_cu": 0.075,"r_al": 0.12, "x": 0.11}, 
    "750": {"r_cu": 0.062,"r_al": 0.10, "x": 0.11} 
}

# =============================================================================
# VARIABLES GLOBALES
# =============================================================================
MEMORIA_TABLEROS: List['Tablero'] = []
SISTEMA_PROYECTO: Optional['Tablero'] = None

# =============================================================================
# CLASES DE DOMINIO (LÓGICA VARIABLES.XLSX)
# =============================================================================

class Circuito:
    def __init__(self, 
                 tag: str, 
                 descripcion: str, 
                 p_input: float, 
                 unidad: str,  # hp, kW, kVA
                 tension: int, 
                 fases: int, 
                 fp: float, 
                 eff: float, 
                 longitud: float, 
                 mat: str, # Cobre / Aluminio
                 tipo_aislam: str, # THHN, XHHW-2
                 t_aislamiento_cable: int, # 60, 75, 90
                 tipo_instalacion: str, # BD-Sub, BD-Vista, Bandeja, Red aerea
                 req_neutro: str, # SI / NO
                 t_ambiente: int = 30,
                 tipo_carga: str = "Continua",
                 material_canalizacion: str = "No Magnético"):
        
        # Variables de Entrada [cite: 89-101]
        self.tag = tag
        self.descripcion = descripcion
        self.p_input = float(p_input)
        self.unidad = unidad
        self.tension = int(tension)
        self.fases = int(fases) # 1, 2, 3
        self.fp = float(fp)
        self.eff = float(eff)
        self.l_m = float(longitud)
        self.mat = mat.upper() # CU / AL
        self.tipo_aislam = tipo_aislam
        self.t_aislamiento_cable = int(t_aislamiento_cable)
        self.tipo_instalacion = tipo_instalacion
        self.req_neutro = req_neutro.upper()
        self.t_ambiente = int(t_ambiente)
        self.tipo_carga = tipo_carga
        self.material_canalizacion = material_canalizacion

        # Cache de Resultados
        self.res: Dict[str, Any] = {}

    def _calcular_kva(self) -> float:
        """Ref: Variable kVA_Calc [cite: 93]"""
        if self.unidad == "hp":
            return (self.p_input * 0.746) / (self.eff * self.fp)
        elif self.unidad == "kW":
            return self.p_input / (self.eff * self.fp)
        else: # kVA
            return self.p_input

    def _calcular_inom(self, kva: float) -> float:
        """Ref: Variable I.Nom (A) [cite: 94]"""
        if self.fases == 3:
            return (kva * 1000) / (1.732 * self.tension)
        elif self.fases == 2:
            return (kva * 1000) / self.tension
        else: # 1F
            return (kva * 1000) / self.tension

    def _obtener_f_temp(self) -> float:
        """Ref: Variable F.Temp (NEC 310.15(B)(1)) [cite: 95]"""
        # Simplificación de tabla basada en NEC para 90°C (aislamiento típico industrial)
        # Si T_Aislamiento es 90°C:
        t = self.t_ambiente
        if self.t_aislamiento_cable == 90:
            if 21 <= t <= 25: return 1.04
            if 26 <= t <= 30: return 1.00
            if 31 <= t <= 35: return 0.96
            if 36 <= t <= 40: return 0.91
            if 41 <= t <= 45: return 0.87
            if 46 <= t <= 50: return 0.82
            if 51 <= t <= 55: return 0.76
            if 56 <= t <= 60: return 0.71
            if 61 <= t <= 70: return 0.58
            if 71 <= t <= 80: return 0.41
        # Implementar otras columnas si es necesario (60/75), por ahora default 1.0
        return 1.0

    def _obtener_f_agrup(self, num_cond_activos: int) -> float:
        """Ref: Variable F.Agrup [cite: 96]"""
        if self.tipo_instalacion in ["Red aérea", "Bandeja"]:
            return 1.00
        
        # Para BD-Sub o BD-Vista (Tuberías)
        n = num_cond_activos
        if 1 <= n <= 3: return 1.00
        if 4 <= n <= 6: return 0.80
        if 7 <= n <= 9: return 0.70
        if 10 <= n <= 20: return 0.50
        if 21 <= n <= 30: return 0.45
        if 31 <= n <= 40: return 0.40
        if n >= 41: return 0.35
        return 1.0

    def _seleccionar_breaker(self, i_diseno: float) -> int:
        """Ref: Variable I_Proteccion (NEC 240.6) [cite: 115]"""
        for b in BREAKERS_ESTANDAR:
            if b >= i_diseno:
                return b
        return 6000 # Max value

    def _obtener_tierra(self, breaker: int) -> str:
        """Ref: Variable Calibre_Tierra (NEC 250.122) [cite: 116]"""
        col_idx = 1 if self.mat == "CU" else 2 # Col 1=Cu, Col 2=Al
        for fila in TABLA_250_122:
            if fila[0] >= breaker:
                return fila[col_idx]
        return "750"

    def ejecutar_calculo(self) -> Dict[str, Any]:
        # 1. Cálculos de Potencia y Corriente
        kva_calc = self._calcular_kva()
        i_nom = self._calcular_inom(kva_calc)
        
        # Variable I.Dis (A) [cite: 94]
        factor_seguridad = 1.25 if self.tipo_carga == "Continua" else 1.0
        i_dis = i_nom * factor_seguridad
        
        # Variable I_Proteccion
        i_proteccion = self._seleccionar_breaker(i_dis)

        # Factores Fijos Iniciales
        f_temp = self._obtener_f_temp()
        
        # Lógica Iterativa para Selección de Calibre
        cal_elegido = "ERR"
        n_cond_fase = 1
        i_corregida_unit = 0.0
        caida_v = 0.0
        reg_porc = 0.0
        estado = "ALERTA"
        nota = ""

        encontrado = False
        idx_cal = 0
        
        while not encontrado and n_cond_fase <= 6: # Limite de seguridad
            if idx_cal >= len(ORDEN_CALIBRES):
                n_cond_fase += 1
                idx_cal = 0 # Reiniciar barrido de calibres
                continue
            
            cal_actual = ORDEN_CALIBRES[idx_cal]
            
            # Validar existencia en tabla (ej: AL no tiene 14)
            key_mat = "CU" if self.mat == "Cobre" or self.mat == "CU" else "AL"
            if TABLA_310_16[cal_actual][key_mat] == 0:
                idx_cal += 1
                continue

            # 1. Factor de Agrupamiento (Depende de cantidad de conductores totales)
            # Asumimos: (Fases * N_cond) + (Neutro si aplica y cuenta). Tierra no cuenta NEC 310.15.
            # Simplificación: Total portadores corriente = Fases * N_cond
            total_portadores = self.fases * n_cond_fase
            f_agrup = self._obtener_f_agrup(total_portadores)

            # 2. Ampacidad Corregida
            i_base = TABLA_310_16[cal_actual][key_mat] # Variable I_Base_Tabla [cite: 111]
            i_corr_unit = i_base * f_temp * f_agrup # Variable I_Corregida_Unit [cite: 112]
            capacidad_total = i_corr_unit * n_cond_fase

            # Criterio Ampacidad: Capacidad >= I_Proteccion (Conservador) o >= I_Diseno
            # El excel Variable Estado_Cumplimiento dice: SI Capacidad_Total >= I_Proteccion -> OK [cite: 120]
            if capacidad_total < i_proteccion:
                idx_cal += 1
                continue

            # 3. Criterio Regulación
            # Datos Físicos
            d_fis = DATOS_FISICOS.get(cal_actual, {"r_cu": 0.1, "r_al": 0.1, "x": 0.1})
            r_ac = d_fis["r_cu"] if key_mat == "CU" else d_fis["r_al"] # Variable Resistencia_AC [cite: 104]
            x_l = d_fis["x"] # Variable Reactancia_X [cite: 108]
            
            # Variable Z_Eficaz [cite: 110]
            phi = math.acos(self.fp)
            z_eficaz = (r_ac * self.fp) + (x_l * math.sin(phi))

            # Variable Caida_Tension_V [cite: 113]
            k = 1.732 if self.fases == 3 else 2
            # Dividimos L por 1000 porque Z está en Ohm/km
            v_drop = (k * i_dis * (self.l_m / 1000.0) * z_eficaz) / n_cond_fase
            
            # Variable Regulacion_Porc [cite: 114]
            reg = (v_drop / self.tension) * 100.0

            if reg <= 3.0:
                encontrado = True
                cal_elegido = cal_actual
                i_corregida_unit = i_corr_unit
                caida_v = v_drop
                reg_porc = reg
                estado = "OK"
            else:
                idx_cal += 1

        # Variable Calibre_Tierra [cite: 116]
        cal_tierra = self._obtener_tierra(i_proteccion)

        # Variables Neutro [cite: 120]
        cant_neutro = n_cond_fase if self.req_neutro == "SI" else 0
        cal_neutro = cal_elegido if self.req_neutro == "SI" else "N/A"

        # Guardar resultados
        self.res = {
            "I_Nominal": i_nom,
            "I_Diseno": i_dis,
            "I_Proteccion": i_proteccion,
            "Calibre_Fase": cal_elegido,
            "Cant_Cond_Fase": n_cond_fase,
            "Calibre_Tierra": cal_tierra,
            "Req_Neutro": self.req_neutro,
            "Config_Neutro": f"{cant_neutro}x{cal_neutro}",
            "I_Corregida_Unit": i_corregida_unit,
            "Capacidad_Total": i_corregida_unit * n_cond_fase,
            "Caida_V": caida_v,
            "Reg_Porc": reg_porc,
            "Estado_Cumplimiento": estado,
            "Config_Fase": f"{n_cond_fase}x{cal_elegido}"
        }
        return self.res

class Tablero:
    def __init__(self, nombre: str, voltaje: int, fases: int):
        self.nombre = nombre
        self.voltaje = voltaje
        self.fases = fases
        self.circuitos: List[Circuito] = []
        self.sub_tableros: List['Tablero'] = []
        self.padre: Optional[str] = None

    def agregar_c(self, c: Circuito) -> None:
        self.circuitos.append(c)

    def agregar_sub(self, t: 'Tablero') -> None:
        t.padre = self.nombre
        self.sub_tableros.append(t)
    
    def total_kw(self) -> float:
        kw_propios = sum(c._calcular_kva() * c.fp for c in self.circuitos) # Aprox KW
        kw_hijos = sum(s.total_kw() for s in self.sub_tableros)
        return kw_propios + kw_hijos
