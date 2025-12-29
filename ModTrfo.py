import ipywidgets as widgets
from IPython.display import display, clear_output, Markdown
import backend

# =============================================================================
# MÓDULO DE SELECCIÓN DE TRANSFORMADOR
# =============================================================================

# --- WIDGETS ---
style_full = widgets.Layout(width='98%', margin='5px 0')
style_half = widgets.Layout(width='48%', margin='5px')

# Inputs
drop_tipo = widgets.Dropdown(
    options=[
        ("Aceite Mineral", "ACEITE_MINERAL"),
        ("Aceite Vegetal (FR3)", "ACEITE_VEGETAL"),
        ("Seco (Resina/VPI)", "SECO")
    ],
    description="Tipo:",
    value="ACEITE_MINERAL",
    layout=style_full
)

drop_refrig = widgets.Dropdown(
    options=["ONAN", "ONAF", "KNAN", "KNAF", "AN", "AF"],
    description="Refrig:",
    value="ONAN",
    layout=style_full
)

num_v_pri = widgets.FloatText(description="V Primario:", value=13200, step=100, layout=style_half)
num_v_sec = widgets.FloatText(description="V Secun:", value=480, disabled=True, layout=style_half) # Lee del tablero

slide_reserva = widgets.FloatSlider(
    value=20, min=0, max=50, step=5,
    description='Reserva %:',
    continuous_update=False,
    layout=style_full
)

btn_calc_trafo = widgets.Button(description="CALCULAR TRANSFORMADOR", button_style='danger', icon='bolt', layout=style_full)
out_trafo = widgets.Output()

def actualizar_voltaje_secundario():
    # Sincronizar con el voltaje del tablero actual
    if backend.SISTEMA_PROYECTO:
        num_v_sec.value = backend.SISTEMA_PROYECTO.voltaje

def ejecutar_calculo_trafo(b):
    out_trafo.clear_output()
    tbt = backend.SISTEMA_PROYECTO
    
    # 1. Calcular Carga Total del Tablero
    kva_load, kw_load = tbt.calcular_carga_total()
    
    if kva_load <= 0:
        with out_trafo:
            print("⚠️ El tablero no tiene carga. Agrega circuitos en IngCargas primero.")
        return

    # 2. Instanciar Transformador
    nuevo_trafo = backend.Transformador(
        tipo=drop_tipo.value,
        refrigeracion=drop_refrig.value,
        reserva_deseada=slide_reserva.value,
        voltaje_pri=num_v_pri.value,
        voltaje_sec=tbt.voltaje
    )
    
    # 3. Ejecutar Cálculo
    res = nuevo_trafo.calcular(kva_load, kw_load)
    tbt.trafo_asociado = nuevo_trafo # Guardar en memoria
    
    # 4. Mostrar Resultados
    with out_trafo:
        display(Markdown(f"### ⚡ Resultados para {tbt.nombre}"))
        print(f"🔹 Carga Instalada: {round(kva_load, 2)} kVA ({round(kw_load, 2)} kW)")
        print(f"🔹 Carga + Reserva ({slide_reserva.value}%): {round(nuevo_trafo.kva_requerido, 2)} kVA")
        print("-" * 40)
        
        # Tabla resumen
        display(widgets.HTML(f"""
        <table style="width:100%; border: 1px solid #ccc;">
            <tr style="background-color: #f0f0f0;">
                <th>TRAFO SELECCIONADO</th>
                <th>EFICIENCIA (DOE 2016)</th>
                <th>CARGABILIDAD</th>
            </tr>
            <tr>
                <td style="font-size: 1.2em; color: darkblue; text-align:center;"><b>{res['kVA_Com']} kVA</b></td>
                <td style="text-align:center;">{res['Eff']}%</td>
                <td style="text-align:center; color: {'green' if res['Cargabilidad'] < 80 else 'orange'};">
                    {round(res['Cargabilidad'], 2)}%
                </td>
            </tr>
        </table>
        <br>
        <table style="width:100%">
            <tr><td><b>FP Ponderado (Entrada):</b></td><td>{round(res['FP_Final'], 3)}</td></tr>
            <tr><td><b>Corriente Primaria ({num_v_pri.value}V):</b></td><td>{round(res['I_Pri'], 1)} A (Barraje Rec.)</td></tr>
            <tr><td><b>Corriente Secundaria ({tbt.voltaje}V):</b></td><td>{round(res['I_Sec'], 1)} A (Barraje Rec.)</td></tr>
        </table>
        """))

btn_calc_trafo.on_click(ejecutar_calculo_trafo)

def iniciar_modulo_trafo():
    actualizar_voltaje_secundario()
    display(widgets.HTML("<h3>🔌 SELECCIÓN DE TRANSFORMADOR</h3>"))
    display(widgets.VBox([
        widgets.HBox([num_v_pri, num_v_sec]),
        drop_tipo,
        drop_refrig,
        slide_reserva,
        btn_calc_trafo,
        out_trafo
    ]))
