import math

# --- TABLAS NEC Y CONSTANTES ---
# (Se mantienen las tablas 310.16 y 250.122 definidas anteriormente)
TABLA_310_16_CU = { "14": (20, 25), "12": (25, 30), "10": (35, 40), "8": (50, 55), "6": (65, 75), "4": (85, 95), "3": (100, 115), "2": (115, 130), "1": (130, 145), "1/0": (150, 170), "2/0": (175, 195), "3/0": (200, 225), "4/0": (230, 260), "250": (255, 290), "300": (285, 320), "350": (310, 350), "500": (380, 430), "600": (420, 475), "750": (475, 535) }
TABLA_310_16_AL = { "12": (20, 25), "10": (30, 35), "8": (40, 45), "6": (50, 55), "4": (65, 75), "3": (75, 85), "2": (90, 100), "1": (100, 115), "1/0": (120, 135), "2/0": (135, 150), "3/0": (155, 175), "4/0": (180, 205), "250": (205, 230), "300": (230, 255), "350": (250, 280), "500": (310, 350), "600": (340, 385), "750": (385, 435) }
TABLA_250_122 = [ (15, "14", "12"), (20, "12", "10"), (60, "10", "8"), (100, "8", "6"), (200, "6", "4"), (300, "4", "2"), (400, "3", "1"), (500, "2", "1/0"), (600, "1", "2/0"), (800, "1/0", "3/0"), (1000, "2/0", "4/0"), (1200, "3/0", "250"), (1600, "4/0", "350"), (2000, "250", "400"), (2500, "350", "600"), (3000, "400", "600"), (4000, "500", "800"), (5000, "700", "1200"), (6000, "800", "1200") ]
ORDEN_CALIBRES = ["14", "12", "10", "8", "6", "4", "3", "2", "1", "1/0", "2/0", "3/0", "4/0", "250", "300", "350", "500", "600", "750"]
DATOS_FISICOS = { "14": {"r_cu": 10.2, "x_cu": 0.19, "r_al": 16.7, "x_al": 0.19}, "12": {"r_cu": 6.6, "x_cu": 0.18, "r_al": 10.8, "x_al": 0.18}, "10": {"r_cu": 3.9, "x_cu": 0.16, "r_al": 6.4, "x_al": 0.16}, "8": {"r_cu": 2.56, "x_cu": 0.17, "r_al": 4.2, "x_al": 0.17}, "6": {"r_cu": 1.61, "x_cu": 0.16, "r_al": 2.66, "x_al": 0.16}, "4": {"r_cu": 1.02, "x_cu": 0.15, "r_al": 1.67, "x_al": 0.15}, "3": {"r_cu": 0.82, "x_cu": 0.15, "r_al": 1.35, "x_al": 0.15}, "2": {"r_cu": 0.62, "x_cu": 0.14, "r_al": 1.05, "x_al": 0.14}, "1": {"r_cu": 0.51, "x_cu": 0.14, "r_al": 0.82, "x_al": 0.14}, "1/0": {"r_cu": 0.39, "x_cu": 0.13, "r_al": 0.66, "x_al": 0.13}, "2/0": {"r_cu": 0.31, "x_cu": 0.13, "r_al": 0.52, "x_al": 0.13}, "3/0": {"r_cu": 0.25, "x_cu": 0.12, "r_al": 0.43, "x_al": 0.12}, "4/0": {"r_cu": 0.20, "x_cu": 0.12, "r_al": 0.33, "x_al": 0.12}, "250": {"r_cu": 0.17, "x_cu": 0.12, "r_al": 0.28, "x_al": 0.12}, "300": {"r_cu": 0.14, "x_cu": 0.11, "r_al": 0.23, "x_al": 0.11}, "350": {"r_cu": 0.12, "x_cu": 0.11, "r_al": 0.20, "x_al": 0.11}, "500": {"r_cu": 0.089, "x_cu": 0.11, "r_al": 0.14, "x_al": 0.11}, "600": {"r_cu": 0.075, "x_cu": 0.11, "r_al": 0.12, "x_al": 0.11}, "750": {"r_cu": 0.062, "x_cu": 0.11, "r_al": 0.10, "x_al": 0.11} }

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

# --- MEMORIA GLOBAL ---
MEMORIA_TABLEROS = []
SISTEMA_PROYECTO = None

class Circuito:
    def __init__(self, tag, descripcion, potencia_nominal_kw, voltaje, fases, 
                 factor_potencia=0.9, tipo_operacion=TipoOperacion.CONTINUA, 
                 longitud_mts=10.0, calibre_usuario="12", material_conductor="CU",
                 tipo_instalacion=TipoInstalacion.DUCTO,
                 eficiencia=1.0, temp_ambiente=30, factor_agrupamiento=1.0,
                 aislamiento="THHN"):
        
        # Mapeo directo de columnas Excel
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
        self._res_conductor = None

    def calcular_corriente_nominal(self):
        denom = self.voltaje * self.factor_potencia * self.eficiencia
        if self.fases == 3: denom *= math.sqrt(3)
        return (self.potencia_nominal_kw * 1000.0) / denom if denom != 0 else 0.0

    def calcular_corriente_diseno(self):
        inom = self.calcular_corriente_nominal()
        factor = 1.25 if self.tipo_operacion == TipoOperacion.CONTINUA else 1.0
        return inom * factor

    def obtener_tierra(self, amp_proteccion):
        col = 1 if self.material_conductor == "CU" else 2
        for fila in TABLA_250_122:
            if fila[0] >= amp_proteccion: return fila[col]
        return "750"

    def ejecutar_seleccion_conductor(self):
        i_diseno = self.calcular_corriente_diseno()
        
        # Factores
        t = self.temp_ambiente
        f_temp = 1.0
        if 31 <= t <= 35: f_temp = 0.96
        elif 36 <= t <= 40: f_temp = 0.91
        elif 41 <= t <= 45: f_temp = 0.87
        elif 46 <= t <= 50: f_temp = 0.82
        elif 51 <= t <= 80: f_temp = 0.41 # Simplificado
        
        f_total = f_temp * self.factor_agrupamiento
        tabla_amp = TABLA_310_16_CU if self.material_conductor == "CU" else TABLA_310_16_AL
        
        cal_elegido, n_cond, nota = None, 1, ""
        reg_pct, v_caida, amp_real = 0.0, 0.0, 0.0
        
        idx = 0
        encontrado = False
        while not encontrado:
            cal = ORDEN_CALIBRES[idx]
            amp_base = tabla_amp[cal][1] # Columna 90C
            amp_sitio = amp_base * n_cond * f_total
            
            if amp_sitio >= i_diseno:
                # Calculo Caida
                datos = DATOS_FISICOS.get(cal, {"r_cu":0.2})
                r = datos.get(f"r_{self.material_conductor.lower()}", 0.2)
                x = datos.get(f"x_{self.material_conductor.lower()}", 0.1)
                phi = math.acos(self.factor_potencia)
                z_eff = (r * self.factor_potencia) + (x * math.sin(phi))
                
                dv_u = z_eff * i_diseno * (self.longitud_mts / 1000.0)
                v_drop = (math.sqrt(3) * dv_u / n_cond) if self.fases == 3 else (2 * dv_u / n_cond)
                reg = (v_drop / self.voltaje) * 100.0
                
                if reg <= 3.0:
                    cal_elegido, amp_real, v_caida, reg_pct = cal, amp_sitio, v_drop, reg
                    encontrado = True
                else:
                    idx += 1
            else:
                idx += 1
            
            if idx >= len(ORDEN_CALIBRES):
                n_cond += 1; idx = 0
                if n_cond > 4: encontrado = True; nota = "Excede Limite"

        gnd = self.obtener_tierra(i_diseno)
        self._res_conductor = {
            "I_Nominal": self.calcular_corriente_nominal(), "I_Diseno": i_diseno,
            "Calibre": cal_elegido, "N_Hilos": n_cond, "Tierra": gnd,
            "Amp_Real": amp_real, "V_Caida": v_caida, "Reg_Pct": reg_pct,
            "Nota": nota, "Config": f"{n_cond}x{cal_elegido}+{gnd}(GND)"
        }
        return self._res_conductor

class Tablero:
    def __init__(self, nombre, voltaje, fases):
        self.nombre = nombre
        self.voltaje = voltaje
        self.fases = fases
        self.circuitos = []
        self.sub_tableros = []
        self.padre = None

    def agregar_c(self, c): self.circuitos.append(
