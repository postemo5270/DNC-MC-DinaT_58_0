import pandas as pd
from IPython.display import display, Markdown
import backend

# =============================================================================
# MÓDULO DE REPORTE DE CONDUCTORES (REPORTE SECUENCIAL COMPLETO)
# =============================================================================

def mostrar_reporte_conductores():
    # 1. Detectar qué tableros hay en memoria
    # Si usamos CargaDatos, estarán en MEMORIA_TABLEROS. Si fue manual, quizás solo esté SISTEMA_PROYECTO.
    if backend.MEMORIA_TABLEROS:
        lista_tableros = backend.MEMORIA_TABLEROS
    else:
        lista_tableros = [backend.SISTEMA_PROYECTO]
    
    display(Markdown("# 📊 REPORTE CONSOLIDADO DEL PROYECTO"))
    print("=" * 80)
    
    # 2. Bucle: Un reporte por cada tablero encontrado
    for i, tbt in enumerate(lista_tableros):
        # Título del Tablero
        display(Markdown(f"### ⚡ {i+1}. Tablero: {tbt.nombre} ({tbt.voltaje}V)"))
        
        if not tbt.circuitos:
            print("   (⚠️ Este tablero no tiene circuitos registrados)")
            print("_" * 80 + "\n")
            continue

        # Recopilar datos
        datos = []
        for c in tbt.circuitos:
            # Verificar si ya se calculó, si no, calcular ahora
            res = c._res_conductor if c._res_conductor else c.ejecutar_seleccion_conductor()
            
            datos.append({
                "TAG": c.tag,
                "Descripción": c.descripcion,
                "kW": c.potencia_nominal_kw,
                "Instalación": c.tipo_instalacion.value,
                "I_Nom": round(res.get("I_Nom", 0), 1),
                "Calibre": res.get("Calibre", "?"),
                "Hilos": res.get("N", 1), # Corregido: Agregamos Hilos
                "Mat": res.get("Mat", "?"),
                "%Reg": round(res.get("DV", 0), 2),
                "Nota": res.get("Nota", "")
            })

        # Mostrar Tabla
        df = pd.DataFrame(datos)
        cols = ["TAG", "Descripción", "kW", "I_Nom", "Calibre", "Hilos", "Mat", "Instalación", "%Reg", "Nota"]
        
        display(df[cols])
        print("\n" + "_"*80 + "\n") # Línea separadora entre tableros
