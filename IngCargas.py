import ipywidgets as widgets
from IPython.display import display, clear_output
import backend

# =============================================================================
# INTERFAZ DE INGRESO DE CARGAS (V4 - MULTI-VOLTAJE Y SUB-TABLEROS)
# =============================================================================

# --- ESTILOS VISUALES (HORIZONTAL) ---
layout_box = widgets.Layout(width='98%', display='flex', justify_content='flex-start', margin='5px 0px')
layout_input = widgets.Layout(width='auto', flex='1 1 auto', margin='0px 5px')
layout_small = widgets.Layout(width='120px', margin='0px 5px')

# =============================================================================
# SECCIÓN A: CONFIGURACIÓN DEL PROYECTO Y TABLERO PRINCIPAL
# =============================================================================
txt_proyecto = widgets.Text(description="Proyecto:", placeholder="Nombre del Proyecto", layout=layout_input)
# El voltaje aquí es para el Tablero Principal (Padre de todos)
drop_voltaje_main = widgets.Dropdown(options=[480, 440, 220, 208], description="Voltaje TBT:", value=480, layout=layout_small)
btn_reset = widgets.Button(description="NUEVO / RESET", button_style='warning', icon='eraser', layout=widgets.Layout(width='150px'))
out_msg = widgets.Output()

ui_proyecto = widgets.HBox([txt_proyecto, drop_voltaje_main, btn_reset], layout=layout_box)

# =============================================================================
# SECCIÓN B: AGREGAR ELEMENTOS (CARGAS O SUB-TABLEROS)
# =============================================================================
# Selector de TIPO DE ELEMENTO
tog_tipo = widgets.ToggleButtons(
    options=['CARGA FINAL', 'SUB-TABLERO'],
    description='Tipo:',
    disabled=False,
    button_style='info',
    tooltips=['Motor, Iluminación, Toma', 'Alimentador hacia otro tablero aguas abajo']
)

# --- CAMPOS (FILA 1) ---
txt_tag = widgets.Text(description="TAG:", placeholder="M-01 o TBT-02", layout=layout_input)
txt_desc = widgets.Text(description="Desc:", placeholder="Bomba / Tablero Secundario", layout=layout_input)
# Potencia: Si es carga final es kW, si es Sub-Tablero es kW estimados o instalados
float_potencia = widgets.FloatText(description="Pot (kW):", layout=layout_small)

fila_1 = widgets.HBox([txt_tag, txt_desc, float_potencia], layout=layout_box)

# --- CAMPOS (FILA 2) ---
# Fases y FP aplican para ambos
drop_fases = widgets.Dropdown(options=[3, 2, 1], description="Fases:", value=3, layout=layout_small)
float_fp = widgets.FloatText(description="F.P.:", value=0.9, step=0.01, layout=layout_small)
float_long = widgets.FloatText(description="Long (m):", value=10, layout=layout_small)

# Este dropdown de voltaje SOLO es visible si elegimos SUB-TABLERO (Para saber a qué voltaje opera el hijo)
drop_voltaje_sub = widgets.Dropdown(
    options=[480, 440, 220, 208], 
    description="Volt (Sec):", 
    value=220, 
    layout=layout_small,
    disabled=True # Inicia desactivado pq por defecto es Carga Final
)

fila_2 = widgets.HBox([drop_fases, float_fp, float_long, drop_voltaje_sub], layout=layout_box)

# --- CAMPOS (FILA 3 - CONDUCTORES) ---
drop_calibre = widgets.Dropdown(options=backend.ORDEN_CALIBRES, description="Calibre:", value="12", layout=layout_small)
drop_mat = widgets.Dropdown(options=["CU", "AL"], description="Mat:", value="CU", layout=widgets.Layout(width='100px'))
drop_inst = widgets.Dropdown(
    options=[("Ducto", backend.TipoInstalacion.DUCTO), ("Aire", backend.TipoInstalacion.AIRE)],
    description="Instal:", value=backend.TipoInstalacion.DUCTO, layout=layout_input
)
btn_add = widgets.Button(description="AGREGAR", button_style='success', icon='plus', layout=widgets.Layout(width='120px'))

fila_3 = widgets.HBox([drop_calibre, drop_mat, drop_inst, btn_add], layout=layout_box)

out_tabla = widgets.Output()

# =============================================================================
# LÓGICA
# =============================================================================

def on_tipo_change(change):
    # Si cambiamos a Sub-Tablero, habilitamos el selector de voltaje secundario
    if change['new'] == 'SUB-TABLERO':
        drop_voltaje_sub.disabled = False
        float_potencia.description = "Est. (kW):" # Potencia estimada del tablero hijo
    else:
        drop_voltaje_sub.disabled = True
        float_potencia.description = "Pot (kW):"

tog_tipo.observe(on_tipo_change, names='value')

def al_clic_reset(b):
    # 1. Limpiar Backend
    backend.SISTEMA_PROYECTO = backend.Tablero(txt_proyecto.value, drop_voltaje_main.value, 3)
    
    with out_msg:
        clear_output()
        print(f"🗑️ PROYECTO NUEVO: {txt_proyecto.value} | Tensión Principal: {drop_voltaje_main.value}V")
    with out_tabla:
        clear_output()

def al_clic_agregar(b):
    if float_potencia.value <= 0: return

    # Recopilamos datos comunes
    tag = txt_tag.value
    desc = txt_desc.value
    kw = float_potencia.value
    vol_prin = backend.SISTEMA_PROYECTO.voltaje # El voltaje del cable siempre es el del padre
    fases = drop_fases.value
    fp = float_fp.value
    l = float_long.value
    
    # Lógica según tipo
    if tog_tipo.value == 'CARGA FINAL':
        # Creamos Carga
        nuevo_item = backend.Circuito(
            tag=tag, descripcion=desc, potencia_nominal_kw=kw,
            voltaje=vol_prin, fases=fases, factor_potencia=fp,
            tipo_operacion=backend.TipoOperacion.CONTINUA, longitud_mts=l,
            calibre_usuario=drop_calibre.value, material_conductor=drop_mat.value,
            tipo_instalacion=drop_inst.value
        )
        backend.SISTEMA_PROYECTO.agregar_c(nuevo_item)
        res = nuevo_item.ejecutar_seleccion_conductor()
        tipo_txt = "💡 CARGA"
        
    else: # SUB-TABLERO
        # 1. Creamos el objeto Tablero hijo
        vol_hijo = drop_voltaje_sub.value
        nuevo_tablero = backend.Tablero(tag, vol_hijo, fases)
        nuevo_tablero.kva_demandado = kw / fp # Estimacion inicial para calcular el cable alimentador
        
        # 2. Creamos el circuito ALIMENTADOR para ese tablero
        # El alimentador "vive" en el tablero principal, pero alimenta al hijo
        nuevo_item = backend.Circuito(
            tag=f"ALIM-{tag}", descripcion=f"Alim. a {desc}", potencia_nominal_kw=kw,
            voltaje=vol_prin, fases=fases, factor_potencia=fp,
            tipo_operacion=backend.TipoOperacion.CONTINUA, longitud_mts=l,
            calibre_usuario=drop_calibre.value, material_conductor=drop_mat.value,
            tipo_instalacion=drop_inst.value
        )
        # Marcamos que es un alimentador (usuario debe saberlo, o lo forzamos)
        
        backend.SISTEMA_PROYECTO.agregar_c(nuevo_item) # Agregamos el cable
        backend.SISTEMA_PROYECTO.agregar_s(nuevo_tablero) # Agregamos la lógica del tablero hijo
        
        res = nuevo_item.ejecutar_seleccion_conductor()
        tipo_txt = f"⚡ SUB-TBT ({vol_hijo}V)"

    with out_tabla:
        print(f"➕ {tipo_txt} | {tag} | {desc} -> {res['N']}x{res['Calibre']} {res['Mat']} (DV: {round(res['DV'],2)}%)")

btn_reset.on_click(al_clic_reset)
btn_add.on_click(al_clic_agregar)

def iniciar_interfaz():
    display(widgets.HTML("<h3>🏗️ GESTOR DE PROYECTO ELÉCTRICO</h3>"))
    display(ui_proyecto)
    display(out_msg)
    
    display(widgets.HTML("<hr>"))
    display(tog_tipo) # Botones grandes para elegir modo
    display(widgets.VBox([fila_1, fila_2, fila_3]))
    
    display(widgets.HTML("<hr><b>Historial:</b>"))
    display(out_tabla)
