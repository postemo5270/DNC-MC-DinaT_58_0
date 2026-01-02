import backend
from backend import Circuito, Tablero, TipoInstalacion, TipoOperacion

def cargar_demo():
    print("🚧 CARGANDO BASE DE DATOS COMPLETA (ModConds.xlsx)...")
    backend.MEMORIA_TABLEROS = []
    
    # =========================================================================
    # 1. DEFINICIÓN DE ESTRUCTURA (JERARQUÍA)
    # =========================================================================
    
    # --- SISTEMA 1 ---
    # Tablero Principal 1
    t_main1 = Tablero("Tablero Principal 1", 480, 3)
    # Subtablero 1 (Asociado a TP1) - Lo renombramos para unicidad
    t_sub1_tp1 = Tablero("Subtablero 1 (TP1)", 480, 3)
    t_main1.agregar_sub(t_sub1_tp1)
    
    # --- SISTEMA 2 ---
    # Tablero Principal 2
    t_main2 = Tablero("Tablero Principal 2", 480, 3)
    # Subtablero 1 (Asociado a TP2)
    t_sub1_tp2 = Tablero("Subtablero 1 (TP2)", 480, 3)
    t_main2.agregar_sub(t_sub1_tp2)

    # =========================================================================
    # 2. CARGAS DEL SISTEMA 1
    # =========================================================================
    
    # --- CARGAS DE SUBTABLERO 1 (TP1) ---
    # Item 1: Carga sub 11 | 100 kW
    c_sub11 = Circuito("Carga sub 11", "Motor Subtablero", 100.0, 480, 3, 0.79, 
                       TipoOperacion.CONTINUA, 100.0, "AL", "BANCO_DUCTOS", 
                       eficiencia=0.902, temp_ambiente=30)
    t_sub1_tp1.agregar_c(c_sub11)
    c_sub11.ejecutar_seleccion_conductor()

    # --- CARGAS DE TABLERO PRINCIPAL 1 ---
    # Item 1: Carga 11 | 100 kW
    c_11 = Circuito("Carga 11", "Carga Principal", 100.0, 480, 3, 0.79, 
                    TipoOperacion.CONTINUA, 100.0, "AL", "BANCO_DUCTOS", 
                    eficiencia=0.902, temp_ambiente=30)
    t_main1.agregar_c(c_11)
    c_11.ejecutar_seleccion_conductor()

    # Item 2: Carga 12 | 75 HP -> 55.9 kW
    c_12 = Circuito("Carga 12", "Motor 75HP", 55.9, 480, 3, 0.79, 
                    TipoOperacion.CONTINUA, 100.0, "AL", "BANCO_DUCTOS", 
                    eficiencia=0.902, temp_ambiente=30)
    t_main1.agregar_c(c_12)
    c_12.ejecutar_seleccion_conductor()

    # Item 3: Carga 13 | 112 kVA (FP 0.79) -> 88.5 kW
    c_13 = Circuito("Carga 13", "Carga 112kVA", 88.5, 480, 3, 0.79, 
                    TipoOperacion.CONTINUA, 100.0, "AL", "BANCO_DUCTOS", 
                    eficiencia=0.902, temp_ambiente=30)
    t_main1.agregar_c(c_13)
    c_13.ejecutar_seleccion_conductor()

    # --- ALIMENTADOR AUTOMÁTICO PARA SUB 1 (TP1) ---
    kw_sub1 = t_sub1_tp1.total_kw()
    c_alim1 = Circuito(f"ALIM-SUB-TP1", f"Alim. {t_sub1_tp1.nombre}", kw_sub1, 480, 3, 0.95, 
                       TipoOperacion.CONTINUA, 20.0, "CU", "BANDEJA")
    t_main1.agregar_c(c_alim1)
    c_alim1.ejecutar_seleccion_conductor()


    # =========================================================================
    # 3. CARGAS DEL SISTEMA 2
    # =========================================================================

    # --- CARGAS DE SUBTABLERO 1 (TP2) ---
    # Item 1: Carga sub 21 | 100 kW
    c_sub21 = Circuito("Carga sub 21", "Motor Subtablero 2", 100.0, 480, 3, 0.79, 
                       TipoOperacion.CONTINUA, 100.0, "AL", "BANCO_DUCTOS", 
                       eficiencia=0.902, temp_ambiente=30)
    t_sub1_tp2.agregar_c(c_sub21)
    c_sub21.ejecutar_seleccion_conductor()

    # --- CARGAS DE TABLERO PRINCIPAL 2 ---
    # Item 1: Carga 21 | 100 kW
    c_21 = Circuito("Carga 21", "Carga Principal 2", 100.0, 480, 3, 0.79, 
                    TipoOperacion.CONTINUA, 100.0, "AL", "BANCO_DUCTOS", 
                    eficiencia=0.902, temp_ambiente=30)
    t_main2.agregar_c(c_21)
    c_21.ejecutar_seleccion_conductor()

    # Item 2: Carga 22 | 75 HP -> 55.9 kW
    c_22 = Circuito("Carga 22", "Motor 75HP (TP2)", 55.9, 480, 3, 0.79, 
                    TipoOperacion.CONTINUA, 100.0, "AL", "BANCO_DUCTOS", 
                    eficiencia=0.902, temp_ambiente=30)
    t_main2.agregar_c(c_22)
    c_22.ejecutar_seleccion_conductor()

    # Item 3: Carga 23 | 112 kVA -> 88.5 kW
    c_23 = Circuito("Carga 23", "Carga 112kVA (TP2)", 88.5, 480, 3, 0.79, 
                    TipoOperacion.CONTINUA, 100.0, "AL", "BANCO_DUCTOS", 
                    eficiencia=0.902, temp_ambiente=30)
    t_main2.agregar_c(c_23)
    c_23.ejecutar_seleccion_conductor()

    # --- ALIMENTADOR AUTOMÁTICO PARA SUB 1 (TP2) ---
    kw_sub2 = t_sub1_tp2.total_kw()
    c_alim2 = Circuito(f"ALIM-SUB-TP2", f"Alim. {t_sub1_tp2.nombre}", kw_sub2, 480, 3, 0.95, 
                       TipoOperacion.CONTINUA, 20.0, "CU", "BANDEJA")
    t_main2.agregar_c(c_alim2)
    c_alim2.ejecutar_seleccion_conductor()

    # =========================================================================
    # 4. FINALIZAR
    # =========================================================================
    backend.MEMORIA_TABLEROS.extend([t_main1, t_sub1_tp1, t_main2, t_sub1_tp2])
    backend.SISTEMA_PROYECTO = t_main1
    
    print(f"✅ BASE DE DATOS IMPORTADA COMPLETAMENTE.")
    print(f"   📊 Estructura cargada: 4 Tableros, {len(backend.MEMORIA_TABLEROS)} objetos en memoria.")
