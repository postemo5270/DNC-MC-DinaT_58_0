import ipywidgets as widgets
from IPython.display import display, clear_output, Markdown, HTML
import backend

# =============================================================================
# MÓDULO DE TRANSFORMADORES (DISEÑO COMPACTO)
# =============================================================================

# --- ESTILOS COMPACTOS ---
layout_full = widgets.Layout(width='98%')
layout_half = widgets.Layout(width='48%')
style_desc = {'description_width': 'initial'} # Para que quepan etiquetas largas

# --- INPUTS ---
drop_tableros = widgets.Dropdown(description="<b>TABLERO:</b>", layout=layout_full, style=style_desc)

# Fila 1: Voltajes
in_v_pri = widgets.FloatText(description="V. Primario:", value=13200, step=100, layout=layout_half)
in_v_sec = widgets.FloatText(description="V. Secundario:", value=480, disabled=True, layout=layout_half)

# Fila 2: Selección Trafo
drop_tipo = widgets.Dropdown(options=[("Aceite Mineral", "ACEITE_MINERAL"), ("Seco (Resina)", "SECO")], description="Tipo:", value="ACEITE_MINERAL", layout=layout_half)
drop_refrig = widgets.Dropdown(options=["ONAN", "ONAF", "AN", "AF"], description="Refrig:", value="ONAN", layout=layout_half)

# Fila 3: Reserva
slide_res = widgets.FloatSlider(value=20, min=0, max=50, description='Reserva %:', layout=layout_full)

# Botón
btn_calc = widgets.Button(description="CALCULAR", button_style='primary', icon='bolt', layout=layout_full)
out_res = widgets.Output()

def al_cambiar_tablero(change):
    if change['type'] == 'change' and change['name'] == 'value':
        backend.SISTEMA_PROYECTO = backend.MEMORIA_TABLEROS[change['new']]
        in_v_sec.value = backend.SISTEMA_PROYECTO.voltaje
        with out_res: clear_output()

drop_tableros.observe(al_cambiar_tablero, names='value')

def ejecutar(b):
    out_res.clear_output()
    tbt = backend.SISTEMA_PROYECTO
    datos_tbt = tbt.get_datos_totales() # Trae kVAR, I_Barraje, etc.
    
    if datos_tbt["kVA"] <= 0:
        with out_res: print("⚠️ El tablero seleccionado no tiene carga.")
        return

    # Calcular Trafo
    tr = backend.Transformador(drop_tipo.value, drop_refrig.value, slide_res.value, in_v_pri.value, tbt.voltaje)
    res_tr = tr.calcular(datos_tbt["kVA"], datos_tbt["kW"], datos_tbt["kVAR"])
    tbt.trafo_asociado = tr
    
    # --- GENERACIÓN DEL REPORTE HTML ---
    html_report = f"""
    <style>
        .report-box {{ border: 1px solid #ddd; padding: 10px; border-radius: 5px; background-color: #f9f9f9; }}
        .report-title {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px; margin-bottom: 10px; }}
        .data-row {{ display: flex; justify-content: space-between; padding: 3px 0; border-bottom: 1px dotted #ccc; }}
        .lbl {{ font-weight: bold; color: #555; }}
        .val {{ color: #000; }}
        .highlight {{ background-color: #e8f6f3; font-weight: bold; color: #117a65; }}
    </style>
    
    <div class="report-box">
        <h3 class="report-title">1.1 TABLERO: {tbt.nombre}</h3>
        <div class="data-row"><span class="lbl">Potencia Activa (P):</span> <span class="val">{round(datos_tbt['kW'], 2)} kW</span></div>
        <div class="data-row"><span class="lbl">Potencia Reactiva (Q):</span> <span class="val">{round(datos_tbt['kVAR'], 2)} kVAR</span></div>
        <div class="data-row"><span class="lbl">Potencia Aparente (S):</span> <span class="val">{round(datos_tbt['kVA'], 2)} kVA</span></div>
        <div class="data-row"><span class="lbl">Factor de Potencia (FP):</span> <span class="val">{round(datos_tbt['FP'], 3)}</span></div>
        <div class="data-row"><span class="lbl">Corriente de Carga ({tbt.voltaje}V):</span> <span class="val">{round(datos_tbt['I_Carga'], 1)} A</span></div>
        <div class="data-row highlight"><span class="lbl">CAPACIDAD MÍNIMA BARRAJE (Ix1.25):</span> <span class="val">{round(datos_tbt['I_Barraje'], 1)} A</span></div>
        
        <br>
        
        <h3 class="report-title">1.2 TRANSFORMADOR SELECCIONADO</h3>
        <div style="text-align:center; margin: 10px 0;">
            <span style="font-size: 20px; font-weight: bold; color: darkblue; border: 2px solid darkblue; padding: 5px 15px; border-radius: 10px;">
                {res_tr['kVA_Com']} kVA
            </span>
        </div>
        
        <div class="data-row"><span class="lbl">Reserva Deseada:</span> <span class="val">{slide_res.value}%</span></div>
        <div class="data-row"><span class="lbl">Cargabilidad Real:</span> <span class="val">{round(res_tr['Cargabilidad'], 2)}%</span></div>
        <div class="data-row"><span class="lbl">Eficiencia (DOE 2016):</span> <span class="val">{res_tr['Eff']}%</span></div>
        <div class="data-row"><span class="lbl">Pérdidas Estimadas:</span> <span class="val">{round(res_tr['Perdidas_kW'], 2)} kW</span></div>
        <div class="data-row"><span class="lbl">Potencia de Entrada (S_in):</span> <span class="val">{round(res_tr['S_In'], 2)} kVA</span></div>
        <div class="data-row"><span class="lbl">FP Final (con pérdidas):</span> <span class="val">{round(res_tr['FP_In'], 3)}</span></div>
        <div class="data-row"><span class="lbl">Corriente Nominal Primario ({in_v_pri.value}V):</span> <span class="val">{round(res_tr['I_Pri_Nom'], 1)} A</span></div>
        <div class="data-row"><span class="lbl">Corriente Nominal Secundario ({tbt.voltaje}V):</span> <span class="val">{round(res_tr['I_Sec_Nom'], 1)} A</span></div>
    </div>
    """
    with out_res: display(HTML(html_report))

btn_calc.on_click(ejecutar)

def iniciar_modulo_trafo():
    # Inicializar lista
    if not backend.MEMORIA_TABLEROS: backend.MEMORIA_TABLEROS = [backend.SISTEMA_PROYECTO]
    drop_tableros.options = [(t.nombre, i) for i, t in enumerate(backend.MEMORIA_TABLEROS)]
    drop_tableros.value = 0
    
    # Interfaz Compacta
    display(widgets.HTML("<h3>🔌 CÁLCULO DE TRANSFORMADOR</h3>"))
    display(drop_tableros)
    
    # Filas compactas (HBox)
    display(widgets.HBox([in_v_pri, in_v_sec]))
    display(widgets.HBox([drop_tipo, drop_refrig]))
    
    display(slide_res)
    display(btn_calc)
    display(out_res)
