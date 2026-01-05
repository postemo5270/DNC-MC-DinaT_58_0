import backend
from backend import Circuito, Tablero

def cargar_demo():
    print("🚧 INICIANDO CARGA SIMPLIFICADA (Solo 2 Cargas)...")
    
    # 1. Limpiamos memoria para evitar duplicados
    backend.MEMORIA_TABLEROS = []

    # =========================================================================
    # TABLERO PRINCIPAL (TP1)
    # =========================================================================
    tp1 = Tablero("Tablero Principal 1", 480, 3)

    # --- Carga 01: Motor 50 HP ---
    c1 = Circuito(
        tag="M-101", descripcion="Bomba Principal",
        p_input=50.0, unidad="hp", tension=480, fases=3,
        fp=0.85, eff=0.92, longitud=80.0,
        mat="CU", tipo_aislam="THHN", t_aislamiento_cable=75,
        tipo_instalacion="Bandeja", req_neutro="NO"
    )
    tp1.agregar_c(c1)

    # --- Carga 02: Carga Genérica 10 kW ---
    c2 = Circuito(
        tag="C-102", descripcion="Servicios Auxiliares",
        p_input=10.0, unidad="kW", tension=480, fases=3,
        fp=0.95, eff=1.0, longitud=40.0,
        mat="AL", tipo_aislam="THHN", t_aislamiento_cable=75,
        tipo_instalacion="Ducto", req_neutro="SI"
    )
    tp1.agregar_c(c2)

    # =========================================================================
    # CARGAR A MEMORIA
    # =========================================================================
    # Agregamos solo el tablero principal (que ya contiene las dos cargas dentro)
    backend.MEMORIA_TABLEROS.append(tp1)
    
    print(f"✅ CARGA FINALIZADA: 1 Tablero con 2 Cargas cargado en memoria.")

# Si necesitas ejecutarlo directamente para probar:
if __name__ == "__main__":
    cargar_demo()
