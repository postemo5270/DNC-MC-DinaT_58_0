import backend
from backend import Circuito, Tablero, TipoInstalacion, TipoOperacion

def cargar_demo():
    print("🚀 INICIANDO CARGA DE DATOS DEMO...")
    
    # Limpiar memoria
    backend.MEMORIA_TABLEROS = []
    
    # --- 1. CREACIÓN DE ESTRUCTURA ---
    print("   -> Creando Tableros...")
    tbt1 = Tablero("TBT-Petroleo-01", 480, 3)
    tbt11 = Tablero("TBT-Sub-Lighting", 480, 3) # Subtablero
    
    tbt2 = Tablero("TBT-Bombeo-02", 480, 3)
    tbt21 = Tablero("TBT-Sub-Inst", 440, 3)
    
    # --- 2. CREACIÓN DE CARGAS ---
    print("   -> Generando Circuitos (Esto incluye cálculos iterativos)...")

    # TBT 1
    # Carga con temperatura alta (40°C) para probar derateo
    c1_1 = Circuito("M-P1-01", "Bomba Transferencia (Amb 40°C)", 100.0, 480, 3, 0.85, 
                    TipoOperacion.CONTINUA, 100.0, "1/0", "AL", TipoInstalacion.BANCO_DUCTOS,
                    eficiencia=0.95, temp_ambiente=40, factor_agrupamiento=1.0)
    
    # Carga estándar
    c1_2 = Circuito("M-P1-02", "Compresor Aire", 75.0, 480, 3, 0.85, 
                    TipoOperacion.RESPALDO, 50.0, "2", "CU", TipoInstalacion.BANDEJA,
                    eficiencia=0.92, temp_ambiente=30, factor_agrupamiento=1.0)
    
    tbt1.agregar_c(c1_1)
    tbt1.agregar_c(c1_2)
    print(f"      OK: {tbt1.nombre} cargado con {len(tbt1.circuitos)} circuitos.")

    # TBT 1.1 (Subtablero)
    c11_1 = Circuito("L-01", "Iluminación Patio", 20.0, 480, 3, 0.95, 
                     TipoOperacion.CONTINUA, 150.0, "10", "CU", TipoInstalacion.DUCTO,
                     eficiencia=1.0, temp_ambiente=30)
    tbt11.agregar_c(c11_1)
    print(f"      OK: {tbt11.nombre} cargado.")

    # TBT 2
    c2_1 = Circuito("P-Inj-01", "Bomba Inyección", 150.0, 480, 3, 0.88, 
                    TipoOperacion.CONTINUA, 80.0, "4/0", "AL", TipoInstalacion.BANDEJA,
                    eficiencia=0.96)
    tbt2.agregar_c(c2_1)
    print(f"      OK: {tbt2.nombre} cargado.")

    # TBT 2.1
    c21_1 = Circuito("I-Ups", "Sistema UPS", 30.0, 440, 3, 0.9, 
                     TipoOperacion.CONTINUA, 40.0, "6", "CU", TipoInstalacion.DUCTO,
                     eficiencia=0.94)
    tbt21.agregar_c(c21_1)
    print(f"      OK: {tbt21.nombre} cargado.")

    # --- 3. GUARDAR EN MEMORIA ---
    backend.MEMORIA_TABLEROS.extend([tbt1, tbt11, tbt2, tbt21])
    backend.SISTEMA_PROYECTO = tbt1 # Foco por defecto
    
    print("✅ CARGA DE DATOS COMPLETADA EXITOSAMENTE.")
    print(f"📊 Total Tableros en Memoria: {len(backend.MEMORIA_TABLEROS)}")
