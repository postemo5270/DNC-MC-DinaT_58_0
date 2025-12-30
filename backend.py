import math
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional

# --- MEMORIA GLOBAL ---
MEMORIA_TABLEROS = [] 

# --- TABLAS REFERENCIA ---
ORDEN_CALIBRES = ["12", "10", "8", "6", "4", "2", "1/0", "2/0", "3/0", "4/0", "250", "350", "500", "750", "1000"]

# Eficiencias DOE 2016
DOE_2016_LIQUID_3PH = {15: 98.65, 30: 98.93, 45: 99.03, 75: 99.19, 112.5: 99.25, 150: 99.28, 225: 99.33, 300: 99.36, 500: 99.42, 750: 99.46, 1000: 99.49, 1500: 99.52, 2000: 99.55, 2500: 99.57}
DOE_2016_DRY_MV_3PH = {15: 97.50, 30: 97.90, 45: 98.10, 75: 98.33, 112.5: 98.52, 150: 98.65, 225: 98.75, 300: 98.83, 500: 98.94, 750: 99.03, 1000: 99.08, 1500: 99.14, 2000: 99.18, 2500: 99.22}
KVA_ESTANDAR = sorted(list(DOE_2016_LIQUID_3PH.keys()))

# Base de Datos Cables (Ampacidad Base a 30°C)
BD_CABLES_CU = {"12": {"A_DUCTO": 30, "A_AIRE": 40, "R": 6.6, "X": 0.177}, "10": {"A_DUCTO": 40, "A_AIRE": 55, "R": 3.9, "X": 0.164}, "8": {"A_DUCTO": 55, "A_AIRE": 80, "R": 2.56, "X": 0.171}, "6": {"A_DUCTO": 75, "A_AIRE": 105, "R": 1.61, "X": 0.167}, "4": {"A_DUCTO": 95, "A_AIRE": 140, "R": 1.02, "X": 0.157}, "2": {"A_DUCTO": 130, "A_AIRE": 190, "R": 0.62, "X": 0.148}, "1/0": {"A_DUCTO": 170, "A_AIRE": 260, "R": 0.39, "X": 0.141}, "2/0": {"A_DUCTO": 195, "A_AIRE": 300, "R": 0.33, "X": 0.141}, "3/0": {"A_DUCTO": 225, "A_AIRE": 350, "R": 0.26, "X": 0.138}, "4/0": {"A_DUCTO": 260, "A_AIRE": 405, "R": 0.21, "X": 0.135}, "250": {"A_DUCTO": 290, "A_AIRE": 455, "R": 0.179, "X": 0.139}, "350": {"A_DUCTO": 350, "A_AIRE": 570, "R": 0.129, "X": 0.099}, "500": {"A_DUCTO": 430, "A_AIRE": 700, "R": 0.093, "X": 0.069}, "750": {"A_DUCTO": 535, "A_AIRE": 855, "R": 0.06, "X": 0.118}, "1000": {"A_DUCTO": 615, "A_AIRE": 1055, "R": 0.04, "X": 0.115}}
BD_CABLES_AL = {"12": {"A_DUCTO": 25, "A_AIRE": 35, "R": 10.49, "X": 0.177}, "10": {"A_DUCTO": 35, "A_AIRE": 40, "R": 6.56, "X": 0.164}, "8": {"A_DUCTO": 45, "A_AIRE": 60, "R": 4.27, "X": 0.171}, "6": {"A_DUCTO": 60, "A_AIRE": 80, "R": 2.66, "X": 0.167}, "4": {"A_DUCTO": 75, "A_AIRE": 115, "R": 1.67, "X": 0.157}, "2": {"A_DUCTO": 100, "A_AIRE": 150, "R": 1.05, "X": 0.148}, "1/0": {"A_DUCTO": 135, "A_AIRE": 205, "R": 0.66, "X": 0.141}, "2/0": {"A_DUCTO": 150, "A_AIRE": 235, "R": 0.52, "X": 0.138}, "3/0": {"A_DUCTO": 175, "A_AIRE": 275, "R": 0.42, "X": 0.135}, "4/0": {"A_DUCTO": 205, "A_AIRE": 315, "R": 0.33, "X": 0.131}, "250": {"A_DUCTO": 230, "A_AIRE": 355, "R": 0.28, "X": 0.128}, "350": {"A_DUCTO": 280, "A_AIRE": 445, "R": 0.21, "X": 0.125}, "500": {"A_DUCTO": 350, "A_AIRE": 545, "R": 0.14, "X": 0.121}, "750": {"A_DUCTO": 435, "A_AIRE": 700, "R": 0.09, "X": 0.118}, "1000": {"A_DUCTO": 500, "A_AIRE": 845, "R": 0.06, "X": 0.115}}

class TipoOperacion(Enum):
    CONTINUA = "C"; RESPALDO = "R"
class TipoInstalacion(Enum):
    DUCTO = "DUCTO"; AIRE = "AIRE"; AGRUP = "AGRUP"; BANDEJA = "BANDEJA"; BANCO_DUCTOS = "BANCO"; TRENZADA = "RED TRENZADA"

@dataclass
class Circuito:
    tag: str; descripcion: str; potencia_nominal_kw: float; voltaje: float; fases: int; factor_potencia: float
    tipo_operacion: TipoOperacion; longitud_mts: float; calibre_usuario: str; material_conductor: str; tipo_instalacion: TipoInstalacion
    factor_utilizacion: float = 1.0; tiene_vfd: bool = False; tiene_sut: bool = False
    
    # Nuevos atributos para detalle
    eficiencia: float = 1.0 
    temp_ambiente: float = 30.0 # Grados C
    factor_agrupamiento: float = 1.0
    
    MAX_CAIDA: float = 3.0
    _res_conductor: dict = field(default_factory=dict)

    def calcular_corriente_carga(self):
        # Asumimos que potencia_nominal_kw es Potencia Mecánica/Útil si eff < 1.0
        # P_elec = P_nom / eff
        p_elec_kw = self.potencia_nominal_kw / self.eficiencia
        
        # Considerar armónicos VFD
        if self.tiene_vfd or self.tiene_sut: p_elec_kw *= 1.02
        
        fp = self.factor_potencia if self.factor_potencia > 0 else 0.9
        kva = p_elec_kw / fp
        kvar = kva * math.sin(math.acos(fp))
        
        denom = (math.sqrt(3) * self.voltaje) if self.fases == 3 else self.voltaje
        i_nom = (kva * 1000) / denom if self.voltaje > 0 else 0
        
        return i_nom, p_elec_kw, kva, kvar

    def ejecutar_seleccion_conductor(self):
        i_nom, _, _, _ = self.calcular_corriente_carga()
        i_req = i_nom * 1.25
        
        bd = BD_CABLES_AL if self.material_conductor == "AL" else BD_CABLES_CU
        
        # Factores de Derrateo
        # Por ahora simplificado a lo que pediste:
        f_temp = 1.0 # Implementar lógica de temp si se requiere despues
        f_agrup = self.factor_agrupamiento
        f_total = f_temp * f_agrup
        
        # Lógica de Selección
        cal_opt = "750"
        for c in ORDEN_CALIBRES:
            if c not in bd: continue
            amp_base = bd[c].get("A_AIRE" if self.tipo_instalacion in [TipoInstalacion.AIRE, TipoInstalacion.BANDEJA, TipoInstalacion.TRENZADA] else "A_DUCTO", 0)
            amp_derrateada = amp_base * f_total
            
            # Chequeo Ampacidad
            if amp_derrateada < i_req: continue
            
            # Chequeo Regulación
            dv = (math.sqrt(3) if self.fases==3 else 2) * i_nom * ((bd[c]["R"]*0.9 + bd[c]["X"]*0.43)/1000) * self.longitud_mts / self.voltaje * 100
            if dv <= self.MAX_CAIDA:
                cal_opt = c; break
        
        # Respetar usuario si es mayor
        idx_u = ORDEN_CALIBRES.index(self.calibre_usuario) if self.calibre_usuario in ORDEN_CALIBRES else -1
        idx_o = ORDEN_CALIBRES.index(cal_opt)
        sel_cal = cal_opt if idx_u < idx_o else self.calibre_usuario
        
        # Recalcular finales con seleccionado
        dat = bd.get(sel_cal, bd["12"])
        n = 1
        while n <= 10:
            amp_base = dat.get("A_AIRE" if self.tipo_instalacion in [TipoInstalacion.AIRE, TipoInstalacion.BANDEJA] else "A_DUCTO", 0)
            cap_derrateada = amp_base * f_total * n
            if cap_derrateada >= i_req: break
            n += 1
        
        dv_final = (math.sqrt(3) if self.fases==3 else 2) * i_nom * ((dat["R"]*0.9 + dat["X"]*0.43)/1000) * self.longitud_mts / self.voltaje * 100
        
        # String Configuración
        # Ej: 2x(3x1/0 AWG + 1x4 AWG) - Tierra simplificada a mismo calibre o menor
        tierra = "4" # Simplificacion
        config_str = f"{n}x(3x{sel_cal} AWG + 1x{tierra} AWG)" if self.fases == 3 else f"{n}x(2x{sel_cal} AWG + 1x{tierra} AWG)"

        self._res_conductor = {
            "Calibre": sel_cal, "N": n, "Mat": self.material_conductor,
            "Cap_Base": amp_base,
            "Cap_Real": cap_derrateada,
            "I_Req": i_req, "I_Nom": i_nom, "DV": dv_final, 
            "Config": config_str,
            "F_Temp": f_temp, "F_Agrup": f_agrup, "F_Total": f_total,
            "Instalacion": self.tipo_instalacion.value
        }
        return self._res_conductor




def _calcular_factor_temp_real(self):
        """
        Calcula F.T. basado en Tabla NEC 310.15(B)(2)(a) (Imagen provista).
        Base 30°C, Aislamiento 90°C.
        """
        t = self.temp_ambiente
        
        # Rangos exactos de la tabla
        if t <= 10: return 1.15
        if t <= 15: return 1.12
        if t <= 20: return 1.08
        if t <= 25: return 1.04
        if t <= 30: return 1.00 # Base
        if t <= 35: return 0.96
        if t <= 40: return 0.91
        if t <= 45: return 0.87
        if t <= 50: return 0.82
        if t <= 55: return 0.76
        if t <= 60: return 0.71
        if t <= 65: return 0.65
        if t <= 70: return 0.58
        if t <= 75: return 0.50
        if t <= 80: return 0.41
        if t <= 85: return 0.29
        
        # Para temperaturas > 85°C según la tabla es 0.00
        return 0.00

@dataclass
class Transformador:
    tipo: str; refrigeracion: str; reserva_deseada: float; voltaje_pri: float; voltaje_sec: float
    kva_requerido: float = 0.0; kva_comercial: float = 0.0; eficiencia_doe: float = 0.0; cargabilidad: float = 0.0
    
    def calcular(self, kva_load, kw_load, kvar_load):
        self.kva_requerido = kva_load / (1 - (self.reserva_deseada/100.0) if self.reserva_deseada < 100 else 0.1)
        self.kva_comercial = next((k for k in KVA_ESTANDAR if k >= self.kva_requerido), KVA_ESTANDAR[-1])
        tbl = DOE_2016_DRY_MV_3PH if self.tipo == "SECO" else DOE_2016_LIQUID_3PH
        k_eff = max([k for k in tbl.keys() if k <= self.kva_comercial], default=15)
        self.eficiencia_doe = tbl.get(k_eff, 98.0)
        eff_dec = self.eficiencia_doe/100.0
        p_perdidas = kw_load * (1 - eff_dec)
        p_in = kw_load + p_perdidas
        s_in = math.sqrt(p_in**2 + kvar_load**2)
        fp_in = p_in / s_in if s_in > 0 else 0.9
        self.cargabilidad = (kva_load / self.kva_comercial * 100) if self.kva_comercial else 0
        i_pri = (self.kva_comercial * 1000) / (math.sqrt(3) * self.voltaje_pri)
        i_sec = (self.kva_comercial * 1000) / (math.sqrt(3) * self.voltaje_sec)
        return {"kVA_Com": self.kva_comercial, "Eff": self.eficiencia_doe, "Perdidas_kW": p_perdidas, "S_In": s_in, "FP_In": fp_in, "Cargabilidad": self.cargabilidad, "I_Pri_Nom": i_pri, "I_Sec_Nom": i_sec}

class Tablero:
    def __init__(self, nombre, voltaje, fases):
        self.nombre = nombre; self.voltaje = voltaje; self.fases = fases
        self.circuitos = []; self.sub_tableros = []; self.trafo_asociado = None
    def agregar_c(self, c): self.circuitos.append(c)
    def agregar_s(self, t): self.sub_tableros.append(t)
    def get_datos_totales(self):
        tot_kw = 0.0; tot_kvar = 0.0
        for c in self.circuitos:
            _, kw, _, kvar = c.calcular_corriente_carga()
            tot_kw += kw; tot_kvar += kvar
        tot_kva = math.sqrt(tot_kw**2 + tot_kvar**2)
        fp_avg = tot_kw / tot_kva if tot_kva > 0 else 0.9
        i_carga = (tot_kva * 1000) / (math.sqrt(3) * self.voltaje) if self.voltaje > 0 else 0
        return {"kW": tot_kw, "kVAR": tot_kvar, "kVA": tot_kva, "FP": fp_avg, "I_Carga": i_carga, "I_Barraje": i_carga * 1.25}

SISTEMA_PROYECTO = Tablero("General", 480, 3)
