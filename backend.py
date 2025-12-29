import math
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional

# --- MEMORIA GLOBAL ---
MEMORIA_TABLEROS = [] 

# --- TABLAS REFERENCIA ---
ORDEN_CALIBRES = ["12", "10", "8", "6", "4", "2", "1/0", "2/0", "3/0", "4/0", "250", "350", "500", "750", "1000"]
DOE_2016_LIQUID_3PH = {15: 98.65, 30: 98.93, 45: 99.03, 75: 99.19, 112.5: 99.25, 150: 99.28, 225: 99.33, 300: 99.36, 500: 99.42, 750: 99.46, 1000: 99.49, 1500: 99.52, 2000: 99.55, 2500: 99.57}
DOE_2016_DRY_MV_3PH = {15: 97.50, 30: 97.90, 45: 98.10, 75: 98.33, 112.5: 98.52, 150: 98.65, 225: 98.75, 300: 98.83, 500: 98.94, 750: 99.03, 1000: 99.08, 1500: 99.14, 2000: 99.18, 2500: 99.22}
KVA_ESTANDAR = sorted(list(DOE_2016_LIQUID_3PH.keys()))

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
    MAX_CAIDA: float = 3.0
    _res_conductor: dict = field(default_factory=dict)

    def calcular_corriente_carga(self):
        p_op = self.potencia_nominal_kw * self.factor_utilizacion * (1.02 if self.tiene_vfd or self.tiene_sut else 1.0)
        fp = self.factor_potencia if self.factor_potencia > 0 else 0.9
        kva = p_op / fp
        # kVAR = S * sen(acos(fp))
        kvar = kva * math.sin(math.acos(fp))
        
        i_nom = (kva * 1000) / ((math.sqrt(3) * self.voltaje) if self.fases == 3 else self.voltaje) if self.voltaje > 0 else 0
        return i_nom, p_op, kva, kvar

    def ejecutar_seleccion_conductor(self):
        i_nom, _, _, _ = self.calcular_corriente_carga()
        i_req = i_nom * 1.25
        bd = BD_CABLES_AL if self.material_conductor == "AL" else BD_CABLES_CU
        cal_opt = "750"
        for c in ORDEN_CALIBRES:
            if c not in bd: continue
            amp = bd[c].get("A_AIRE" if self.tipo_instalacion in [TipoInstalacion.AIRE, TipoInstalacion.BANDEJA, TipoInstalacion.TRENZADA] else "A_DUCTO", 0)
            dv = (math.sqrt(3) if self.fases==3 else 2) * i_nom * ((bd[c]["R"]*0.9 + bd[c]["X"]*0.43)/1000) * self.longitud_mts / self.voltaje * 100
            if amp >= i_req and dv <= self.MAX_CAIDA: cal_opt = c; break
        
        idx_u = ORDEN_CALIBRES.index(self.calibre_usuario) if self.calibre_usuario in ORDEN_CALIBRES else -1
        sel_cal = cal_opt if idx_u < ORDEN_CALIBRES.index(cal_opt) else self.calibre_usuario
        dat = bd.get(sel_cal, bd["12"])
        n = 1
        while n <= 10:
            amp = dat.get("A_AIRE" if self.tipo_instalacion in [TipoInstalacion.AIRE, TipoInstalacion.BANDEJA] else "A_DUCTO", 0)
            if amp * n >= i_req: break
            n += 1
        self._res_conductor = {"Calibre": sel_cal, "N": n, "Mat": self.material_conductor, "Capacidad": amp*n, "I_Req": i_req, "I_Nom": i_nom, "DV": 0.0, "Nota": "Ok", "Instalacion": self.tipo_instalacion.value}
        return self._res_conductor

@dataclass
class Transformador:
    tipo: str; refrigeracion: str; reserva_deseada: float; voltaje_pri: float; voltaje_sec: float
    
    def calcular(self, kva_load, kw_load, kvar_load):
        # 1. Selección
        kva_req = kva_load / (1 - (self.reserva_deseada/100.0) if self.reserva_deseada < 100 else 0.1)
        kva_com = next((k for k in KVA_ESTANDAR if k >= kva_req), KVA_ESTANDAR[-1])
        
        # 2. Eficiencia DOE
        tbl = DOE_2016_DRY_MV_3PH if self.tipo == "SECO" else DOE_2016_LIQUID_3PH
        k_eff = max([k for k in tbl.keys() if k <= kva_com], default=15)
        eff_doe = tbl.get(k_eff, 98.0)
        
        # 3. Pérdidas y Potencia de Entrada
        # Asumimos que las pérdidas son puramente activas (calor)
        p_perdidas = kw_load * (1 - eff_doe/100.0)
        p_in = kw_load + p_perdidas
        q_in = kvar_load # Simplificación: Q del trafo no se suma en este nivel básico
        s_in = math.sqrt(p_in**2 + q_in**2)
        fp_in = p_in / s_in if s_in > 0 else 0.9
        
        cargabilidad = (kva_load / kva_com * 100) if kva_com else 0
        
        i_pri = (kva_com * 1000) / (math.sqrt(3) * self.voltaje_pri)
        i_sec = (kva_com * 1000) / (math.sqrt(3) * self.voltaje_sec)
        
        return {
            "kVA_Com": kva_com, "Eff": eff_doe, "Perdidas_kW": p_perdidas,
            "P_In": p_in, "Q_In": q_in, "S_In": s_in, "FP_In": fp_in,
            "Cargabilidad": cargabilidad, "I_Pri_Nom": i_pri, "I_Sec_Nom": i_sec
        }

class Tablero:
    def __init__(self, nombre, voltaje, fases):
        self.nombre = nombre; self.voltaje = voltaje; self.fases = fases
        self.circuitos = []; self.sub_tableros = []; self.trafo_asociado = None
    def agregar_c(self, c): self.circuitos.append(c)
    def agregar_s(self, t): self.sub_tableros.append(t)
    
    def get_datos_totales(self):
        tot_kw = 0.0; tot_kvar = 0.0; tot_kva = 0.0
        for c in self.circuitos:
            _, kw, _, kvar = c.calcular_corriente_carga()
            tot_kw += kw
            tot_kvar += kvar
        
        # Suma vectorial para S total
        tot_kva = math.sqrt(tot_kw**2 + tot_kvar**2)
        fp_avg = tot_kw / tot_kva if tot_kva > 0 else 0.9
        
        # Corriente de carga total
        i_carga = (tot_kva * 1000) / (math.sqrt(3) * self.voltaje) if self.voltaje > 0 else 0
        i_barraje = i_carga * 1.25 # Criterio NEC
        
        return {
            "kW": tot_kw, "kVAR": tot_kvar, "kVA": tot_kva, "FP": fp_avg,
            "I_Carga": i_carga, "I_Barraje": i_barraje
        }

SISTEMA_PROYECTO = Tablero("General", 480, 3)
