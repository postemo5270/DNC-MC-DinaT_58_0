import backend
from backend import Circuito, Tablero

def cargar_demo():
    print("🚧 INICIANDO ETL: Carga de Datos Estructurada (ModConds.xlsx)...")
    
    # Limpiamos memoria
    backend.MEMORIA_TABLEROS = []

    # =========================================================================
    # 1. TABLERO PRINCIPAL 1 (TP1)
    # =========================================================================
    tp1 = Tablero("Tablero Principal 1", 480, 3)

    # Carga 11: 100 kW, THHN, Al, BD
    c11 = Circuito(
        tag="Carga 11", descripcion="Carga Principal",
        p_input=100.0, unidad="kW", tension=480, fases=3,
        fp=0.79, eff=0.902, longitud=100.0, 
        mat="AL", tipo_aislam="THHN", t_aislamiento_cable=90,
        tipo_instalacion="BD-Sub", req_neutro="NO"
    )
    tp1.agregar_c(c11)

    # Carga 12: 75 HP, THHN, Al, BD (Nota: 75HP = 55.9kW aprox, pero el sistema calcula)
    c12 = Circuito(
        tag="Carga 12", descripcion="Motor Bomba",
        p_input=75.0, unidad="hp", tension=480, fases=3,
        fp=0.79, eff=0.902, longitud=100.0,
        mat="AL", tipo_aislam="THHN", t_aislamiento_cable=90,
        tipo_instalacion="BD-Sub", req_neutro="NO"
    )
    tp1.agregar_c(c12)

    # Carga 13: 112 kVA, THHN, Al, BD
    c13 = Circuito(
        tag="Carga 13", descripcion="Carga Genérica",
        p_input=112.0, unidad="kVA", tension=480, fases=3,
        fp=0.79, eff=0.902, longitud=100.0,
        mat="AL", tipo_aislam="THHN", t_aislamiento_cable=90,
        tipo_instalacion="BD-Sub", req_neutro="NO"
    )
    tp1.agregar_c(c13)

    # --- SUBTABLERO 1 (TP1) ---
    sub1_tp1 = Tablero("Subtablero 1 (TP1)", 480, 3)
    
    # Carga sub 11
    cs11 = Circuito(
        tag="Carga sub 11", descripcion="Carga Interna Sub",
        p_input=100.0, unidad="kW", tension=480, fases=3,
        fp=0.79, eff=0.902, longitud=100.0,
        mat="AL", tipo_aislam="THHN", t_aislamiento_cable=90,
        tipo_instalacion="BD-Sub", req_neutro="NO"
    )
    sub1_tp1.agregar_c(cs11)
    
    # Vincular Subtablero a Principal
    tp1.agregar_sub(sub1_tp1)


    # =========================================================================
    # 2. TABLERO PRINCIPAL 2 (TP2)
    # =========================================================================
    tp2 = Tablero("Tablero Principal 2", 480, 3)

    # Carga 21
    c21 = Circuito(
        tag="Carga 21", descripcion="Carga P2",
        p_input=100.0, unidad="kW", tension=480, fases=3,
        fp=0.79, eff=0.902, longitud=100.0,
        mat="AL", tipo_aislam="THHN", t_aislamiento_cable=90,
        tipo_instalacion="BD-Sub", req_neutro="NO"
    )
    tp2.agregar_c(c21)

    # --- SUBTABLERO 1 (TP2) ---
    sub1_tp2 = Tablero("Subtablero 21", 480, 3) # Nombre ajustado a ModConds
    
    # Carga sub 21
    cs21 = Circuito(
        tag="Carga sub 21", descripcion="Carga Interna Sub 2",
        p_input=100.0, unidad="kW", tension=480, fases=3,
        fp=0.79, eff=0.902, longitud=100.0,
        mat="AL", tipo_aislam="THHN", t_aislamiento_cable=90,
        tipo_instalacion="BD-Sub", req_neutro="NO"
    )
    sub1_tp2.agregar_c(cs21)
    
    tp2.agregar_sub(sub1_tp2)

    # Cargar a Memoria Global
    backend.MEMORIA_TABLEROS.extend([tp1, sub1_tp1, tp2, sub1_tp2])
    print(f"✅ ETL FINALIZADO: {len(backend.MEMORIA_TABLEROS)} tableros cargados.")
