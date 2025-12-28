import ipywidgets as widgets
from IPython.display import display, clear_output
import backend  # Importamos el cerebro y la memoria compartida

# =============================================================================
# INTERFAZ DE INGRESO DE CARGAS (V3 - DISEÑO HORIZONTAL + LIMPIEZA)
# =============================================================================

# --- ESTILOS ---
# Definimos un ancho fijo para que se vean ordenados
style_box = widgets.Layout(width='98%', display='flex', justify_content='space-between')
style_input = widgets.Layout(width='auto', flex='1 1 auto') # Flexible

# --- 1. SECCIÓN PROYECTO ---
txt_proyecto = widgets.Text(description="Proyecto:", placeholder="Nombre del Proyecto", layout=style_input)
drop_voltaje = widgets.Dropdown(options=[480, 440, 220, 208], description="Voltaje (V):", value=480, layout=widgets.Layout(width='200px'))
btn_iniciar = widgets.Button(description="NUEVO PROYECTO / RESET", button_style='warning', icon='eraser', layout=widgets.Layout(width='250px'))
out_mensaje_proyecto = widgets.Output()

# Agrupamos en una fila horizontal
ui_proyecto = widgets.HBox([txt_proyecto, drop_voltaje, btn_iniciar], layout=style_box)

# --- 2. SECCIÓN AGREGAR CIRCUITOS ---
# Fila A: Identificación y Potencia
txt_tag = widgets.Text(description="TAG:", placeholder="M-01", layout=style_input)
txt_desc = widgets.Text(description="Desc:", placeholder="Descripción", layout=style_input)
float_potencia = widgets.FloatText(description="Pot (kW):", layout=style_input)

fila_A = widgets.HBox([txt_tag, txt_desc, float_potencia], layout=style_box)

# Fila B: Datos Técnicos Eléctricos
drop_fases = widgets.Dropdown(options=[3, 2, 1], description="Fases:", value=3, layout=style_input)
float_fp = widgets.FloatText(description="F.P.:", value=0.9, step=0.01, layout=style_input)
float_long = widgets.FloatText(description="Long (m):", value=10, layout=style_input)

fila_B = widgets.HBox([drop_fases, float_fp, float_long], layout=style_box)

# Fila C: Selección de Cable y Botón Agregar
drop_calibre = widgets.Dropdown(options=backend.ORDEN_CALIBRES, description="Calibre:", value="12", layout=style_input)
drop_mat = widgets.Dropdown(options=["CU", "AL"], description="Mat:", value="CU", layout=widgets.Layout(width='150px'))
drop_inst = widgets.Dropdown(
    options=[("Ducto", backend.TipoInstalacion.DUCTO), 
             ("Aire", backend.TipoInstalacion.AIRE), 
             ("Agrupado", backend.TipoInstalacion.AGRUP)],
    description="Instal:",
    value=backend.TipoInstalacion.DUCTO,
    layout=style_input
)
btn_agregar = widgets.Button(description="AGREGAR", button_style='success', icon='plus', layout=widgets.Layout(width='150px'))

fila_C = widgets.HBox([drop_calibre, drop_mat, drop_inst, btn_agregar], layout=style_box)

out_tabla = widgets.Output()

# --- LÓGICA (HANDLERS) ---

def al_clic_iniciar(b):
    # 1. LIMPIEZA DE MEMORIA (RESET)
    backend.SISTEMA_PROYECTO.circuitos = []
    backend.SISTEMA_PROYECTO.sub_tableros = []
    
    # 2. Configuración Nueva
    backend.SISTEMA_PROYECTO.nombre = txt_proyecto.value
    backend.SISTEMA_PROYECTO.voltaje = drop_voltaje.value
    
    with out_mensaje_proyecto:
        clear_output()
        print(f"🗑️ Memoria borrada. Nuevo proyecto '{txt_proyecto.value}' ({drop_voltaje.value}V) iniciado.")
        
    with out_tabla:
        clear_output()

def al_clic_agregar(b):
    # Validar campos básicos
    if float_potencia.value <= 0: return

    # 1. Crear el objeto Circuito
    nuevo_c = backend.Circuito(
        tag=txt_tag.value,
        descripcion=txt_desc.value,
        potencia_nominal_kw=float_potencia.value,
        voltaje=drop_voltaje.value,
        fases=drop_fases.value,
        factor_potencia=float_fp.value,
        tipo_operacion=backend.TipoOperacion.CONTINUA,
        longitud_mts=float_long.value,
        calibre_usuario=drop_calibre.value,
        material_conductor=drop_mat.value,
        tipo_instalacion=drop_inst.value
    )
    
    # 2. GUARDAR EN LA MEMORIA GLOBAL
    backend.SISTEMA_PROYECTO.agregar_c(nuevo_c)
    
    # 3. Feedback visual (Lista acumulativa)
    res = nuevo_c.ejecutar_seleccion_conductor()
    
    with out_tabla:
        print(f"✅ {nuevo_c.tag.ljust(6)} | {nuevo_c.descripcion.ljust(15)} | {res['N']}x{res['Calibre']} {res['Mat']} (Reg: {round(res['DV'],2)}%)")

# Conectar botones
btn_iniciar.on_click(al_clic_iniciar)
btn_agregar.on_click(al_clic_agregar)

def iniciar_interfaz():
    # Títulos y Estructura Visual
    display(widgets.HTML("<h3>🏗️ GESTIÓN DE PROYECTO</h3>"))
    display(ui_proyecto)
    display(out_mensaje_proyecto)
    
    display(widgets.HTML("<hr><h3>🔌 DETALLE DE CARGAS</h3>"))
    display(widgets.VBox([fila_A, fila_B, fila_C]))
    
    display(widgets.HTML("<hr><b>Historial de Agregados:</b>"))
    display(out_tabla)
