import pandas as pd
import backend
from IPython.display import display, HTML

def generar_reporte():
    """
    Genera la Memoria de Cálculo detallada con TODOS los parámetros técnicos.
    """
    # 1. Validación de seguridad
    if not backend.MEMORIA_TABLEROS:
        print("⚠️ No hay datos en memoria. Por favor ejecuta IngCargas primero.")
        return

    t = backend.MEMORIA_TABLEROS[0]
    
    # Encabezado del Reporte
    display(HTML(f"""
    <div style='background-color:#2c3e50; color:white; padding:10px; border-radius:5px 5px 0 0'>
        <h3 style='margin:0'>📊 MEMORIA DE CÁLCULO: {t.nombre.upper()}</h3>
        <small>Voltaje: {t.voltaje}V | Fases: {t.fases} | Frecuencia: 60Hz</small>
    </div>
    """))

    # 2. Extracción Rigurosa de Datos (Todos los campos)
    datos_filas = []
    
    suma_kw_inst = 0.0
    suma_kva_total = 0.0
    
    for i, c in enumerate(t.circuitos, 1):
        r = c.res # Resultados del cálculo del backend
        
        # Recopilación de TODOS los atributos técnicos
        fila = {
            # --- IDENTIFICACIÓN ---
            "Item": i,
            "Tag": c.tag,
            "Descripción": c.descripcion,
            
            # --- DATOS DE ENTRADA (POTENCIA) ---
            "Pot. Input": f"{c.p_input} {c.unidad}",
            "F.P.": c.fp,
            "Eff": c.eff,
            "kVA Calc": round(r.get('kVA_Calc', 0), 2),
            
            # --- CORRIENTE Y PROTECCIÓN ---
            "I.Nom (A)": round(r.get('I_Nominal', 0), 2),
            "I.Diseño (A)": round(r.get('I_Diseno', 0), 2),
            "Breaker (A)": r.get('I_Proteccion', 0),
            
            # --- CABLEADO (RESULTADOS) ---
            "Conductor Fase": r.get('Config_Fase', 'ERR'),
            "Neutro": r.get('Config_Neutro', 'N/A'),
            "Tierra": r.get('Calibre_Tierra', '-'),
            
            # --- PARÁMETROS FÍSICOS Y DE INSTALACIÓN ---
            "Long (m)": c.l_m,
            "Instalación": c.tipo_instalacion,
            "Material": c.mat,       # CU / AL
            "Aisl.": c.tipo_aislam,  # THHN, etc.
            "T.Amb": f"{c.t_ambiente}°C",
            
            # --- VALIDACIÓN NORMATIVA ---
            "Caída V (%)": r.get('Reg_Porc', 0),
            "Cumple": "✅" if r.get('Estado_Cumplimiento') == "OK" else "❌"
        }
        datos_filas.append(fila)
        
        # Acumuladores para totales
        suma_kva_total += r.get('kVA_Calc', 0)
        # Estimamos kW reales en bornes (kVA * FP)
        suma_kw_inst += r.get('kVA_Calc', 0) * c.fp

    # 3. Creación del DataFrame
    df = pd.DataFrame(datos_filas)
    
    # 4. Visualización Profesional (Formato Sábana)
    if not df.empty:
        # Estilos avanzados para facilitar la lectura de tantas columnas
        estilo = df.style.hide(axis='index')\
            .set_table_styles([
                {'selector': 'th', 'props': [
                    ('background-color', '#34495e'), 
                    ('color', 'white'), 
                    ('font-size', '11px'), 
                    ('text-align', 'center'),
                    ('vertical-align', 'middle')
                ]},
                {'selector': 'td', 'props': [
                    ('border-bottom', '1px solid #ecf0f1'), 
                    ('font-size', '12px'), 
                    ('text-align', 'center'),
                    ('padding', '6px')
                ]},
                # Resaltar columna de Breaker y Cable Fase
                {'selector': 'td.col5', 'props': [('font-weight', 'bold'), ('background-color', '#f4f6f7')]}, # Breaker (aprox index)
                {'selector': 'td.col6', 'props': [('font-weight', 'bold'), ('color', '#2980b9')]}, # Fase
            ])\
            .format({
                'Caída V (%)': "{:.2f}%",
                'F.P.': "{:.2f}",
                'Eff': "{:.2f}"
            })
            
        display(estilo)
        
        # 5. Resumen de Totales Técnicos
        amp_total = (suma_kva_total * 1000) / (1.732 * t.voltaje) if t.fases == 3 else (suma_kva_total * 1000) / t.voltaje
        
        resumen_html = f"""
        <div style='margin-top:15px; padding:15px; background-color:#eaf2f8; border:1px solid #a9cce3; border-radius:4px;'>
            <h4 style='margin-top:0; color:#154360'>RESUMEN DE CAPACIDAD DEL TABLERO</h4>
            <table style='width:100%; border-collapse: collapse;'>
                <tr>
                    <td style='padding:5px;'>Potencia Instalada (kW):</td>
                    <td style='padding:5px; font-weight:bold; font-size:1.1em'>{suma_kw_inst:.2f} kW</td>
                    <td style='padding:5px;'>Potencia Aparente Total:</td>
                    <td style='padding:5px; font-weight:bold; font-size:1.1em'>{suma_kva_total:.2f} kVA</td>
                </tr>
                <tr>
                    <td style='padding:5px;'>Corriente Nominal Total:</td>
                    <td style='padding:5px; font-weight:bold; font-size:1.1em; color:#d35400'>{amp_total:.1f} A</td>
                    <td style='padding:5px;'><i>(Sin aplicar Factores de Demanda Globales)</i></td>
                    <td></td>
                </tr>
            </table>
        </div>
        """
        display(HTML(resumen_html))
        
    else:
        print("El tablero está vacío. No hay datos para generar el reporte.")
