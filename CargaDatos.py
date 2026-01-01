import backend
from backend import Circuito, Tablero, TipoInstalacion, TipoOperacion

def cargar_demo():
    print("🚧 CARGANDO DATOS EXACTOS DE 'ModConds.xlsx'...")
    backend.MEMORIA_TABLEROS = []
    
    # 1. ESTRUCTURA (Jerarquía)
    t_main = Tablero("Tablero Principal 1", 480, 3)
    t_sub = Tablero("Subtablero 1", 480, 3)
    
    # Enlace: Main alimenta a Sub
    t_main.agregar_sub(t_sub)

    # 2. CARGAS DEL SUBTABLERO (Datos del Excel)
    c_sub_11 = Circuito(
        tag="Carga sub 11",
        descripcion="Motor Subtablero (Excel)",
        potencia_nominal_kw=100.0,
        voltaje=480,
        fases=3,
        factor_potencia=0.79,      # Dato específico Excel
        eficiencia=0.9024,         # Dato específico Excel
        longitud_mts=100.0,
        material_conductor="AL",   # Dato específico Excel
        tipo_instalacion=TipoInstalacion.BANCO_DUCTOS, # Dato específico Excel
        temp_ambiente=30,
        tipo_operacion=TipoOperacion.CONTINUA
    )
    t_sub.agregar_c(c_sub_11)
    
    # Calcular
    c_sub_11.ejecutar_seleccion_conductor()

    # 3. CARGAS DEL PRINCIPAL (Datos del Excel)
    c_21 = Circuito(
        tag="Carga 21",
        descripcion="Carga Principal (Excel)",
        potencia_nominal_kw=100.0,
        voltaje=480,
        fases=3,
        factor_potencia=0.79,
        eficiencia=0.9024,
        longitud_mts=100.0,
        material_conductor="AL",
        tipo_instalacion=TipoInstalacion.BANCO_DUCTOS,
        temp_ambiente=30,
        tipo_operacion=TipoOperacion.CONTINUA
    )
    t_main.agregar_c(c_21)
    
    # Calcular
    c_21.ejecutar_seleccion_conductor()

    # 4. CARGA ALIMENTADOR (Calculada Automáticamente)
    kw_sub = t_sub.total_kw()
    c_alim = Circuito(
        tag="ALIM-SUB-1",
        descripcion=f"Alimentador {t_sub.nombre}",
        potencia_nominal_kw=kw_sub,
        voltaje=480,
        fases=3,
        factor_potencia=0.95, 
        longitud_mts=20.0,
        material_conductor="CU",
        tipo_instalacion=TipoInstalacion.BANDEJA
    )
    t_main.agregar_c(c_alim)
    c_alim.ejecutar_seleccion_conductor()

    # Guardar en memoria para reporte
    backend.MEMORIA_TABLEROS.extend([t_main, t_sub])
    backend.SISTEMA_PROYECTO = t_main
    
    print(f"✅ Datos cargados correctamente.")
    print(f"   -> {t_sub.nombre}: {len(t_sub.circuitos)} circuitos")
    print(f"   -> {t_main.nombre}: {len(t_main.circuitos)} circuitos")
