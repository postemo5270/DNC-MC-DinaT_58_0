import pandas as pd
from IPython.display import display, HTML
import backend

def mostrar_reporte_conductores():
    if not backend.MEMORIA_TABLEROS:
        print("⚠️ ALERTA: No hay datos cargados.")
        return

    # Estilos CSS
    estilos = [
        dict(selector="th", props=[("background-color", "#2c3e50"), ("color", "white"), ("text-align", "center"), ("font-size", "10px")]),
        dict(selector="td", props=[("text-align", "center"), ("padding", "4px"), ("font-size", "10px"), ("border-bottom", "1px solid #ddd")])
    ]
    
    # Formatos
    formatos = {
        "P_Input": "{:.1f}", "FP": "{:.2f}", "Eff": "{:.2f}", "kVA": "{:.1f}",
        "I.Nom": "{:.1f}", "I.Dis": "{:.1f}", "I.Prot": "{:.0f}",
        "F.Temp": "{:.2f}", "F.Agrup": "{:.2f}", "L(m)": "{:.1f}",
        "I.Base": "{:.1f}", "I.Corr": "{:.1f}", "Cap.Tot": "{:.1f}",
        "R": "{:.3f}", "X": "{:.3f}", "Z": "{:.3f}",
        "Caída": "{:.2f}", "%Reg": "{:.2f}%"
    }

    display(HTML("<h2>📊 REPORTE MAESTRO DE INGENIERÍA (VARIABLES COMPLETAS)</h2>"))

    for tbt in backend.MEMORIA_TABLEROS:
        data_filas = []
        display(HTML(f"""<div style='background-color: #ecf0f1; padding: 5px; border-left: 5px solid #2980b9; margin-top: 15px;'>
        <h4 style='margin:0'>⚡ {tbt.nombre} ({tbt.voltaje}V - {tbt.fases}F)</h4></div>"""))
        
        if not tbt.circuitos: continue

        for i, c in enumerate(tbt.circuitos, 1):
            res = c.ejecutar_calculo()
            
            # Mapeo EXACTO a MC-ELE-Variables.xlsx
            row = {
                "#": i,
                "Tag": c.tag,
                "Desc": c.descripcion,
                # Entrada
                "P_Input": c.p_input,
                "Ud": c.unidad,
                "FP": c.fp,
                "Eff": c.eff,
                "TipoCarga": c.tipo_carga,
                "L(m)": c.l_m,
                # Calculado Inicial
                "kVA": res["kVA_Calc"],
                "I.Nom": res["I_Nominal"],
                "I.Dis": res["I_Diseno"],
                "I.Prot": res["I_Proteccion"],
                # Entorno y Config
                "T(°C)": c.t_ambiente,
                "Inst": c.tipo_instalacion,
                "Mat": c.mat,
                "Aisl": c.tipo_aislam,
                "T.Cab": c.t_aislamiento_cable,
                # Factores
                "F.Temp": res["F_Temp"],
                "F.Agrup": res["F_Agrup"],
                # Selección Conductor
                "Calibre": res["Calibre_Fase"],
                "#Cond": res["Cant_Cond_Fase"],
                "I.Base": res["I_Base_Tabla"],
                "I.Corr": res["I_Corregida_Unit"],
                "Cap.Tot": res["Capacidad_Total"],
                # Impedancia
                "R": res["Resistencia_AC"],
                "X": res["Reactancia_X"],
                "Z": res["Z_Eficaz"],
                # Resultados Finales
                "Tierra": res["Calibre_Tierra"],
                "Neutro": res["Config_Neutro"],
                "Caída": res["Caida_V"],
                "%Reg": res["Reg_Porc"],
                "Estado": res["Estado_Cumplimiento"]
            }
            data_filas.append(row)

        if data_filas:
            df = pd.DataFrame(data_filas)
            def color_estado(val):
                return f'color: {"green" if val == "OK" else "red"}; font-weight: bold'
            
            styler = df.style.set_table_styles(estilos).format(formatos).applymap(color_estado, subset=['Estado']).hide(axis="index")
            display(styler)
