import ipywidgets as widgets
from IPython.display import display, clear_output
import backend  # Importamos el cerebro y la memoria compartida

# =============================================================================
# INTERFAZ DE INGRESO DE CARGAS (V2 - CON LIMPIEZA DE MEMORIA)
# =============================================================================

# 1. Widgets de Datos Generales
txt_proyecto = widgets.Text(description="Proyecto:", placeholder="Ej: Planta Procesadora")
drop_voltaje = widgets.Dropdown(
    options=[480, 440, 220, 208],
    description="Voltaje (V):",
    value=480
)

# Botón con estilo de 'Advertencia' para indicar que reinicia cosas
btn_iniciar = widgets.Button(description="NUEVO PROYECTO / RESET", button_style='warning', icon='eraser')
out_mensaje_proyecto = widgets.Output()

# 2. Widgets de Circuitos
txt_tag = widgets.Text(description="TAG:", placeholder="M-01")
txt_desc = widgets.Text(description="Desc:", placeholder="Bomba Agua")
float_potencia = widgets.FloatText(description="Pot (kW):")
drop_fases = widgets.Dropdown(options=[3, 2, 1], description="Fases:", value=3)
float_fp = widgets.FloatText(description="F.P.:", value=0.9)
float_long = widgets.FloatText(description="Long (m):", value=10)
drop_calibre = widgets.Dropdown(options=backend.ORDEN_CALIBRES, description="Calibre:", value="12")
drop_mat = widgets.Dropdown(options=["CU", "AL"], description="Mat:", value="CU")
drop_inst = widgets.Dropdown(
    options=[("Ducto", backend.TipoInstalacion.DUCTO), 
             ("Aire", backend.TipoInstalacion.AIRE), 
             ("Agrupado", backend.TipoInstalacion.AGRUP)],
    description="Instal:",
    value=backend.TipoInstalacion.DUCTO
)

btn_agregar = widgets.Button(description="AGREGAR CIRCUITO", button_style='success', icon='plus')
out_tabla = widgets.Output()

def al_clic_iniciar(b):
    # 1. LIMPIEZA DE MEMORIA (RESET)
    # Vaciamos la lista de circuitos y subtableros para empezar de cero
    backend.SISTEMA_PROYECTO.circuitos = []
    backend.SISTEMA_PROYECTO.sub_tableros = []
    
    # 2. Configuración Nueva
    backend.SISTEMA_PROYECTO.nombre = txt_proyecto.value
    backend.SISTEMA_PROYECTO.voltaje = drop_voltaje.value
    
    with out_mensaje_proyecto:
        clear_output()
        print(f"🗑️ Memoria limpiada.")
        print(f"✅ PROYECTO '{txt_proyecto.value}' INICIADO ({drop_voltaje.value}V).")
        print("   La base de datos está vacía y lista para nuevos circuitos. 👇")
        
    # Limpiamos también la tabla visual de abajo para que no confunda
    with out_tabla:
        clear_output()

def al_clic_agregar(b):
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
    
    # 3. Feedback visual
    res = nuevo_c.ejecutar_seleccion_conductor()
    
    with out_tabla:
        # No usamos clear_output aquí para que se vaya haciendo una lista acumulativa visual
        print(f"➕ {nuevo_c.tag} | {nuevo_c.descripcion} -> {res['N']}x{res['Calibre']} {res['Mat']}")

# Conectar botones
btn_iniciar.on_click(al_clic_iniciar)
btn_agregar.on_click(al_clic_agregar)

def iniciar_interfaz():
    display(widgets.HTML("<h2>🏗️ GESTIÓN DE PROYECTO Y CARGAS</h2>"))
    display(widgets.HTML("<i>Nota: Al hacer clic en 'Nuevo Proyecto', se borran los datos anteriores.</i>"))
    display(txt_proyecto, drop_voltaje, btn_iniciar, out_mensaje_proyecto)
    
    display(widgets.HTML("<hr><h3>🔌 AGREGAR CARGAS</h3>"))
    display(txt_tag, txt_desc, float_potencia, drop_fases, float_fp, float_long)
    display(drop_calibre, drop_mat, drop_inst, btn_agregar)
    display(out_tabla)
