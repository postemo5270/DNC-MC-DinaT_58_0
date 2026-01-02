import pandas as pd
from IPython.display import display, HTML
import backend

def mostrar_reporte_conductores():
    if not backend.MEMORIA_TABLEROS:
        print("⚠️ Ejecute CargaDatos primero.")
        return

    estilos = [
        dict(selector="th", props=[("background-color", "#2c3e50"), ("color", "white"), ("text-align", "center")]),
        dict(selector="td", props=[("text-align", "center"), ("padding", "5px")])
    ]
    
    formatos = {
        "P_Input": "{:.1f}", "I.Nom": "{:.1f}", "I.Dis": "{:.1f}", "Breaker": "{:.0f}",
        "Cap.Total": "{:.1f}", "Caída(V)": "{:.2f}", "%Reg": "{:.2f}%"
    }

    for tbt in backend.MEMORIA_TABLEROS:
        data = []
        
        display(HTML(f"<h3>⚡ TABLERO: {tbt.nombre}</h3>"))
        
        if not tbt.circuitos:
            continue

        for c in tbt.circuitos:
            # Ejecutar cálculo (Idempotente)
            res = c.ejecutar_calculo()
            
            row = {
                "Tag": c.tag,
                "P_Input": c.p_input,
                "Unidad": c.unidad,
                "I.Nom": res["I_Nominal"],
                "I.Dis": res["I_Diseno"],
                "Breaker": res["I_Proteccion"],
                "Fases": res["Config_Fase"], # Ej: 2x4/0
                "Neutro": res["Config_Neutro"],
                "Tierra": res["Calibre_Tierra"],
                "Cap.Total": res["Capacidad_Total"],
                "Caída(V)": res["Caida_V"],
                "%Reg": res["Reg_Porc"],
                "Estado": res["Estado_Cumplimiento"]
            }
            data.append(row)

        if data:
            df = pd.DataFrame(data)
            # Colorear estado
            def color_estado(val):
                color = 'green' if val == 'OK' else 'red'
                return f'color: {color}; font-weight: bold'
            
            styler = df.style.set_table_styles(estilos).format(formatos).applymap(color_estado, subset=['Estado'])
            display(styler)
