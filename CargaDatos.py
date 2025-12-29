import backend
from backend import Circuito, Tablero, TipoInstalacion, TipoOperacion

# =============================================================================
# CARGA DE DATOS ESPECÍFICA (PROYECTO 1 - DEFINIDO POR USUARIO)
# =============================================================================

def cargar_demo():
    print("🚧 CARGANDO DATOS DEL PROYECTO 1... 🚧")
    
    # --- 1. DEFINICIÓN DE TABLEROS ---
    # RAMA 1
    tbt1 = Tablero("TBT 1 - PRINCIPAL", 480, 3)
    tbt11 = Tablero("TBT 1.1 - SUBTABLERO", 480, 3)
    tbt1.agregar_s(tbt11) # Enlace
    
    # RAMA 2 (Estructura espejo)
    tbt2 = Tablero("TBT 2 - PRINCIPAL", 480, 3)
    tbt21 = Tablero("TBT 2.1 - SUBTABLERO", 480, 3)
    tbt2.agregar_s(tbt21) # Enlace

    # --- 2. CREACIÓN DE CARGAS RAMA 1 ---
    
    # Cargas TBT 1 (2 cargas de 100kW, Aluminio, Banco)
    c1_1 = Circuito(
        tag="tag 11", descripcion="Carga 11", potencia_nominal_kw=100.0,
        voltaje=480, fases=3, factor_potencia=0.85,
        tipo_operacion=TipoOperacion.CONTINUA, longitud_mts=100.0,
        calibre_usuario="1/0", material_conductor="AL", 
        tipo_instalacion=TipoInstalacion.BANCO_DUCTOS
    )
    
    c1_2 = Circuito(
        tag="tag 12", descripcion="Carga 12", potencia_nominal_kw=100.0,
        voltaje=480, fases=3, factor_potencia=0.85,
        tipo_operacion=TipoOperacion.RESPALDO, longitud_mts=100.0,
        calibre_usuario="1/0", material_conductor="AL", 
        tipo_instalacion=TipoInstalacion.BANCO_DUCTOS
    )
    
    tbt1.agregar_c(c1_1)
    tbt1.agregar_c(c1_2)

    # Cargas TBT 1.1 (1 carga de 40kW, Cobre, Banco)
    c11_1 = Circuito(
        tag="tag 111", descripcion="Carga 111", potencia_nominal_kw=40.0,
        voltaje=480, fases=3, factor_potencia=0.9,
        tipo_operacion=TipoOperacion.CONTINUA, longitud_mts=78.0,
        calibre_usuario="2", material_conductor="CU", 
        tipo_instalacion=TipoInstalacion.BANCO_DUCTOS
    )
    tbt11.agregar_c(c11_1)

    # --- 3. CREACIÓN DE CARGAS RAMA 2 (Cambio de Potencias) ---
    
    # Cargas TBT 2 (Igual a TBT 1 pero 75kW)
    c2_1 = Circuito(
        tag="tag 21", descripcion="Carga 21", potencia_nominal_kw=75.0, # <--- Cambio
        voltaje=480, fases=3, factor_potencia=0.85,
        tipo_operacion=TipoOperacion.CONTINUA, longitud_mts=100.0,
        calibre_usuario="1/0", material_conductor="AL", 
        tipo_instalacion=TipoInstalacion.BANCO_DUCTOS
    )
    
    c2_2 = Circuito(
        tag="tag 22", descripcion="Carga 22", potencia_nominal_kw=75.0, # <--- Cambio
        voltaje=480, fases=3, factor_potencia=0.85,
        tipo_operacion=TipoOperacion.RESPALDO, longitud_mts=100.0,
        calibre_usuario="1/0", material_conductor="AL", 
        tipo_instalacion=TipoInstalacion.BANCO_DUCTOS
    )
    
    tbt2.agregar_c(c2_1)
    tbt2.agregar_c(c2_2)

    # Cargas TBT 2.1 (Igual a TBT 1.1 pero 150kW)
    c21_1 = Circuito(
        tag="tag 211", descripcion="Carga 211", potencia_nominal_kw=150.0, # <--- Cambio fuerte
        voltaje=480, fases=3, factor_potencia=0.9,
        tipo_operacion=TipoOperacion.CONTINUA, longitud_mts=78.0,
        calibre_usuario="2", material_conductor="CU", 
        tipo_instalacion=TipoInstalacion.BANCO_DUCTOS
    )
    tbt21.agregar_c(c21_1)

    # --- 4. EXPORTAR A MEMORIA GLOBAL ---
    # Listamos los 4 para que ModConds y ModTrafo los muestren todos
    backend.MEMORIA_TABLEROS = [tbt1, tbt11, tbt2, tbt21]
    
    # Establecemos TBT 1 como foco inicial por defecto
    backend.SISTEMA_PROYECTO = tbt1 
    
    print(f"✅ Datos cargados correctamente.")
    print(f"   - TBT 1: 2 Cargas (100kW c/u)")
    print(f"   - TBT 1.1: 1 Carga (40kW)")
    print(f"   - TBT 2: 2 Cargas (75kW c/u)")
    print(f"   - TBT 2.1: 1 Carga (150kW)")
