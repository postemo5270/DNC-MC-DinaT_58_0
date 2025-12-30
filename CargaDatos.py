import backend
from backend import Circuito, Tablero, TipoInstalacion, TipoOperacion

def cargar_demo():
    print("🚧 CARGANDO DATOS DEL PROYECTO 1... 🚧")
    
    # DEFINICIÓN DE TABLEROS
    tbt1 = Tablero("TBT 1 - PRINCIPAL", 480, 3)
    tbt11 = Tablero("TBT 1.1 - SUBTABLERO", 480, 3); tbt1.agregar_s(tbt11)
    tbt2 = Tablero("TBT 2 - PRINCIPAL", 480, 3)
    tbt21 = Tablero("TBT 2.1 - SUBTABLERO", 480, 3); tbt2.agregar_s(tbt21)

    # CREACIÓN DE CARGAS (Agregamos eficiencia=0.95 aprox)
    # TBT 1
    c1_1 = Circuito("tag 11", "Carga 11", 100.0, 480, 3, 0.85, TipoOperacion.CONTINUA, 100.0, "1/0", "AL", TipoInstalacion.BANCO_DUCTOS, eficiencia=0.95)
    c1_2 = Circuito("tag 12", "Carga 12", 100.0, 480, 3, 0.85, TipoOperacion.RESPALDO, 100.0, "1/0", "AL", TipoInstalacion.BANCO_DUCTOS, eficiencia=0.95)
    tbt1.agregar_c(c1_1); tbt1.agregar_c(c1_2)

    # TBT 1.1
    c11_1 = Circuito("tag 111", "Carga 111", 40.0, 480, 3, 0.9, TipoOperacion.CONTINUA, 78.0, "2", "CU", TipoInstalacion.BANCO_DUCTOS, eficiencia=0.95)
    tbt11.agregar_c(c11_1)

    # TBT 2
    c2_1 = Circuito("tag 21", "Carga 21", 75.0, 480, 3, 0.85, TipoOperacion.CONTINUA, 100.0, "1/0", "AL", TipoInstalacion.BANCO_DUCTOS, eficiencia=0.95)
    c2_2 = Circuito("tag 22", "Carga 22", 75.0, 480, 3, 0.85, TipoOperacion.RESPALDO, 100.0, "1/0", "AL", TipoInstalacion.BANCO_DUCTOS, eficiencia=0.95)
    tbt2.agregar_c(c2_1); tbt2.agregar_c(c2_2)

    # TBT 2.1
    c21_1 = Circuito("tag 211", "Carga 211", 150.0, 480, 3, 0.9, TipoOperacion.CONTINUA, 78.0, "2", "CU", TipoInstalacion.BANCO_DUCTOS, eficiencia=0.95)
    tbt21.agregar_c(c21_1)

    # MEMORIA GLOBAL
    backend.MEMORIA_TABLEROS = [tbt1, tbt11, tbt2, tbt21]
    backend.SISTEMA_PROYECTO = tbt1 
    print("✅ Datos cargados correctamente.")
