import ipywidgets as widgets
from IPython.display import display, clear_output
import backend
import importlib

# Recargamos backend para asegurar que las tablas estén frescas
importlib.reload(backend)

# =============================================================================
# WIDGETS GLOBALES (DEFINICIÓN VISUAL)
# =============================================================================
style_input = widgets.Layout(width='98%')
style_label = widgets.Layout(width='98%', font_weight='bold')

# --- WIDGETS DE CONFIGURACIÓN INICIAL (TABLERO) ---
dd_voltaje = widgets.Dropdown(options=[208, 220, 440, 460, 480], value=480, description="Voltaje (V):", layout=style_input)
dd_fases = widgets.Dropdown(options=[1, 3], value=3, description="Fases:", layout=style_input)
btn_crear_tbt = widgets.Button(description="INICIAR PROYECTO", button_style='primary', layout=style_input)

# --- WIDGETS DE CARGAS (FORMULARIO) ---
# Identificación
txt_tag = widgets.Text(description="Tag:", placeholder="", layout=style_input)
txt_desc = widgets.Text(description="Desc:", placeholder="", layout=style_input)

# Potencia
num_p = widgets.FloatText(description="Potencia:", layout=style_input)
dd_unit = widgets.Dropdown(options=["kW", "hp", "kVA"], value="kW", layout=style_input)
num_fp = widgets.FloatText(description="F.P.:", value=0.9, step=0.01, layout=style_input)
num_eff = widgets.FloatText(description="Eff:", value=1.0, step=0.01, layout=style_input)

# Físico / Cable
num_len = widgets.FloatText(description="Long (m):", value=10.0, layout=style_input)
num_temp = widgets.IntText(description="T.Amb (°C):", value=30, layout=style_input)
dd_inst = widgets.Dropdown(options=["Bandeja", "Ducto", "Directamente Enterrado"], description="Inst.:", value="Bandeja", layout=style_input)
dd_mat = widgets.Dropdown(options=["Cobre", "Aluminio"], description="Material:", value="Cobre", layout=style_input)
dd_aisl = widgets.Dropdown(options=["THHN", "THWN-2", "XHHW-2"], description="Aisl.:", value="THHN", layout=style_input)
dd_temp_cable = widgets.Dropdown(options=[60, 75, 90], description="T.Cable:", value=90, layout=style_input)
dd_neutro = widgets.Dropdown(options=["NO", "SI"], description="Neutro:", value="NO", layout=style_input)

# Botones de Acción
btn_add = widgets.Button(description="CALCULAR Y GUARDAR CARGA", button_style='success', layout=style_input)
btn_finish = widgets.Button(description="FINALIZAR EDICIÓN", button_style='warning', layout=style_input)

# Salidas
out_main = widgets.Output() # Contenedor principal
out_msg = widgets.Output()  # Mensajes de éxito/error

# =============================================================================
# LÓGICA DE CONTROL
# =============================================================================

def iniciar_interfaz():
    """Punto de entrada: Muestra configuración inicial del tablero único."""
    # 1. Limpiamos la memoria anterior para empezar limpio
    backend.MEMORIA_TABLEROS = [] 
    
    # 2. Pantalla de Configuración
    header = widgets.HTML("<h3 style='color:#2c3e50; border-bottom:2px solid #2c3e50'>⚡ NUEVO PROYECTO (Tablero Único)</h3>")
    
    container = widgets.VBox([
        header,
        widgets.HTML("Configura el nivel de tensión del tablero principal:"),
        dd_voltaje,
        dd_fases,
        widgets.HTML("<br>"),
        btn_crear_tbt
    ])
    
    with out_main:
        clear_output(wait=True)
        display(container)

def crear_tablero(b):
    """Crea el objeto Tablero en backend y muestra el formulario de cargas."""
    # 1. Crear Objeto en Backend
    t = backend.Tablero("Tablero Principal", dd_voltaje.value, dd_fases.value)
    backend.MEMORIA_TABLEROS.append(t)
    
    # 2. Renderizar Formulario de Cargas
    mostrar_formulario_cargas(t)

def mostrar_formulario_cargas(t):
    """Construye la interfaz de ingreso de cargas."""
    
    # Estructura visual en filas (HBox) para orden
    row1 = widgets.HBox([txt_tag, txt_desc])
    row2 = widgets.HBox([num_p, dd_unit, num_fp])
    row3 = widgets.HBox([num_len, dd_inst])
    row4 = widgets.HBox([dd_mat, dd_aisl, dd_temp_cable])
    
    form = widgets.VBox([
        widgets.HTML(f"<h3 style='color:#d35400'>📝 Editando: {t.nombre} ({t.voltaje}V)</h3>"),
        widgets.HTML("<b>1. Datos de Carga</b>"),
        row1, row2,
        widgets.HTML("<b>2. Configuración Física</b>"),
        row3, row4,
        widgets.HTML("<hr>"),
        btn_add,
        out_msg, # Aquí saldrán los mensajes verdes
        widgets.HTML("<br>"),
        btn_finish
    ])
    
    with out_main:
        clear_output(wait=True)
        display(form)

def agregar_carga(b):
    """Calcula, guarda y limpia."""
    if num_p.value <= 0:
        with out_msg: 
            clear_output()
            display(widgets.HTML("<b style='color:red'>⚠️ La potencia debe ser mayor a 0</b>"))
        return

    # Obtenemos el único tablero disponible
    t = backend.MEMORIA_TABLEROS[0]
    
    try:
        # 1. Instanciar Circuito (Usando tu clase de Backend)
        c = backend.Circuito(
            tag=txt_tag.value, descripcion=txt_desc.value,
            p_input=num_p.value, unidad=dd_unit.value,
            tension=t.voltaje, fases=t.fases,
            fp=num_fp.value, eff=num_eff.value,
            longitud=num_len.value,
            mat="CU" if dd_mat.value == "Cobre" else "AL",
            tipo_aislam=dd_aisl.value, t_aislamiento_cable=dd_temp_cable.value,
            tipo_instalacion=dd_inst.value, req_neutro=dd_neutro.value,
            t_ambiente=num_temp.value
        )
        
        # 2. Calcular
        res = c.ejecutar_calculo()
        
        # 3. Guardar en Backend
        t.agregar_c(c)
        
        # 4. Feedback Visual (Mensaje Verde)
        msg_html = f"""
        <div style='background-color:#d4edda; color:#155724; padding:10px; border-radius:5px; border:1px solid #c3e6cb'>
            <b>✅ Carga '{c.tag}' Agregada Correctamente</b><br>
            <small>Breaker: {res['I_Proteccion']}A | Cable: {res['Config_Fase']} | Reg: {res['Reg_Porc']:.2f}%</small>
        </div>
        """
        with out_msg:
            clear_output(wait=True)
            display(widgets.HTML(msg_html))
            
        # 5. Limpiar campos para la siguiente carga
        txt_tag.value = ""
        txt_desc.value = ""
        num_p.value = 0.0
        # Ponemos el foco visualmente (mentalmente) en el Tag de nuevo
        
    except Exception as e:
        with out_msg:
            display(widgets.HTML(f"<b style='color:red'>Error Crítico: {str(e)}</b>"))

def finalizar(b):
    """Cierra la edición."""
    with out_main:
        clear_output(wait=True)
        display(widgets.HTML("""
            <h3 style='color:green'>✅ Edición Finalizada</h3>
            <p>Los datos han sido guardados en la memoria.</p>
            <hr>
            <p>👉 <b>Ejecuta ahora el módulo ModConds.py</b> para ver la tabla de resultados y el resumen de carga.</p>
        """))

# --- CONEXIÓN DE EVENTOS ---
btn_crear_tbt.on_click(crear_tablero)
btn_add.on_click(agregar_carga)
btn_finish.on_click(finalizar)
