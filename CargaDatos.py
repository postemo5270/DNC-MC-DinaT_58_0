import backend
from backend import Circuito, Tablero, TipoInstalacion, TipoOperacion

def cargar_demo():
    print("🚧 CARGANDO DATOS DEL PROYECTO 1... 🚧")
    
    # DEFINICIÓN DE TABLEROS
    tbt1 = Tablero("TBT 1 - PRINCIPAL", 480, 3)
    tbt11 = Tablero("TBT 1.1 - SUBTABLERO", 480, 3); tbt1.agregar_s(tbt11)
    tbt2 = Tablero("TBT 2 - PRINCIPAL", 480, 3)
    tbt21 = Tablero("TBT 2.1 - SUBTABLERO", 480, 3); tbt2.agregar_s(tbt21)

    # --- 2. CREACIÓN DE CARGAS (CON TEMPERATURAS DE PRUEBA) ---
    
    # TBT 1: Probamos Temperaturas Altas
    c1_1 = Circuito(
        tag="tag 11", descripcion="Carga 11 (Amb: 40°C)", # Cambié desc para ver fácil
        potencia_nominal_kw=100.0, voltaje=480, fases=3, factor_potencia=0.85,
        tipo_operacion=TipoOperacion.CONTINUA, longitud_mts=100.0,
        calibre_usuario="1/0", material_conductor="AL", 
        tipo_instalacion=TipoInstalacion.BANCO_DUCTOS,
        eficiencia=0.95,
        temp_ambiente=40.0 # <--- PRUEBA TABLA (Debería dar 0.91)
    )
    
    c1_2 = Circuito(
        tag="tag 12", descripcion="Carga 12 (Amb: 50°C)",
        potencia_nominal_kw=100.0, voltaje=480, fases=3, factor_potencia=0.85,
        tipo_operacion=TipoOperacion.RESPALDO, longitud_mts=100.0,
        calibre_usuario="1/0", material_conductor="AL", 
        tipo_instalacion=TipoInstalacion.BANCO_DUCTOS,
        eficiencia=0.95,
        temp_ambiente=50.0 # <--- PRUEBA TABLA (Debería dar 0.82)
    )
    
    tbt1.agregar_c(c1_1)
    tbt1.agregar_c(c1_2)

    # TBT 1.1: Temperatura Estándar (30°C implícito)
    c11_1 = Circuito(
        tag="tag 111", descripcion="Carga 111 (Amb: 30°C)", 
        potencia_nominal_kw=40.0, voltaje=480, fases=3, factor_potencia=0.9,
        tipo_operacion=TipoOperacion.CONTINUA, longitud_mts=78.0,
        calibre_usuario="2", material_conductor="CU", 
        tipo_instalacion=TipoInstalacion.BANCO_DUCTOS,
        eficiencia=0.95
        # temp_ambiente por defecto es 30.0
    )
    tbt11.agregar_c(c11_1)

    # TBT 2
    c2_1 = Circuito("tag 21", "Carga 21", 75.0, 480, 3, 0.85, TipoOperacion.CONTINUA, 100.0, "1/0", "AL", TipoInstalacion.BANCO_DUCTOS, eficiencia=0.95)
    c2_2 = Circuito("tag 22", "Carga 22", 75.0, 480, 3, 0.85, TipoOperacion.RESPALDO, 100.0, "1/0", "AL", TipoInstalacion.BANCO_DUCTOS, eficiencia=0.95)
    tbt2.agregar_c(c2_1); tbt2.agregar_c(c2_2)

    # TBT 2.1
    c21_1 = Circuito("tag 211", "Carga 211", 150.0, 480, 3, 0.9, TipoOperacion.CONTINUA, 78.0, "2", "CU", TipoInstalacion.BANCO_DUCTOS, eficiencia=0.95)
    tbt21.agregar_c(c21_1)
