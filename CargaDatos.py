import backend
from backend import Circuito, Tablero, TipoInstalacion, TipoOperacion

def cargar_demo():
    print("🚧 CARGANDO DATOS AUTOMÁTICOS... 🚧")
    
    # 1. Crear Jerarquía
    t1 = Tablero("TBT-1-PRINCIPAL", 480, 3)
    t11 = Tablero("TBT-11-SUB", 480, 3); t1.agregar_s(t11)
    
    t2 = Tablero("TBT-2-SECUNDARIO", 440, 3)
    t21 = Tablero("TBT-21-SUB", 220, 3); t2.agregar_s(t21)

    # 2. Función auxiliar de llenado
    def add_loads(tbt, lista):
        for tag, desc, kw, inst in lista:
            tipo = TipoInstalacion.BANDEJA if inst == "BANDEJA" else TipoInstalacion.DUCTO
            c = Circuito(tag, desc, kw, tbt.voltaje, 3, 0.9, TipoOperacion.CONTINUA, 50, "12", "CU", tipo)
            tbt.agregar_c(c); c.ejecutar_seleccion_conductor()

    # 3. Llenar Cargas
    add_loads(t1, [("BOMBA-1", "Agua", 45, "DUCTO"), ("EXTRUSORA", "Principal", 110, "BANDEJA")])
    add_loads(t11, [("PC-SALA", "Computo", 5, "DUCTO"), ("UPS", "Respaldo", 15, "BANDEJA")])
    add_loads(t2, [("MOLINO", "Trituradora", 75, "DUCTO"), ("HORNO", "Secado", 150, "BANDEJA")])
    add_loads(t21, [("ILUM", "Luces", 6, "DUCTO"), ("CCTV", "Cámaras", 2, "DUCTO")])

    # 4. EXPORTAR A MEMORIA GLOBAL (CRUCIAL)
    backend.MEMORIA_TABLEROS = [t1, t11, t2, t21]
    backend.SISTEMA_PROYECTO = t1 # Focus inicial
    print("✅ ¡4 Tableros cargados y listos para ModTrafo!")
