import math
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional

# --- MEMORIA GLOBAL PARA LISTAS DESPLEGABLES ---
MEMORIA_TABLEROS = [] 

# --- TABLAS REFERENCIA ---
ORDEN_CALIBRES = ["12", "10", "8", "6", "4", "2", "1/0", "2/0", "3/0", "4/0", "250", "350", "500", "750", "1000"]
DOE_2016_LIQUID_3PH = {15: 98.65, 30: 98.93, 45: 99.03, 75: 99.19, 112.5: 99.25, 150: 99.28, 225: 99.33, 300: 99.36, 500: 99.42, 750: 99.46, 1000: 99.49, 1500: 99.52, 2000: 99.55, 2500: 99.57}
DOE_2016_DRY_MV_3PH = {15: 97.50, 30: 97.90, 45: 98.10, 75: 98.33, 112.5: 98.52, 150: 98.65, 225: 98.75, 300: 98.83, 500: 98.94, 750: 99.03, 1000: 99.08, 1500: 99.14, 2000: 99.18, 2500: 99.22}
KVA_ESTANDAR = sorted(list(DOE_2016_LIQUID_3PH.keys()))

BD_CABLES_CU = {"12": {"A_DUCTO": 30, "A_AIRE": 40, "R": 6.6, "X": 0.177}, "10": {"A_DUCTO": 40, "A_AIRE": 55, "R": 3.9, "X": 0.164}, "8": {"A_DUCTO": 55, "A_AIRE": 80, "R": 2.56, "X": 0.171}, "6": {"A_DUCTO": 75, "A_AIRE": 105, "R": 1.61, "X": 0.167}, "4": {"A_DUCTO": 95, "A_AIRE": 140, "R": 1.02, "X": 0.157}, "2": {"A_DUCTO": 130, "A_AIRE": 190, "R": 0.62, "X": 0.148}, "1/0": {"A_DUCTO": 170, "A_AIRE": 260, "R": 0.39, "X": 0.141}, "2/0": {"A_DUCTO": 195, "A_AIRE": 300, "R": 0.33, "X": 0.141}, "3/0": {"A_DUCTO": 225, "A_AIRE": 350, "R": 0.26, "X": 0.138}, "4/0": {"A_DUCTO": 260, "A_AIRE": 405, "R": 0.21, "X": 0.135}, "250": {"A_DUCTO": 290, "A_AIRE": 455, "R": 0.179, "X": 0.139}, "350": {"A_DUCTO": 350, "A_AIRE": 570, "R": 0.129, "X": 0.099}, "500": {"A_DUCTO": 430, "A_AIRE": 700, "R": 0.093, "X": 0.069}, "750": {"A_DUCTO": 535, "A_AIRE": 855, "R": 0.06, "X": 0.118}, "1000": {"A_DUCTO": 615, "A_AIRE": 1055, "R": 0.04, "X": 0.115}}
BD_CABLES_AL = {"12": {"A_DUCTO": 25, "A_AIRE": 35, "R": 10.49, "X": 0.177}, "10": {"A_DUCTO": 35, "A_AIRE": 40, "R": 6.56, "X": 0.164}, "8": {"A_DUCTO": 45, "A_AIRE": 60, "R": 4.27, "X": 0.171}, "6": {"A_DUCTO": 60, "A_AIRE": 80, "R": 2.66, "X": 0.167}, "4": {"A_DUCTO": 75, "A_AIRE": 115, "R": 1.67, "X": 0.157}, "2": {"A_DUCTO": 100, "A_AIRE": 150, "R": 1.05, "X": 0.148}, "1/0": {"A_DUCTO": 135, "A_AIRE": 205, "R": 0.66, "X": 0.141}, "2/0": {"A_DUCTO": 150, "A_AIRE": 235, "R": 0.52, "X": 0.138}, "3/0": {"A_DUCTO": 175, "A_AIRE": 275, "R": 0.42, "X": 0.135}, "4/0": {"A_DUCTO": 205, "A_AIRE": 315, "R": 0.33, "X": 0.131}, "250": {"A_DUCTO": 230, "A_AIRE": 355, "R": 0.28, "X": 0.128}, "350": {"A_DUCTO": 280, "A_AIRE": 445, "R": 0.21, "X": 0.125}, "500": {"A_DUCTO": 350, "A_AIRE": 545, "R": 0.14, "X": 0.121}, "750": {"A_DUCTO": 435, "A_AIRE": 700, "R": 0.09, "X": 0.118}, "1000": {"A_DUCTO": 500, "A_AIRE": 845, "R": 0.06, "X": 0.115}}

class TipoOperacion(Enum):
    CONTINUA = "C"
    RESPALDO = "R"
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
        kva = p_op / (self.factor_potencia if self.factor_potencia > 0 else 0.9)
        i_nom = (kva * 1000) / ((math.sqrt(3) * self.voltaje) if self.fases == 3 else self.voltaje) if self.voltaje > 0 else 0
        return i_nom, p_op, kva

    def ejecutar_seleccion_conductor(self):
        i_nom, _, _ = self.calcular_corriente_carga(); i_req = i_nom * 1.25; bd = BD_CABLES_AL if self.material_conductor == "AL" else BD_CABLES_CU
        # Lógica resumida de selección
        cal_opt = "750"
        for c in ORDEN_CALIBRES:
            if c not in bd: continue
            amp = bd[c].get("A_AIRE" if self.tipo_instalacion in [TipoInstalacion.AIRE, TipoInstalacion.BANDEJA, TipoInstalacion.TRENZADA] else "A_DUCTO", 0)
            dv = (math.sqrt(3) if self.fases==3 else 2) * i_nom * ((bd[c]["R"]*0.9 + bd[c]["X"]*0.43)/1000) * self.longitud_mts / self.voltaje * 100
            if amp >= i_req and dv <= self.MAX_CAIDA:
                cal_opt = c; break
        
        # Guardar resultado simplificado
        self._res_conductor = {"Calibre": cal_opt, "I_Nom": i_nom, "Capacidad": amp, "DV": dv, "Mat": self.material_conductor, "Nota": "Calculado"}
        return self._res_conductor

@dataclass
class Transformador:
    tipo: str; refrigeracion: str; reserva_deseada: float; voltaje_pri: float; voltaje_sec: float
    kva_comercial: float = 0.0; eficiencia_doe: float = 0.0; cargabilidad: float = 0.0; fp_entrada: float = 0.0; i_pri_nom: float = 0.0; i_sec_nom: float = 0.0; kva_requerido: float = 0.0
    
    def calcular(self, kva_load, kw_load):
        self.kva_requerido = kva_load / (1 - (self.reserva_deseada/100.0) if self.reserva_deseada < 100 else 0.1)
        self.kva_comercial = next((k for k in KVA_ESTANDAR if k >= self.kva_requerido), KVA_ESTANDAR[-1])
        
        tbl = DOE_2016_DRY_MV_3PH if self.tipo == "SECO" else DOE_2016_LIQUID_3PH
        k_eff = max([k for k in tbl.keys() if k <= self.kva_comercial], default=15)
        self.eficiencia_doe = tbl.get(k_eff, 98.0)
        
        self.cargabilidad = (kva_load / self.kva_comercial * 100) if self.kva_comercial else 0
        perdidas = kw_load * (1 - self.eficiencia_doe/100.0)
        s_in = math.sqrt((kw_load + perdidas)**2 + (kva_load * math.sin(math.acos(kw_load/kva_load if kva_load else 1)))**2)
        self.fp_entrada = (kw_load + perdidas) / s_in if s_in else 0.9
        
        self.i_pri_nom = (self.kva_comercial*1000)/(math.sqrt(3)*self.voltaje_pri)
        self.i_sec_nom = (self.kva_comercial*1000)/(math.sqrt(3)*self.voltaje_sec)
        return {"kVA_Com": self.kva_comercial, "Eff": self.eficiencia_doe, "Cargabilidad": self.cargabilidad, "FP_Final": self.fp_entrada, "I_Pri": self.i_pri_nom, "I_Sec": self.i_sec_nom}

class Tablero:
    def __init__(self, nombre, voltaje, fases):
        self.nombre = nombre; self.voltaje = voltaje; self.fases = fases
        self.circuitos = []; self.sub_tableros = []; self.trafo_asociado = None
    def agregar_c(self, c): self.circuitos.append(c)
    def agregar_s(self, t): self.sub_tableros.append(t)
    def calcular_carga_total(self):
        tot_kw = sum(c.calcular_corriente_carga()[1] for c in self.circuitos)
        tot_kva = sum(c.calcular_corriente_carga()[2] for c in self.circuitos)
        return tot_kva, tot_kw

SISTEMA_PROYECTO = Tablero("General", 480, 3)
