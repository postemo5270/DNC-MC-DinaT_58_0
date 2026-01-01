import pandas as pd
from IPython.display import display, HTML
import backend

def obtener_factor_temp(t):
    if 26 <= t <= 30: return 1.0
    elif 31 <= t <= 35: return 0.96
    elif 36 <= t <= 40: return 0.91
    elif 41 <= t <= 45: return 0.87
    elif 46 <= t <= 50: return 0.82
    elif 51 <= t <= 60: return 0.71
    elif t > 60: return 0.41
    return 1.0

def mostrar_reporte_conductores():
    if not backend.MEMORIA_TABLEROS:
        print("⚠️ No hay datos cargados en memoria. Ejecuta CargaDatos primero.")
        return

    # Estilos CSS (Similar a Excel)
    estilos = [
        dict(selector="th", props=[("font-size", "11px"), ("text-align", "center"), ("background-color", "#2c3e50"), ("color", "white")]),
        dict(selector="td", props=[("font-size", "11px"), ("text-align", "center")]),
        dict(selector="tr:hover", props=[("background-color", "#ffff99")])
    ]
    
    # Formatos de número
    formatos = {
        "kW": "{:.1f}", "FP": "{:.2f}", "Eff": "{:.2f}", 
        "I.Nom": "{:.1f}", "I.Dis": "{:.1f}", 
        "F.Temp": "{:.2f}", "F.Agrup": "{:.2f}", 
        "Cap.Real": "{:.1f}", "Caída(V)": "{:.2f}", "%Reg": "{:.2f}%"
    }

    display(HTML("<h2>📊 REPORTE DE CÁLCULO (NEC) - DETALLE POR TABLERO</h2>"))

    # BUCLE PRINCIPAL: TABLERO POR TABLERO
    for tbt in backend.MEMORIA_TABLEROS:
        data_tbt = []
        item_counter = 1
        
        # Título del Tablero (Separador Visual)
        display(HTML(f"<br><hr><h3 style='color:darkblue; margin-bottom:5px'>⚡ TABLERO: {tbt.nombre}</h3>"))
        display(HTML(f"<i>Voltaje: {tbt.voltaje}V | Fases: {tbt.fases} | Carga Total: {tbt.total_kw():.1f} kW</i>"))

        if not tbt.circuitos:
            display(HTML("<span style='color:gray'>Sin cargas registradas.</span>"))
            continue

        for c in tbt.circuitos:
            # Asegurar cálculo actualizado
            if not c._res_conductor: c.ejecutar_seleccion_conductor()
            res = c._res_conductor
            
            f_temp = obtener_factor_temp(c.temp_ambiente)
            
            # Estado Alerta
            estado = "OK"
            if res['Reg_Pct'] > 3.0: estado = "⚠️ >3%"
            if res['Nota']: estado += f" {res['Nota']}"

            fila = {
                "Item": item_counter,
                "Tag": c.tag,
                "Descripción": c.descripcion,
                "kW": c.potencia_nominal_kw,
                "FP": c.factor_potencia,
                "Eff": c.eficiencia,
                "I.Nom": res['I_Nominal'],
                "I.Dis": res['I_Diseno'],
                "T(°C)": c.temp_ambiente,
                "F.Temp": f_temp,
                "F.Agrup": c.factor_agrupamiento,
                "Instalación": c.tipo_instalacion,
                "Mat": c.material_conductor,
                "Aisl": c.aislamiento,
                "Tierra": res['Tierra'],
                "Fase (Config)": res['Config'].split('+')[0], # Solo parte fase
                "Cap.Real": res['Amp_Real'],
                "L(m)": c.longitud_mts,
                "Caída(V)": res['V_Caida'],
                "%Reg": res['Reg_Pct'],
                "Estado": estado
            }
            data_tbt.append(fila)
            item_counter += 1
        
        # Crear DataFrame de ESTE tablero
        df = pd.DataFrame(data_tbt)
        display(df.style.set_table_styles(estilos).format(formatos).hide(axis="index"))
