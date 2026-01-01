import pandas as pd
from IPython.display import display, HTML
import backend

def obtener_factor_temp(t):
    # Misma lógica del backend para mostrar en el reporte
    if 26 <= t <= 30: return 1.0
    elif 31 <= t <= 35: return 0.96
    elif 36 <= t <= 40: return 0.91
    elif 41 <= t <= 45: return 0.87
    elif 46 <= t <= 50: return 0.82
    elif 51 <= t <= 55: return 0.76
    elif 56 <= t <= 60: return 0.71
    elif 61 <= t <= 70: return 0.58
    elif 71 <= t <= 80: return 0.41
    return 1.0

def generar_dataframe():
    data = []
    item_counter = 1

    for tbt in backend.MEMORIA_TABLEROS:
        # Encabezado de Tablero (Fila vacía o separador si se quiere, aquí lo repetimos por fila)
        for c in tbt.circuitos:
            # Asegurar que haya cálculo
            if not c._res_conductor:
                c.ejecutar_seleccion_conductor()
            
            res = c._res_conductor
            
            # Calcular F.Temp para mostrarlo
            f_temp = obtener_factor_temp(c.temp_ambiente)
            
            # Estado
            estado = "✅ OK"
            if res['Reg_Pct'] > 3.0: estado = "⚠️ Reg > 3%"
            if res['Nota']: estado += f" ({res['Nota']})"

            fila = {
                "TABLERO": tbt.nombre,
                "ITEM": item_counter,
                "TAG": c.tag,
                "DESCRIPCIÓN": c.descripcion,
                "POT (kW)": c.potencia_nominal_kw,
                "V (Sys)": c.voltaje,
                "FASES": c.fases,
                "F.P.": c.factor_potencia,
                "EFF (η)": c.eficiencia,
                "I.NOM (A)": res['I_Nominal'],
                "I.DIS (A)": res['I_Diseno'],
                "T.AMB (°C)": c.temp_ambiente,
                "F.TEMP": f_temp,
                "F.AGRUP": c.factor_agrupamiento,
                "INSTALACIÓN": c.tipo_instalacion,
                "MAT": c.material_conductor,
                "AISL": c.aislamiento,
                "TIERRA (GND)": res['Tierra'],
                "CALIBRE (Fase)": res['Calibre'],
                "HILOS": res['N_Hilos'],
                "CAP. REAL (A)": res['Amp_Real'],
                "LONG (m)": c.longitud_mts,
                "CAÍDA (V)": res['V_Caida'],
                "% REG": res['Reg_Pct'],
                "ESTADO": estado
            }
            data.append(fila)
            item_counter += 1
            
    return pd.DataFrame(data)

def mostrar_reporte_conductores():
    if not backend.MEMORIA_TABLEROS:
        print("⚠️ No hay datos cargados. Ejecuta CargaDatos.cargar_demo() primero.")
        return

    df = generar_dataframe()
    
    # Estilos CSS para que se parezca a Excel
    estilos = [
        dict(selector="th", props=[("font-size", "11px"), ("text-align", "center"), ("background-color", "#2c3e50"), ("color", "white")]),
        dict(selector="td", props=[("font-size", "11px"), ("text-align", "center")]),
        dict(selector="tr:hover", props=[("background-color", "#ffff99")])
    ]
    
    # Formateo de columnas
    formatos = {
        "POT (kW)": "{:.1f}",
        "F.P.": "{:.2f}",
        "EFF (η)": "{:.2f}",
        "I.NOM (A)": "{:.1f}",
        "I.DIS (A)": "{:.1f}",
        "F.TEMP": "{:.2f}",
        "F.AGRUP": "{:.2f}",
        "CAP. REAL (A)": "{:.1f}",
        "CAÍDA (V)": "{:.2f}",
        "% REG": "{:.2f}%"
    }

    display(HTML("<h3>📊 REPORTE DE CÁLCULO DE CONDUCTORES (NEC)</h3>"))
    display(df.style.set_table_styles(estilos).format(formatos).hide(axis="index"))
