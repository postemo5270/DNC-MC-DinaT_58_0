import pandas as pd
from IPython.display import display, Markdown
import backend

def mostrar_reporte_conductores():
    # 1. Verificar si hay datos
    tablero = backend.SISTEMA_PROYECTO
    if not tablero.circuitos:
        print("⚠️ No hay circuitos ingresados en la memoria.")
        print("   Por favor, ejecuta primero 'IngCargas' y agrega circuitos.")
        return

    print(f"📊 GENERANDO REPORTE DE CONDUCTORES PARA: {tablero.nombre}")
    print("="*60)

    # 2. Recopilar resultados
    datos_reporte = []
    
    for c in tablero.circuitos:
        # Ejecutamos el cálculo matemático del backend
        res = c.ejecutar_seleccion_conductor()
        
        # Preparamos la fila para la tabla
        fila = {
            "TAG": c.tag,
            "Descripción": c.descripcion,
            "Potencia (kW)": c.potencia_nominal_kw,
            "I_Nom (A)": round(res["I_Nom"], 1),
            "I_Req (A)": round(res["I_Req"], 1),
            "Calibre": res["Calibre"],
            "Hilos": res["N"],
            "Capacidad Real": round(res["Capacidad"], 1),
            "% Reg": round(res["DV"], 2),
            "Material": res["Mat"],
            "Nota": res["Nota"]
        }
        datos_reporte.append(fila)

    # 3. Mostrar Tabla Bonita con Pandas
    df = pd.DataFrame(datos_reporte)
    
    # Reordenar columnas para mejor lectura
    cols = ["TAG", "Descripción", "Potencia (kW)", "I_Nom (A)", "Calibre", "Hilos", "Material", "% Reg", "Nota"]
    
    # Mostrar en pantalla
    display(Markdown("### 📋 Tabla de Selección de Conductores"))
    display(df[cols])
    
    print("\n✅ Cálculo finalizado.")
