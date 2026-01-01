import backend
from backend import Circuito, Tablero, TipoInstalacion, TipoOperacion

def cargar_demo():
    print("🚧 INICIANDO LECTURA DE DATOS (SIMULACIÓN EXCEL)...")
    
    # Limpiar memoria
    backend.MEMORIA_TABLEROS = []
    
    # =========================================================================
    # PASO 1: DEFINIR ESTRUCTURA JERÁRQUICA (BOTTOM-UP)
    # Primero creamos los hijos, luego los padres.
    # =========================================================================
    
    # 1.1 Crear Sub-Tablero (Según tu Excel: "Subtablero 1")
    tbt_sub1 = Tablero("Subtablero 1", 480, 3)
    
    # 1.2 Crear Tablero Principal (Según tu Excel: "Tablero Principal 1")
    tbt_main1 = Tablero("Tablero Principal 1", 480, 3)
    
    # 1.3 Enlace Físico
    # El Main alimenta al Sub.
    tbt_main1.agregar_subtablero(tbt_sub1)
    
    print(f"   -> Estructura creada: [{tbt_main1.nombre}] alimenta a [{tbt_sub1.nombre}]")

    # =========================================================================
    # PASO 2: CARGAR CIRCUITOS DEL EXCEL (SOLO INPUTS)
    # Ignoramos columnas calculadas (I nom, Reg, etc).
    # =========================================================================

    # --- CARGAS DEL SUBTABLERO 1 ---
    # Fila Excel: "Carga sub 11", 100kW, 480V, 100m, FP 0.79, Eff 0.902, AL, BD...
    c_sub_1 = Circuito(
        tag="C-SUB-11", 
        descripcion="Carga sub 11 (Motor)", 
        potencia_nominal_kw=100.0, 
        voltaje=480, 
        fases=3, 
        factor_potencia=0.79, 
        tipo_operacion=TipoOperacion.CONTINUA, 
        longitud_mts=100.0,
        material_conductor="AL", # Viene del Excel
        tipo_instalacion=TipoInstalacion.BANCO_DUCTOS, # "BD" en Excel
        eficiencia=0.902,
        temp_ambiente=30, # Asumido por "Ampacity a 30C"
        factor_agrupamiento=1.0, # Default si no está explicito
        aislamiento="THHN" # Default standard
    )
    tbt_sub1.agregar_c(c_sub_1)
    
    # Ejecutamos cálculo para este circuito
    c_sub_1.ejecutar_seleccion_conductor()
    
    print(f"   -> Carga '{c_sub_1.tag}' agregada a {tbt_sub1.nombre}")


    # --- CARGAS DEL TABLERO PRINCIPAL 1 ---
    # Fila Excel: "Carga 21", 100kW, 480V, 100m, FP 0.79, Eff 0.902...
    c_main_1 = Circuito(
        tag="C-21", 
        descripcion="Carga 21 (Bomba Principal)", 
        potencia_nominal_kw=100.0, 
        voltaje=480, 
        fases=3, 
        factor_potencia=0.79, 
        tipo_operacion=TipoOperacion.CONTINUA, 
        longitud_mts=100.0,
        material_conductor="AL", 
        tipo_instalacion=TipoInstalacion.BANCO_DUCTOS,
        eficiencia=0.902,
        temp_ambiente=30
    )
    tbt_main1.agregar_c(c_main_1)
    c_main_1.ejecutar_seleccion_conductor()
    
    print(f"   -> Carga '{c_main_1.tag}' agregada a {tbt_main1.nombre}")
    
    # =========================================================================
    # PASO 3: ALIMENTADOR DEL SUBTABLERO (AUTOMÁTICO)
    # Creamos una carga en el Principal que representa al Subtablero completo
    # =========================================================================
    carga_sub = tbt_sub1.calcular_carga_total_kw()
    
    c_alimentador = Circuito(
        tag="ALIM-SUB-1",
        descripcion=f"Alimentador para {tbt_sub1.nombre}",
        potencia_nominal_kw=carga_sub, # La suma del subtablero
        voltaje=480,
        fases=3,
        factor_potencia=0.95, # FP global estimado
        tipo_operacion=TipoOperacion.CONTINUA,
        longitud_mts=20.0, # Distancia entre tableros (Asumida o Input futuro)
        material_conductor="CU",
        tipo_instalacion=TipoInstalacion.BANDEJA
    )
    c_alimentador.ejecutar_seleccion_conductor()
    tbt_main1.agregar_c(c_alimentador)
    
    print(f"   -> Generado Alimentador Automático: {c_alimentador.potencia_nominal_kw} kW")

    # --- FINALIZAR ---
    # Guardamos en memoria solo el Principal (que contiene al hijo dentro)
    # O ambos si queremos verlos por separado en el reporte plana
    backend.MEMORIA_TABLEROS.append(tbt_main1)
    backend.MEMORIA_TABLEROS.append(tbt_sub1) 
    
    backend.SISTEMA_PROYECTO = tbt_main1
    
    print("✅ CARGA DE DATOS COMPLETADA.")
