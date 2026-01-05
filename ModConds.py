import pandas as pd
import backend
from IPython.display import display, HTML

def generar_reporte():
    """
    Lee la memoria del backend y genera una tabla resumen profesional.
    """
    # 1. Validación de seguridad
    if not backend.MEMORIA_TABLEROS:
        print("⚠️ No hay datos en memoria. Por favor ejecuta IngCargas primero.")
        return

    # Tomamos el único tablero disponible (Versión Simplificada)
    t = backend.MEMORIA_TABLEROS[0]
    
    # Encabezado
    display(HTML(f"<h3 style='color:#2c3e50'>📊 REPORTE: {t.nombre.upper()} ({t.voltaje}V - {t.fases}F)</h3>"))

    # 2. Extracción de datos
    datos_filas = []
    
    suma_kw = 0.0
    suma_kva = 0.0
    
    for i, c in enumerate(t.circuitos, 1):
        # Extraemos resultados del diccionario 'res' que calculó el backend
        r = c.res 
        
        fila = {
            "Item": i,
            "Tag": c.tag,
            "Descripción": c.descripcion,
            "Potencia": f"{c.p_input} {c.unidad}",
            "I.Nom (A)": round(r.get('I_Nominal', 0), 2),
            "Breaker": f"{r.get('I_Proteccion', 0)} A",
            "Conductor Fase": r.get('Config_Fase', 'Error'),
            "Tierra": r.get('Calibre_Tierra', '-'),
            "Long (m)": c.l_m,
            "Reg %": r.get('Reg_Porc', 0),
        }
        datos_filas.append(fila)
        
        # Acumuladores
        suma_kva += r.get('kVA_Calc', 0)
        # Aproximación de KW (kVA * FP)
        suma_kw += r.get('kVA_Calc', 0) * c.fp

    # 3. Creación del DataFrame
    df = pd.DataFrame(datos_filas)
    
    # 4. Visualización Estilizada
    if not df.empty:
        # Aplicamos formato visual al DataFrame
        estilo = df.style.hide(axis='index')\
            .set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#2c3e50'), ('color', 'white'), ('text-align', 'center')]},
                {'selector': 'td', 'props': [('border-bottom', '1px solid #eee'), ('text-align', 'center')]}
            ])\
            .format({'Reg %': "{:.2f}%"})
            
        display(estilo)
        
        # 5. Resumen de Totales
        amp_total = (suma_kva * 1000) / (1.732 * t.voltaje) if t.fases == 3 else (suma_kva * 1000) / t.voltaje
        
        resumen_html = f"""
        <div style='margin-top:15px; padding:10px; background-color:#e8f6f3; border:1px solid #a2d9ce; color:#0e6251'>
            <b>RESUMEN TOTAL:</b><br>
            Carga Instalada: <b>{suma_kw:.2f} kW</b> | 
            Potencia Aparente: <b>{suma_kva:.2f} kVA</b> | 
            Corriente Estimada: <b>{amp_total:.1f} A</b>
        </div>
        """
        display(HTML(resumen_html))
        
    else:
        print("El tablero está vacío. Agrega cargas para ver el reporte.")
