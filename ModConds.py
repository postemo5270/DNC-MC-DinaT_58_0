import pandas as pd
from IPython.display import display, HTML
import backend

def mostrar_reporte_conductores():
    """
    Genera tablas HTML estilizadas con los resultados del cálculo.
    Cumple con el patrón de 'Visualización Pasiva': No recalcula, solo muestra.
    """
    if not backend.MEMORIA_TABLEROS:
        print("⚠️ No hay datos cargados en memoria. Ejecuta CargaDatos primero.")
        return

    # Definición de Estilos CSS para el Reporte
    estilos = [
        dict(selector="th", props=[("font-size", "12px"), ("text-align", "center"), 
                                   ("background-color", "#2c3e50"), ("color", "white"),
                                   ("padding", "8px")]),
        dict(selector="td", props=[("font-size", "12px"), ("text-align", "center"),
                                   ("padding", "5px")]),
        dict(selector="tr:hover", props=[("background-color", "#f1f2f6")])
    ]
    
    # Formateo de columnas numéricas
    formatos = {
        "kW": "{:.1f}", "FP": "{:.2f}", "Eff": "{:.2f}", 
        "I.Nom": "{:.1f}", "I.Dis": "{:.1f}", 
        "F.Temp": "{:.2f}", "F.Agrup": "{:.2f}", 
        "Cap.Real": "{:.1f}", "Caída(V)": "{:.2f}", "%Reg": "{:.2f}%"
    }

    display(HTML("<h2>📊 REPORTE DE INGENIERÍA (NEC/NTC 2050)</h2>"))

    # Iteramos sobre cada tablero en la memoria global
    for tbt in backend.MEMORIA_TABLEROS:
        data_tbt = []
        item_counter = 1
        
        # Encabezado del Tablero
        header_html = f"""
        <div style='background-color: #ecf0f1; padding: 10px; border-left: 5px solid #2980b9; margin-top: 20px;'>
            <h3 style='color: #2c3e50; margin: 0;'>⚡ TABLERO: {tbt.nombre}</h3>
            <small>Voltaje: {tbt.voltaje}V | Fases: {tbt.fases} | 
            <b>Carga Total Conectada: {tbt.total_kw():.2f} kW</b></small>
        </div>
        """
        display(HTML(header_html))

        if not tbt.circuitos:
            display(HTML("<div style='padding:10px; color:gray;'><i>Sin circuitos asignados.</i></div>"))
            continue

        for c in tbt.circuitos:
            # 1. Invocamos al backend (Idempotente: si ya calculó, solo trae datos)
            # Ahora el backend nos devuelve los Metadatos exactos que usó.
            try:
                res = c.ejecutar_seleccion_conductor()
            except Exception as e:
                # Manejo básico de errores de visualización
                res = {"Nota": f"ERROR: {str(e)}", "Reg_Pct": 0, "Config": "ERR"}

            # 2. Semáforos Visuales (Lógica de Alerta)
            estado_visual = "✅ OK"
            estilo_estado = "color: green; font-weight: bold;"
            
            if res['Reg_Pct'] > 3.0: 
                estado_visual = "⚠️ >3%"
                estilo_estado = "color: red; font-weight: bold;"
            
            if "CRÍTICO" in res.get('Nota', ''):
                estado_visual = "⛔ FALLA"
                estilo_estado = "color: darkred; font-weight: bold;"

            # 3. Mapeo Directo (Sin lógica de negocio, solo presentación)
            fila = {
                "#": item_counter,
                "Tag": c.tag,
                "Descripción": c.descripcion,
                "kW": c.potencia_nominal_kw,
                "FP": c.factor_potencia,
                "Eff": c.eficiencia,
                "I.Nom": res.get('I_Nominal', 0),
                "I.Dis": res.get('I_Diseno', 0),
                "T(°C)": c.temp_ambiente,
                # Leemos los metadatos del backend, NO recalculamos con funciones locales
                "F.Temp": res.get('Meta_F_Temp', 1.0),
                "F.Agrup": res.get('Meta_F_Agrup', 1.0),
                "Instalación": c.tipo_instalacion,
                "Mat": res.get('Meta_Material', 'CU'),
                "Aisl": c.aislamiento,
                "Tierra": res.get('Tierra', '-'),
                "Configuración": res.get('Config', '?'),
                "Cap.Real": res.get('Amp_Real', 0),
                "L(m)": c.longitud_mts,
                "Caída(V)": res.get('V_Caida', 0),
                "%Reg": res.get('Reg_Pct', 0),
                "Estado": f"<span style='{estilo_estado}'>{estado_visual} {res.get('Nota','')}</span>"
            }
            data_tbt.append(fila)
            item_counter += 1
        
        # Renderizado DataFrame
        if data_tbt:
            df = pd.DataFrame(data_tbt)
            # Aplicamos estilos
            styler = df.style.set_table_styles(estilos).format(formatos).hide(axis="index")
            display(styler)
