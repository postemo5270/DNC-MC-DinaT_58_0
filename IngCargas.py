import ipywidgets as widgets
from IPython.display import display, clear_output
import backend
import importlib

# Recargamos backend para asegurar consistencia
importlib.reload(backend)

# =============================================================================
# 1. DEFINICIÓN DE WIDGETS (ELEMENTOS VISUALES)
# =============================================================================
style_input = widgets.Layout(width='98%')

# --- CONFIGURACIÓN DEL TABLERO ÚNICO ---
# Solo pedimos lo esencial para definir el sistema
dd_voltaje = widgets.Dropdown(options=[208, 220, 440, 460, 480], value=480, description="Voltaje (V):", layout=style_input)
dd_fases = widgets.Dropdown(options=[1, 3], value=3, description="Fases:", layout=style_input)
txt_nombre_tablero = widgets.Text(description="Nombre:", value="Tablero Principal", layout=style_input)
btn_crear_tbt = widgets.Button(description="INICIAR TABLERO", button_style='primary', layout=style_input)

# --- FORMULARIO DE CARGAS ---
# Identificación (Nacen vacíos)
txt_tag = widgets.Text(description="Tag:", placeholder="", layout=style_input)
txt_desc = widgets.Text(description="Desc:", placeholder="", layout=style_input)

# Datos Eléctricos
num_p = widgets.FloatText(description="Potencia:", layout=style_input)
dd_unit = widgets.Dropdown(options=["kW", "hp", "kVA"], value="kW", layout=style_input)
num_fp = widgets.FloatText(description="F.P.:", value=0.9, step=0.01, layout=style_input)
num_eff = widgets.FloatText(description="Eff:", value=1.0, step=0.01, layout=style_input)

# Datos Físicos
num_len = widgets.FloatText(description="Long (m):", value=10.0, layout=style_input)
num_temp = widgets.IntText(description="T.Amb (°C):", value=30, layout=style_input)
dd_inst = widgets.Dropdown(options=["Bandeja", "Ducto", "Directamente Enterrado"], description="Inst.:", value="Bandeja", layout=style_input)

# Datos de Cableado
dd_mat = widgets.Dropdown(options=["Cobre", "Aluminio"], description="Material:", value="Cobre", layout=style_input)
dd_aisl = widgets.Dropdown(options=["THHN", "THWN-2", "XHHW-2"], description="Aisl.:", value="THHN", layout=style_input)
dd_temp_cable = widgets.Dropdown(options=[60, 75, 90], description="T.Cable:", value=90, layout=style_input)
dd_neutro = widgets.Dropdown(options=["NO", "SI"], description="Neutro:", value="NO", layout=style_input)

# Botones de Control
btn_add = widgets.Button(description="CALCULAR Y GUARDAR CARGA", button_style='success', layout=style_input)
btn_finish = widgets.Button(description="FINALIZAR EDICIÓN", button_style='danger', layout=style_input)

# Contenedores de Salida
out_main = widgets.Output() # Aquí va toda la interfaz
out_msg = widgets.Output()  # Aquí van los mensajes de éxito/error

# =============================================================================
# 2. LÓGICA DE CONTROL
# =============================================================================

def iniciar_interfaz():
    """Punto de arranque que llama Colab."""
    
    # 1. MOSTRAR EL CONTENEDOR PRINCIPAL (La corrección clave)
    display(out_main)
    
    # 2. Reiniciar memoria y mostrar configuración inicial
    backend.MEMORIA_TABLEROS = []
    
    with out_main:
        clear_output(wait=True)
        display(widgets.HTML("<h3 style='color:#2980b9; border-bottom:2px solid #2980b9'>⚡ Configuración de Tablero Único</h3>"))
        display(widgets.VBox([
            txt_nombre_tablero,
            dd_voltaje, 
            dd_fases, 
            widgets.HTML("<br>"),
            btn_crear_tbt
        ]))

def crear_tablero(b):
    """Crea el objeto Tablero y pasa a la pantalla de cargas."""
    # Instanciamos el tablero usando tu clase de backend
    t = backend.Tablero(txt_nombre_tablero.value, dd_voltaje.value, dd_fases.value)
    backend.MEMORIA_TABLEROS.append(t)
    
    # Pasamos a la siguiente pantalla
    mostrar_formulario_cargas(t)

def mostrar_formulario_cargas(t):
    """Renderiza el formulario de ingreso de datos."""
    
    # Organización visual en filas
    row1 = widgets.HBox([txt_tag, txt_desc])
    row2 = widgets.HBox([num_p, dd_unit, num_fp])
    row3 = widgets.HBox([num_len, dd_inst, num_temp])
    row4 = widgets.HBox([dd_mat, dd_aisl, dd_temp_cable])
    
    # Estructura completa
    form = widgets.VBox([
        widgets.HTML(f"<h3 style='color:#d35400'>📝 Ingresando Cargas a: {t.nombre} ({t.voltaje}V)</h3>"),
        widgets.HTML("<b>1. Datos de Carga</b>"),
        row1, row2,
        widgets.HTML("<b>2. Configuración Física</b>"),
        row3, row4, dd_neutro,
        widgets.HTML("<hr>"),
        btn_add,
        out_msg, # Espacio para mensajes
        widgets.HTML("<br>"),
        btn_finish
    ])
    
    with out_main:
        clear_output(wait=True)
        display(form)

def agregar_carga(b):
    """Lógica de cálculo y guardado."""
    if num_p.value <= 0:
        with out_msg: 
            clear_output()
            display(widgets.HTML("<b style='color:red'>⚠️ Error: La potencia debe ser mayor a 0</b>"))
        return

    # Recuperamos el tablero actual
    t = backend.MEMORIA_TABLEROS[0]
    
    try:
        # 1. Crear el objeto Circuito (Backend)
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
        
        # 2. Ejecutar cálculos matemáticos
        res = c.ejecutar_calculo()
        
        # 3. Guardar en la lista del tablero
        t.agregar_c(c)
        
        # 4. Mostrar Mensaje de Éxito
        msg = f"""
        <div style='background-color:#d4edda; color:#155724; padding:8px; border-radius:4px; margin-top:5px'>
            <b>✅ Carga '{c.tag}' Guardada.</b><br>
            Cables: {res['Config_Fase']} + {res['Calibre_Tierra']}(GND) | Breaker: {res['I_Proteccion']}A
        </div>
        """
        with out_msg:
            clear_output(wait=True)
            display(widgets.HTML(msg))
            
        # 5. Limpiar campos clave para la siguiente carga
        txt_tag.value = ""
        txt_desc.value = ""
        num_p.value = 0.0
        # No limpiamos materiales/físicos para facilitar ingreso masivo similar
        
    except Exception as e:
        with out_msg:
            display(widgets.HTML(f"<b style='color:red'>Error: {str(e)}</b>"))

def finalizar(b):
    """Cierra la interfaz."""
    with out_main:
        clear_output(wait=True)
        display(widgets.HTML(f"""
            <h3 style='color:green'>✅ Tablero '{txt_nombre_tablero.value}' Finalizado</h3>
            <p>Los datos están listos en memoria.</p>
            <p>👉 <b>Ejecuta ahora ModConds.py</b> para ver la tabla de resultados.</p>
        """))

# --- VINCULACIÓN DE EVENTOS ---
btn_crear_tbt.on_click(crear_tablero)
btn_add.on_click(agregar_carga)
btn_finish.on_click(finalizar)
