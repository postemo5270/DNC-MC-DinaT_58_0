import backend
from backend import Circuito, Tablero, TipoInstalacion, TipoOperacion

def cargar_demo():
    print("🚧 INICIANDO ETL: Carga de Datos de Prueba (ModConds.xlsx Mock)...")
    
    # Limpiamos la memoria para evitar duplicados en recargas
    backend.MEMORIA_TABLEROS = []
    
    # =========================================================================
    # 1. INSTANCIACIÓN DE LA TOPOLOGÍA (Nodos)
    # =========================================================================
    
    # Sistema 1
    t_main1 = Tablero("Tablero Principal 1", 480, 3)
    t_sub1_tp1 = Tablero("Subtablero 1 (TP1)", 480, 3)
    t_main1.agregar_sub(t_sub1_tp1)
    
    # Sistema 2
    t_main2 = Tablero("Tablero Principal 2", 480, 3)
    t_sub1_tp2 = Tablero("Subtablero 1 (TP2)", 480, 3)
    t_main2.agregar_sub(t_sub1_tp2)

    # =========================================================================
    # 2. INGESTA DE CARGAS (Hojas)
    # =========================================================================
    
    # --- Cargas Subtablero 1 (TP1) ---
    c_sub11 = Circuito(
        tag="Carga sub 11", descripcion="Motor Subtablero", 
        potencia_nominal_kw=100.0, voltaje=480, fases=3, 
        factor_potencia=0.79, eficiencia=0.902, 
        longitud_mts=100.0, material_conductor="AL", 
        tipo_instalacion=TipoInstalacion.BANCO_DUCTOS,
        temp_ambiente=30
    )
    t_sub1_tp1.agregar_c(c_sub11)

    # --- Cargas Tablero Principal 1 ---
    # Carga 11: 100 kW
    c_11 = Circuito(
        tag="Carga 11", descripcion="Carga Principal", 
        potencia_nominal_kw=100.0, voltaje=480, fases=3, 
        factor_potencia=0.79, eficiencia=0.902, 
        longitud_mts=100.0, material_conductor="AL", 
        tipo_instalacion=TipoInstalacion.BANCO_DUCTOS
    )
    t_main1.agregar_c(c_11)

    # Carga 12: 75 HP -> 55.9 kW
    c_12 = Circuito(
        tag="Carga 12", descripcion="Motor 75HP", 
        potencia_nominal_kw=55.9, voltaje=480, fases=3, 
        factor_potencia=0.79, eficiencia=0.902, 
        longitud_mts=100.0, material_conductor="AL", 
        tipo_instalacion=TipoInstalacion.BANCO_DUCTOS
    )
    t_main1.agregar_c(c_12)

    # Carga 13: 112 kVA -> 88.5 kW
    c_13 = Circuito(
        tag="Carga 13", descripcion="Carga 112kVA", 
        potencia_nominal_kw=88.5, voltaje=480, fases=3, 
        factor_potencia=0.79, eficiencia=0.902, 
        longitud_mts=100.0, material_conductor="AL", 
        tipo_instalacion=TipoInstalacion.BANCO_DUCTOS
    )
    t_main1.agregar_c(c_13)

    # --- ALIMENTADOR DINÁMICO (TP1 -> SUB1) ---
    # Calculamos la carga acumulada del subtablero para dimensionar su alimentador
    kw_sub1 = t_sub1_tp1.total_kw()
    c_alim1 = Circuito(
        tag="ALIM-SUB-TP1", descripcion=f"Alim. {t_sub1_tp1.nombre}", 
        potencia_nominal_kw=kw_sub1, voltaje=480, fases=3, 
        factor_potencia=0.95, longitud_mts=20.0, 
        material_conductor="CU", tipo_instalacion=TipoInstalacion.BANDEJA,
        tipo_operacion=TipoOperacion.CONTINUA
    )
    t_main1.agregar_c(c_alim1)

    # --- Cargas Sistema 2 (TP2 y SUB2) ---
    # (Resumido para brevedad, usando la misma lógica)
    c_sub21 = Circuito("Carga sub 21", "Motor Sub 2", 100.0, 480, 3, 0.79, TipoOperacion.CONTINUA, 100.0, "AL", TipoInstalacion.BANCO_DUCTOS, eficiencia=0.902)
    t_sub1_tp2.agregar_c(c_sub21)
    
    c_21 = Circuito("Carga 21", "Carga P2", 100.0, 480, 3, 0.79, TipoOperacion.CONTINUA, 100.0, "AL", TipoInstalacion.BANCO_DUCTOS, eficiencia=0.902)
    t_main2.agregar_c(c_21)

    # Alimentador Sub 2
    kw_sub2 = t_sub1_tp2.total_kw()
    c_alim2 = Circuito(f"ALIM-SUB-TP2", f"Alim. {t_sub1_tp2.nombre}", kw_sub2, 480, 3, 0.95, TipoOperacion.CONTINUA, 20.0, "CU", TipoInstalacion.BANDEJA)
    t_main2.agregar_c(c_alim2)

    # =========================================================================
    # 3. PUBLICACIÓN EN MEMORIA GLOBAL
    # =========================================================================
    backend.MEMORIA_TABLEROS.extend([t_main1, t_sub1_tp1, t_main2, t_sub1_tp2])
    backend.SISTEMA_PROYECTO = t_main1
    
    print(f"✅ ETL FINALIZADO: {len(backend.MEMORIA_TABLEROS)} tableros cargados y listos para cálculo.")
