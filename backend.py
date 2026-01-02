import math
from typing import List, Dict, Optional, Tuple, Union, Any
from dataclasses import dataclass

# =============================================================================
# 0. EXCEPCIONES DEL DOMINIO (Semantic Exceptions)
# =============================================================================
class EngineeringError(Exception):
    """Clase base para errores de lógica de ingeniería."""
    pass

class AmpacityError(EngineeringError):
    """Lanzada cuando no se encuentra un conductor capaz de manejar la corriente."""
    pass

class ConfigurationError(EngineeringError):
    """Lanzada cuando hay parámetros físicos inválidos (ej: material desconocido)."""
    pass

# =============================================================================
# 1. TABLAS NEC Y CONSTANTES (INMUTABLES)
# =============================================================================
# Tabla 310.16 (Ampacidades Base 90°C)
TABLA_310_16_CU: Dict[str, Tuple[int, int]] = { 
    "14": (20, 25), "12": (25, 30), "10": (35, 40), "8": (50, 55), 
    "6": (65, 75), "4": (85, 95), "3": (100, 115), "2": (115, 130), 
    "1": (130, 145), "1/0": (150, 170), "2/0": (175, 195), "3/0": (200, 225), 
    "4/0": (230, 260), "250": (255, 290), "300": (285, 320), "350": (310, 350), 
    "500": (380, 430), "600": (420, 475), "750": (475, 535) 
}

TABLA_310_16_AL: Dict[str, Tuple[int, int]] = { 
    "12": (20, 25), "10": (30, 35), "8": (40, 45), "6": (50, 55), 
    "4": (65, 75), "3": (75, 85), "2": (90, 100), "1": (100, 115), 
    "1/0": (120, 135), "2/0": (135, 150), "3/0": (155, 175), "4/0": (180, 205), 
    "250": (205, 230), "300": (230, 255), "350": (250, 280), "500": (310, 350), 
    "600": (340, 385), "750": (385, 435) 
}

# Tabla 250.122 (Puesta a Tierra) - Estructura: (Amperios, Cu, Al)
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

# Datos Físicos (Resistencia y Reactancia) - Unidades: Ohms/km (Aproximado para ejemplo)
DATOS_FISICOS: Dict[str, Dict[str, float]] = { 
    "14": {"r_cu": 10.2, "x_cu": 0.19, "r_al": 16.7, "x_al": 0.19}, 
    "12": {"r_cu": 6.6, "x_cu": 0.18, "r_al": 10.8, "x_al": 0.18}, 
    "10": {"r_cu": 3.9, "x_cu": 0.16, "r_al": 6.4, "x_al": 0.16}, 
    "8": {"r_cu": 2.56, "x_cu": 0.17, "r_al": 4.2, "x_al": 0.17}, 
    "6": {"r_cu": 1.61, "x_cu": 0.16, "r_al": 2.66, "x_al": 0.16}, 
    "4": {"r_cu": 1.02, "x_cu": 0.15, "r_al": 1.67, "x_al": 0.15}, 
    "3": {"r_cu": 0.82, "x_cu": 0.15, "r_al": 1.35, "x_al": 0.15}, 
    "2": {"r_cu": 0.62, "x_cu": 0.14, "r_al": 1.05, "x_al": 0.14}, 
    "1": {"r_cu": 0.51, "x_cu": 0.14, "r_al": 0.82, "x_al": 0.14}, 
    "1/0": {"r_cu": 0.39, "x_cu": 0.13, "r_al": 0.66, "x_al": 0.13}, 
    "2/0": {"r_cu": 0.31, "x_cu": 0.13, "r_al": 0.52, "x_al": 0.13}, 
    "3/0": {"r_cu": 0.25, "x_cu": 0.12, "r_al": 0.43, "x_al": 0.12}, 
    "4/0": {"r_cu": 0.20, "x_cu": 0.12, "r_al": 0.33, "x_al": 0.12}, 
    "250": {"r_cu": 0.17, "x_cu": 0.12, "r_al": 0.28, "x_al": 0.12}, 
    "300": {"r_cu": 0.14, "x_cu": 0.11, "r_al": 0.23, "x_al": 0.11}, 
    "350": {"r_cu": 0.12, "x_cu": 0.11, "r_al": 0.20, "x_al": 0.11}, 
    "500": {"r_cu": 0.089, "x_cu": 0.11, "r_al": 0.14, "x_al": 0.11}, 
    "600": {"r_cu": 0.075, "x_cu": 0.11, "r_al": 0.12, "x_al": 0.11}, 
    "750": {"r_cu": 0.062, "x_cu": 0.11, "r_al": 0.10, "x_al": 0.11} 
}

class TipoInstalacion:
    DUCTO = "Ducto (PVC/IMC)"
    BANDEJA = "Bandeja Portacables"
    AIRE = "Aire Libre"
    BANCO_DUCTOS = "Banco de Ductos"
    AGRUP = "Agrupado"

class TipoOperacion:
    CONTINUA = "Continua" 
    NO_CONTINUA = "No Continua"
    RESPALDO = "Respaldo"

# =============================================================================
# 2. MEMORIA GLOBAL (Persistencia Volátil)
# =============================================================================
MEMORIA_TABLEROS: List['Tablero'] = []
SISTEMA_PROYECTO: Optional['Tablero'] = None

# =============================================================================
# 3. CLASES DE DOMINIO
# =============================================================================

class Circuito:
    def __init__(self, 
                 tag: str, 
                 descripcion: str, 
                 potencia_nominal_kw: float, 
                 voltaje: int, 
                 fases: int, 
                 factor_potencia: float = 0.9, 
                 tipo_operacion: str = TipoOperacion.CONTINUA, 
                 longitud_mts: float = 10.0, 
                 calibre_usuario: str = "12", 
                 material_conductor: str = "CU",
                 tipo_instalacion: str = TipoInstalacion.DUCTO,
                 eficiencia: float = 1.0, 
                 temp_ambiente: int = 30, 
                 factor_agrupamiento: float = 1.0,
                 aislamiento: str = "THHN"):
        
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
        
        # Cache de resultados
        self._res_conductor: Optional[Dict[str, Any]] = None

    @staticmethod
    def obtener_factor_temp(t_amb: int) -> float:
        """Determina el factor de corrección por temperatura (NEC 310.15(B))."""
        if 26 <= t_amb <= 30: return 1.0
        elif 31 <= t_amb <= 35: return 0.96
        elif 36 <= t_amb <= 40: return 0.91
        elif 41 <= t_amb <= 45: return 0.87
        elif 46 <= t_amb <= 50: return 0.82
        elif 51 <= t_amb <= 60: return 0.71
        elif t_amb > 60: return 0.41
        return 1.0

    def calcular_corriente_nominal(self) -> float:
        """Calcula I_nominal basada en potencia, voltaje y factores."""
        denom = self.voltaje * self.factor_potencia * self.eficiencia
        if self.fases == 3: 
            denom *= math.sqrt(3)
        elif self.fases == 1:
            pass # Monofásico (L-N o L-L dependiendo del voltaje, asumimos formula base)
            
        return (self.potencia_nominal_kw * 1000.0) / denom if denom != 0 else 0.0

    def calcular_corriente_diseno(self) -> float:
        """Aplica el factor de seguridad NEC 210.19(A)(1)."""
        inom = self.calcular_corriente_nominal()
        factor = 1.25 if self.tipo_operacion == TipoOperacion.CONTINUA else 1.0
        return inom * factor

    def obtener_tierra(self, amp_proteccion: float) -> str:
        """Selecciona conductor de tierra según NEC 250.122."""
        # Columna 1 para CU, Columna 2 para AL
        col = 1 if self.material_conductor == "CU" else 2
        
        for fila in TABLA_250_122:
            if fila[0] >= amp_proteccion: 
                return fila[col]
        return "750" # Fallback al máximo definido

    def ejecutar_seleccion_conductor(self) -> Dict[str, Any]:
        """
        Algoritmo principal de dimensionamiento iterativo.
        Retorna un diccionario con todos los parámetros técnicos calculados.
        """
        i_diseno = self.calcular_corriente_diseno()
        
        # Factores de corrección
        f_temp = self.obtener_factor_temp(self.temp_ambiente)
        f_total = f_temp * self.factor_agrupamiento
        
        # Selección de tabla base
        if self.material_conductor == "CU":
            tabla_amp = TABLA_310_16_CU
        elif self.material_conductor == "AL":
            tabla_amp = TABLA_310_16_AL
        else:
            raise ConfigurationError(f"Material desconocido: {self.material_conductor}")
        
        cal_elegido: Optional[str] = None
        n_cond = 1
        nota = ""
        reg_pct, v_caida, amp_real = 0.0, 0.0, 0.0
        
        idx = 0
        encontrado = False
        
        # --- BUCLE DE ITERACIÓN DE CALIBRES ---
        while not encontrado:
            if idx >= len(ORDEN_CALIBRES):
                # Si se acaban los calibres, aumentamos hilos por fase y reiniciamos
                n_cond += 1
                idx = 0
                if n_cond > 6: 
                    nota = "CRÍTICO: >6 conductores/fase"
                    break 
            
            cal = ORDEN_CALIBRES[idx]
            
            # Validación de existencia en tabla (ej: AL no tiene 14 AWG)
            if cal not in tabla_amp:
                idx += 1
                continue

            # 1. Criterio de Ampacidad (Corriente)
            amp_base = tabla_amp[cal][1] # Columna 75°C/90°C según terminales (Usamos índice 1 que es la mayor)
            amp_sitio = amp_base * n_cond * f_total
            
            if amp_sitio < i_diseno:
                idx += 1
                continue # No cumple ampacidad, siguiente calibre
                
            # 2. Criterio de Regulación (Caída de Tensión)
            datos_fisicos = DATOS_FISICOS.get(cal, {"r_cu":0.2, "x_cu":0.1})
            r_key = f"r_{self.material_conductor.lower()}"
            x_key = f"x_{self.material_conductor.lower()}"
            
            r = datos_fisicos.get(r_key, 0.2)
            x = datos_fisicos.get(x_key, 0.1)
            
            # Método Impedancia Eficaz: Zeff = R*cos(phi) + X*sin(phi)
            phi = math.acos(self.factor_potencia)
            z_eff = (r * self.factor_potencia) + (x * math.sin(phi))
            
            # Caída unitaria (V L-N)
            dv_u = z_eff * i_diseno * (self.longitud_mts / 1000.0)
            
            # Caída total ajustada por n_cond y fases
            if self.fases == 3:
                v_drop = (math.sqrt(3) * dv_u) / n_cond
            else:
                v_drop = (2 * dv_u) / n_cond
                
            reg = (v_drop / self.voltaje) * 100.0
            
            if reg <= 3.0:
                # CUMPLE AMBOS CRITERIOS
                cal_elegido = cal
                amp_real = amp_sitio
                v_caida = v_drop
                reg_pct = reg
                encontrado = True
            else:
                # No cumple regulación, probar siguiente calibre mayor
                idx += 1
        
        # Selección de Tierra
        gnd = self.obtener_tierra(i_diseno)
        
        # Construcción del Resultado
        self._res_conductor = {
            "I_Nominal": self.calcular_corriente_nominal(), 
            "I_Diseno": i_diseno,
            "Calibre": cal_elegido if cal_elegido else "ERR", 
            "N_Hilos": n_cond, 
            "Tierra": gnd,
            "Amp_Real": amp_real, 
            "V_Caida": v_caida, 
            "Reg_Pct": reg_pct,
            "Nota": nota, 
            "Config": f"{n_cond}x{cal_elegido}+{gnd}(GND)",
            # Metadatos para reporte
            "Meta_F_Temp": f_temp,
            "Meta_F_Agrup": self.factor_agrupamiento,
            "Meta_Material": self.material_conductor
        }
        return self._res_conductor

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
        """Recursividad: Suma cargas propias + cargas de subtableros."""
        kw_propios = sum(c.potencia_nominal_kw for c in self.circuitos)
        kw_hijos = sum(s.total_kw() for s in self.sub_tableros)
        return kw_propios + kw_hijos
