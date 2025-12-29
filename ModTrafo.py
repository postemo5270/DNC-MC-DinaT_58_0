import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import backend

# =============================================================================
# MÓDULO DE TRANSFORMADOR Y BARRAJES (REPORTE EN CASCADA PRO)
# =============================================================================

# --- ESTILOS VISUALES (CSS INTEGRADO) ---
# Usamos tablas HTML reales para evitar el problema de la separación excesiva
ESTILO_TABLA = """
<style>
    .eng-table {
        font-family: 'Arial', sans-serif;
        border-collapse: collapse;
        width: 100%; /* Ancho ajustado al contenedor */
        max-width: 600px; /* Evita que se estire demasiado */
        margin-bottom: 20px;
        background-color: #ffffff;
        border: 1px solid #dcdcdc;
    }
    .eng-table th {
        background-color: #2c3e50;
        color: white;
        padding: 8px;
        text-align: left;
        font-size: 14px;
    }
    .eng-table td {
        padding: 6px 10px;
        border-bottom: 1px solid #eee;
        font-size: 13px;
        color: #333;
    }
    .eng-table tr:last-child td { border-bottom: none; }
    .eng-val { text-align: right; font-weight: bold; color: #000; }
    .eng-section { 
        background-color: #f2f3f4; 
        font-weight: bold; 
        color: #2c3e50; 
        text-transform: uppercase;
        font-size: 12px;
        padding: 4px 8px;
    }
    .highlight-row { background-color: #eafaf1; }
    .trafo-header {
        background-color: #c0392b !important; /* Rojo para Trafo */
        text-align: center !important;
    }
    .trafo-result {
        font-size: 18px;
        color: #c0392b;
        font-weight: bold;
        text-align: center;
        padding: 10px;
        border: 2px solid #c0392b;
        background-color: #fdedec;
        margin: 10px 0;
    }
</style>
"""

# --- INPUTS ---
layout_full = widgets.Layout(width='98%')
layout_half = widgets.Layout(width='48%')

# Datos de Entrada del Transformador
in_v_pri = widgets.FloatText(description="V. Primario:", value=13200, step=100, layout=layout_half)
# Nota: El secundario se toma del tablero principal automáticamente

drop_tipo = widgets.Dropdown(options=[("Aceite Mineral", "ACEITE_MINERAL"), ("Seco (Resina)", "SECO")], description="Tipo:", value="ACEITE_MINERAL", layout=layout_half)
drop_refrig = widgets.Dropdown(options=["ONAN", "ONAF", "AN", "AF"], description="Refrig:", value="ONAN", layout=layout_half)
slide_res = widgets.FloatSlider(value=20, min=0, max=50, description='Reserva %:', layout=layout_full)

btn_calc = widgets.Button(description="CALCULAR PROYECTO COMPLETO", button_style='danger', icon='list-ol', layout=layout_full)
out_res = widgets.Output()

def ejecutar_proyecto(b):
    out_res.clear_output()
    
    # 1. Validar que existan tableros
    lista_tbt = backend.MEMORIA_TABLEROS
    if not lista_tbt:
        lista_tbt = [backend.SISTEMA_PROYECTO] # Fallback si solo hay uno
        
    if not lista_tbt[0].circuitos and not lista_tbt[0].sub_tableros:
        with out_res: print("⚠️ No hay datos cargados en el proyecto.")
        return

    # Iniciar HTML con Estilos
    html_content = ESTILO_TABLA
    
    # 2. Bucle: Mostrar Dimensionamiento de Barrajes (Tablero por Tablero)
    html_content += "<h2>1. DIMENSIONAMIENTO DE BARRAJES (TABLEROS)</h2>"
    
    for i, tbt in enumerate(lista_tbt):
        datos = tbt.get_datos_totales()
        
        # Construimos la tabla para este tablero
        html_content += f"""
        <table class="eng-table">
            <thead>
                <tr><th colspan="2">TABLERO {i+1}: {tbt.nombre} ({tbt.voltaje}V)</th></tr>
            </thead>
            <tbody>
                <tr><td>Potencia Activa Total (P)</td><td class="eng-val">{round(datos['kW'], 2)} kW</td></tr>
                <tr><td>Potencia Reactiva Total (Q)</td><td class="eng-val">{round(datos['kVAR'], 2)} kVAR</td></tr>
                <tr><td>Potencia Aparente Total (S)</td><td class="eng-val">{round(datos['kVA'], 2)} kVA</td></tr>
                <tr><td>Factor de Potencia Promedio</td><td class="eng-val">{round(datos['FP'], 3)}</td></tr>
                <tr><td>Corriente de Carga</td><td class="eng-val">{round(datos['I_Carga'], 1)} A</td></tr>
                <tr class="highlight-row">
                    <td><b>CAPACIDAD BARRAJE (I x 1.25)</b></td>
                    <td class="eng-val" style="color:#27ae60">{round(datos['I_Barraje'], 1)} A</td>
                </tr>
            </tbody>
        </table>
        """
        
    # 3. Cálculo del Transformador (Basado en el Tablero Principal - Índice 0)
    tbt_main = lista_tbt[0]
    datos_main = tbt_main.get_datos_totales()
    
    tr = backend.Transformador(drop_tipo.value, drop_refrig.value, slide_res.value, in_v_pri.value, tbt_main.voltaje)
    res_tr = tr.calcular(datos_main["kVA"], datos_main["kW"], datos_main["kVAR"])
    tbt_main.trafo_asociado = tr
    
    html_content += f"""
    <br>
    <h2>2. SELECCIÓN DE TRANSFORMADOR GENERAL</h2>
    <div class="trafo-result">
        TRAFO SELECCIONADO: {res_tr['kVA_Com']} kVA
    </div>
    
    <table class="eng-table">
        <thead>
            <tr><th colspan="2" class="trafo-header">ESPECIFICACIONES TÉCNICAS</th></tr>
        </thead>
        <tbody>
            <tr><td class="eng-section" colspan="2">ENTRADA</td></tr>
            <tr><td>Carga Instalada (Tablero Principal)</td><td class="eng-val">{round(datos_main['kVA'], 2)} kVA</td></tr>
            <tr><td>Reserva Deseada</td><td class="eng-val">{slide_res.value}%</td></tr>
            <tr><td>Potencia Requerida (Carga + Reserva)</td><td class="eng-val">{round(tr.kva_requerido, 2)} kVA</td></tr>
            
            <tr><td class="eng-section" colspan="2">DESEMPEÑO</td></tr>
            <tr><td>Eficiencia (Norma DOE 2016)</td><td class="eng-val">{res_tr['Eff']}%</td></tr>
            <tr><td>Pérdidas Estimadas (a Plena Carga)</td><td class="eng-val">{round(res_tr['Perdidas_kW'], 2)} kW</td></tr>
            <tr><td>Cargabilidad Real</td><td class="eng-val" style="color:{'green' if res_tr['Cargabilidad'] < 85 else 'orange'}">{round(res_tr['Cargabilidad'], 2)}%</td></tr>
            
            <tr><td class="eng-section" colspan="2">ELECTRICO</td></tr>
            <tr><td>Factor de Potencia Entrada (c/Pérdidas)</td><td class="eng-val">{round(res_tr['FP_In'], 3)}</td></tr>
            <tr><td>Corriente Primaria Nominal ({in_v_pri.value}V)</td><td class="eng-val">{round(res_tr['I_Pri_Nom'], 1)} A</td></tr>
            <tr><td>Corriente Secundaria Nominal ({tbt_main.voltaje}V)</td><td class="eng-val">{round(res_tr['I_Sec_Nom'], 1)} A</td></tr>
        </tbody>
    </table>
    """
    
    with out_res:
        display(HTML(html_content))

btn_calc.on_click(ejecutar_proyecto)

def iniciar_modulo_trafo():
    display(widgets.HTML("<h3>⚡ CONFIGURACIÓN DE TRANSFORMADOR</h3>"))
    display(widgets.HBox([in_v_pri, widgets.Label(value="  (El Secundario se detecta autom.)")]))
    display(widgets.HBox([drop_tipo, drop_refrig]))
    display(slide_res)
    display(btn_calc)
    display(out_res)
