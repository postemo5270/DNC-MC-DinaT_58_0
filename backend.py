import math
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional

# =============================================================================
# MODULO BACKEND: BASE DE DATOS Y LÓGICA DE NEGOCIO
# =============================================================================

ORDEN_CALIBRES = [
    "12", "10", "8", "6", "4", "2", 
    "1/0", "2/0", "3/0", "4/0", "250", "350", "500", "750", "1000"
]

# --- BASE DE DATOS CONDUCTORES (Matriz Ducto/Aire/Agrupado) ---
BD_CABLES_CU = {
    "12":  {"A_DUCTO": 30,  "A_AIRE": 40,   "A_AGRUP": 33,  "R": 6.6,   "X": 0.177},
    "10":  {"A_DUCTO": 40,  "A_AIRE": 55,   "A_AGRUP": 45,  "R": 3.9,   "X": 0.164},
    "8":   {"A_DUCTO": 55,  "A_AIRE": 80,   "A_AGRUP": 66,  "R": 2.56,  "X": 0.171},
    "6":   {"A_DUCTO": 75,  "A_AIRE": 105,  "A_AGRUP": 89,  "R": 1.61,  "X": 0.167},
    "4":   {"A_DUCTO": 95,  "A_AIRE": 140,  "A_AGRUP": 117, "R": 1.02,  "X": 0.157},
    "2":   {"A_DUCTO": 130, "A_AIRE": 190,  "A_AGRUP": 158, "R": 0.62,  "X": 0.148},
    "1/0": {"A_DUCTO": 170, "A_AIRE": 260,  "A_AGRUP": 214, "R": 0.39,  "X": 0.141},
    "2/0": {"A_DUCTO": 195, "A_AIRE": 300,  "A_AGRUP": 247, "R": 0.33,  "X": 0.141},
    "3/0": {"A_DUCTO": 225, "A_AIRE": 350,  "A_AGRUP": 287, "R": 0.26,  "X": 0.138},
    "4/0": {"A_DUCTO": 260, "A_AIRE": 405,  "A_AGRUP": 335, "R": 0.21,  "X": 0.135},
    "250": {"A_DUCTO": 290, "A_AIRE": 455,  "A_AGRUP": 374, "R": 0.179, "X": 0.139},
    "350": {"A_DUCTO": 350, "A_AIRE": 570,  "A_AGRUP": 464, "R": 0.129, "X": 0.099}, 
    "500": {"A_DUCTO": 430, "A_AIRE": 700,  "A_AGRUP": 580, "R": 0.093, "X": 0.069},
    "750": {"A_DUCTO": 535, "A_AIRE": 855,  "A_AGRUP": 747, "R": 0.06,  "X": 0.118},
    "1000":{"A_DUCTO": 615, "A_AIRE": 1055, "A_AGRUP": 879, "R": 0.04,  "X": 0.115}
}

BD_CABLES_AL = {
    "12":  {"A_DUCTO": 25,  "A_AIRE": 35,   "A_AGRUP": 29,  "R": 10.49, "X": 0.177},
    "10":  {"A_DUCTO": 35,  "A_AIRE": 40,   "A_AGRUP": 33,  "R": 6.56,  "X": 0.164},
    "8":   {"A_DUCTO": 45,  "A_AIRE": 60,   "A_AGRUP": 51,  "R": 4.27,  "X": 0.171},
    "6":   {"A_DUCTO": 60,  "A_AIRE": 80,   "A_AGRUP": 69,  "R": 2.66,  "X": 0.167},
    "4":   {"A_DUCTO": 75,  "A_AIRE": 115,  "A_AGRUP": 91,  "R": 1.67,  "X": 0.157},
    "2":   {"A_DUCTO": 100, "A_AIRE": 150,  "A_AGRUP": 123, "R": 1.05,  "X": 0.148},
    "1/0": {"A_DUCTO": 135, "A_AIRE": 205,  "A_AGRUP": 167, "R": 0.66,  "X": 0.141},
    "2/0": {"A_DUCTO": 150, "A_AIRE": 235,  "A_AGRUP": 193, "R": 0.52,  "X": 0.138},
    "3/0": {"A_DUCTO": 175, "A_AIRE": 275,  "A_AGRUP": 224, "R": 0.42,  "X": 0.135}, 
    "4/0": {"A_DUCTO": 205, "A_AIRE": 315,  "A_AGRUP": 262, "R": 0.33,  "X": 0.131},
    "250": {"A_DUCTO": 230, "A_AIRE": 355,  "A_AGRUP": 292, "R": 0.28,  "X": 0.128},
    "350": {"A_DUCTO": 280, "A_AIRE": 445,  "A_AGRUP": 364, "R": 0.21,  "X": 0.125},
    "500": {"A_DUCTO": 350, "A_AIRE": 545,  "A_AGRUP": 458, "R": 0.14,  "X": 0.121},
    "750": {"A_DUCTO": 435, "A_AIRE": 700,  "A_AGRUP": 598, "R": 0.09,  "X": 0.118},
    "1000":{"A_DUCTO": 500, "A_AIRE": 845,  "A_AGRUP": 716, "R": 0.06,  "X": 0.115}
}

TRANSFORMADORES_NEMA = [15, 30, 45, 75, 112.5, 150, 225, 300, 500, 750, 1000, 1500, 2000, 2500]

class TipoOperacion(Enum):
    CONTINUA = "C"
    RESPALDO = "R"
    
class TipoInstalacion(Enum):
    DUCTO = "DUCTO"   
    AIRE = "AIRE"     
    AGRUP = "AGRUP"   

@dataclass
class Circuito:
    tag: str
    descripcion: str
    potencia_nominal_kw: float
    voltaje: float
    fases: int
    factor_potencia: float
    tipo_operacion: TipoOperacion
    longitud_mts: float
    calibre_usuario: str
    material_conductor: str 
    tipo_instalacion: TipoInstalacion 
    
    factor_utilizacion: float = 1.0
    tiene_vfd: bool = False
    tiene_sut: bool = False
    
    MAX_CAIDA: float = 3.0
    _res_conductor: dict = field(default_factory=dict)

    def _get_bd(self):
        return BD_CABLES_AL if self.material_conductor == "AL" else BD_CABLES_CU

    def calcular_corriente_carga(self):
        pot_op = self.potencia_nominal_kw * self.factor_utilizacion
        p_extra = 0.0
        if self.tiene_vfd: p_extra += 0.01
        if self.tiene_sut: p_extra += 0.01
        kw_carga = pot_op * (1 + p_extra)
        fp = self.factor_potencia if self.factor_potencia > 0 else 0.9
        kva = kw_carga / fp
        
        if self.voltaje > 0:
            denom = (math.sqrt(3) * self.voltaje) if self.fases == 3 else self.voltaje
            i_nom = (kva * 1000) / denom
        else: i_nom = 0.0
        return i_nom, kw_carga, kva

    def _get_ampacidad_real(self, datos_cable):
        if self.tipo_instalacion == TipoInstalacion.DUCTO: return datos_cable["A_DUCTO"]
        elif self.tipo_instalacion == TipoInstalacion.AIRE: return datos_cable["A_AIRE"]
        elif self.tipo_instalacion == TipoInstalacion.AGRUP: return datos_cable["A_AGRUP"]
        return 0

    def ejecutar_seleccion_conductor(self):
        i_nom, _, _ = self.calcular_corriente_carga()
        i_req = i_nom * 1.25
        bd = self._get_bd()
        
        cal_opt = "750"
        for c in ORDEN_CALIBRES:
            dat = bd.get(c)
            if not dat: continue
            amp_real = self._get_ampacidad_real(dat)
            if amp_real >= i_req:
                dv = self._calc_dv(1, dat["R"], dat["X"], i_nom)
                if dv <= self.MAX_CAIDA:
                    cal_opt = c
                    break
        
        u_idx = ORDEN_CALIBRES.index(self.calibre_usuario) if self.calibre_usuario in ORDEN_CALIBRES else -1
        o_idx = ORDEN_CALIBRES.index(cal_opt)
        
        sel_cal = self.calibre_usuario
        nota = "Usuario"
        if u_idx > o_idx: 
            sel_cal = cal_opt
            nota = "Optimizado"
        
        dat_sel = bd.get(sel_cal)
        n = 1
        while n <= 10:
            amp_real = self._get_ampacidad_real(dat_sel)
            if (amp_real * n >= i_req) and (self._calc_dv(n, dat_sel["R"], dat_sel["X"], i_nom) <= self.MAX_CAIDA):
                break
            n += 1
            
        cap_real = self._get_ampacidad_real(dat_sel) * n
        dv_real = self._calc_dv(n, dat_sel["R"], dat_sel["X"], i_nom)
        
        # Evidencia
        prev_n = n
        prev_cal = sel_cal
        if n > 1: prev_n = n - 1 
        else:
            if sel_cal in ORDEN_CALIBRES:
                curr_idx = ORDEN_CALIBRES.index(sel_cal)
                if curr_idx > 0: prev_cal = ORDEN_CALIBRES[curr_idx - 1]
                else: prev_cal = None
            else: prev_cal = None
        
        prev_desc = "N/A (Min)"
        prev_dv, prev_cap = 0.0, 0.0
        
        if prev_cal:
            dat_prev = bd.get(prev_cal)
            if dat_prev:
                prev_dv = self._calc_dv(prev_n, dat_prev["R"], dat_prev["X"], i_nom)
                prev_cap = self._get_ampacidad_real(dat_prev) * prev_n
                prev_desc = f"{prev_n} x {prev_cal}"
                fail_reason = ""
                if prev_cap < i_req: fail_reason = "(I<Ireq)"
                elif prev_dv > self.MAX_CAIDA: fail_reason = "(Reg>3%)"
                if fail_reason: prev_desc += f" {fail_reason}"
        
        self._res_conductor = {
            "Calibre": sel_cal, "N": n, "Mat": self.material_conductor,
            "Capacidad": cap_real, "I_Req": i_req, "I_Nom": i_nom,
            "DV": dv_real, "R_unit": dat_sel["R"], "X_unit": dat_sel["X"], "Nota": nota,
            "Prev_Desc": prev_desc, "Prev_DV": prev_dv, "Prev_Cap": prev_cap,
            "Instalacion": self.tipo_instalacion.value
        }
        return self._res_conductor

    def calcular_perdidas_reales(self):
        if not self._res_conductor: self.ejecutar_seleccion_conductor()
        rc = self._res_conductor
        r_total = (rc["R_unit"] * (self.longitud_mts / 1000.0)) / rc["N"]
        factor_fase = 3 if self.fases == 3 else 2
        return (factor_fase * (rc["I_Nom"]**2) * r_total) / 1000.0

    def _calc_dv(self, n, r, x, i):
        k = math.sqrt(3) if self.fases == 3 else 2
        z = r * self.factor_potencia + x * math.sin(math.acos(self.factor_potencia))
        v_drop = (k * i * (z/1000) * self.longitud_mts) / n
        return (v_drop / self.voltaje) * 100

class Tablero:
    def __init__(self, nombre, voltaje, fases, fd=1.0):
        self.nombre = nombre
        self.voltaje = voltaje
        self.fases = fases
        self.fd = fd
        self.circuitos = []
        self.sub_tableros = []
    def agregar_c(self, c): self.circuitos.append(c)
    def agregar_s(self, t): self.sub_tableros.append(t)

class Transformador:
    def __init__(self, nombre, reserva=0.0):
        self.nombre = nombre
        self.reserva = reserva
        self.tableros = []
