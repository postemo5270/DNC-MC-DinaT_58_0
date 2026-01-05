import ipywidgets as widgets
from IPython.display import display, clear_output
import backend
from backend import Circuito, Tablero

# =============================================================================
# GESTIÓN DE ESTADO DE SESIÓN
# =============================================================================
sesion = { 
    "tbt_actual": None, 
    "padres_disponibles": [] 
}

# Estilos de Layout para simular formulario profesional
style_full = widgets.Layout(width='98%', margin='2px 0')
style_half = widgets.Layout(width='48%', margin='2px')
style_third = widgets.Layout(width='32%', margin='2px')
out_main = widgets.Output()

# =============================================================================
# 1. PANTALLA INICIO
# =============================================================================
txt_proy = widgets.Text(description="Proyecto:", placeholder="Nombre del Proyecto", layout=style_full)
btn_start = widgets.Button(description="INICIAR PROYECTO", button_style='primary', layout=style_full)

def mostrar_inicio():
    with out_main:
        clear_output()
        display(widgets.HTML("<h3 style='color:#2980b9'>📂 GESTIÓN DE PROYECTO ELÉCTRICO</h3>"))
        display(widgets.VBox([txt_proy, btn_start]))

def on_start(b):
    if not txt_proy.value: return
    # Reinicio limpio de memoria
    backend.MEMORIA_TABLEROS = []
    mostrar_crear_tbt()

btn_start.on_click(on_start)

# =============================================================================
# 2. PANTALLA CREAR TABLERO
# =============================================================================
txt_tbt_nom = widgets.Text(description="Nombre:", placeholder="Ej: Tablero Principal 1", layout=style_full)
num_voltaje = widgets.Dropdown(options=[208, 220, 480, 4160, 13200], description="Voltaje (V):", value=480, layout=style_half)
num_fases = widgets.Dropdown(options=[1, 2, 3], description="Fases:", value=3, layout=style_half)
drop_padre = widgets.Dropdown(options=["NINGUNO (PRINCIPAL)"], description="Alimentador:", layout=style_full)
btn_tbt_ok = widgets.Button(description="CREAR TABLERO", button_style='success', layout=style_full)

def mostrar_crear_tbt():
    # 1. Analisis de estado (Principal vs Sub)
    nombres = [t.nombre for t in backend.MEMORIA_TABLEROS]
    es_primero = len(nombres) == 0
    
    # 2. Configuración de opciones del dropdown (aunque se oculte)
    drop_padre.options = ["NINGUNO (PRINCIPAL)"] + nombres
    drop_padre.value = "NINGUNO (PRINCIPAL)"
    txt_tbt_nom.value = ""
    
    # 3. Construcción visual usando una LISTA de widgets
    # Esto evita que se duplique o se desordene al renderizar
    items_visuales = []
    
    if es_primero:
        # Encabezado Principal
        items_visuales.append(widgets.HTML("<h3 style='color:#2c3e50; border-bottom: 2px solid #2c3e50; padding-bottom:5px'>⚡ DEFINICIÓN TABLERO PRINCIPAL (ACOMETIDA)</h3>"))
        items_visuales.append(widgets.HTML("<div style='margin-bottom: 10px; color:gray'><i>Este será el origen de energía del sistema. No requiere seleccionar alimentador.</i></div>"))
    else:
        # Encabezado Subtablero
        items_visuales.append(widgets.HTML("<h3 style='color:#2980b9; border-bottom: 2px solid #2980b9; padding-bottom:5px'>⚡ AGREGAR NUEVO TABLERO O SUB-TABLERO</h3>"))
    
    # Fila de Voltaje y Fases (Siempre visible)
    items_visuales.append(widgets.HBox([num_voltaje, num_fases], layout=widgets.Layout(margin='10px 0')))
    
    # Nombre del Tablero
    items_visuales.append(txt_tbt_nom)
    
    # Selector de Padre (Solo se agrega a la lista visual si NO es el primero)
    if not es_primero:
        items_visuales.append(drop_padre)
        
    # Botón de Acción
    items_visuales.append(widgets.HTML("<br>"))
    items_visuales.append(btn_tbt_ok)
    
    # 4. Renderizado Limpio en UN SOLO BLOQUE
    contenedor_total = widgets.VBox(items_visuales)
    
    with out_main:
        clear_output(wait=True) # Borra todo rastro anterior inmediatamente
        display(contenedor_total)

def on_tbt_save(b):
    if not txt_tbt_nom.value: return
    
    nuevo_tbt = Tablero(nombre=txt_tbt_nom.value, voltaje=num_voltaje.value, fases=num_fases.value)
    
    padre_sel = drop_padre.value
    if padre_sel != "NINGUNO (PRINCIPAL)":
        nuevo_tbt.padre = padre_sel
        # ... resto del código ...
    
    backend.MEMORIA_TABLEROS.append(nuevo_tbt)
    sesion["tbt_actual"] = nuevo_tbt
    mostrar_cargas()

btn_tbt_ok.on_click(on_tbt_save)

# =============================================================================
# 3. PANTALLA INGRESO DE CARGAS (CORREGIDO PARA VISUALIZACIÓN)
# =============================================================================

# --- Definición de Widgets (Se mantienen igual, solo ajustamos estilos) ---
style_input = widgets.Layout(width='95%') # Ancho seguro para evitar desbordes

# Identificación
txt_tag = widgets.Text(description="Tag:", placeholder="C-101", layout=style_input)
txt_desc = widgets.Text(description="Desc:", placeholder="Motor Bomba", layout=style_input)

# Potencia
num_p = widgets.FloatText(description="Potencia:", layout=style_input)
drop_unit = widgets.Dropdown(options=["kW", "hp", "kVA"], value="kW", layout=style_input)
num_fp = widgets.FloatText(description="F.P.:", value=0.9, step=0.01, layout=style_input)
num_eff = widgets.FloatText(description="Eff:", value=1.0, step=0.01, layout=style_input)

# Configuración Física
num_len = widgets.FloatText(description="Long (m):", value=10.0, layout=style_input)
num_temp = widgets.IntText(description="T.Amb (°C):", value=30, layout=style_input)
drop_inst = widgets.Dropdown(options=["BD-Sub", "BD-Vista", "Bandeja", "Red aérea"], description="Instalación:", value="BD-Sub", layout=style_input)

# Cable
drop_mat = widgets.Dropdown(options=["Cobre", "Aluminio"], description="Material:", value="Cobre", layout=style_input)
drop_aisl = widgets.Dropdown(options=["THHN", "THWN-2", "XHHW-2", "TW", "THW"], description="Aisl:", value="THHN", layout=style_input)
drop_temp_aisl = widgets.Dropdown(options=[60, 75, 90], description="T.Cable(°C):", value=90, layout=style_input)
drop_neutro = widgets.Dropdown(options=["NO", "SI"], description="Req. Neutro:", value="NO", layout=style_input)

# Botones (Colores brillantes para destacar)
btn_add = widgets.Button(description="CALCULAR Y AGREGAR CARGA", button_style='info', layout=widgets.Layout(width='98%', margin='5px 0'))
btn_fin = widgets.Button(description="FINALIZAR EDICIÓN TABLERO", button_style='warning', layout=widgets.Layout(width='98%', margin='5px 0'))

out_log = widgets.Output() # Aquí saldrán los mensajes de "Agregado correctamente"

def mostrar_cargas():
    tbt = sesion["tbt_actual"]
    
    # Construimos la interfaz en BLOQUES (Rows) para asegurar orden
    row_1 = widgets.HBox([txt_tag, txt_desc])
    row_2 = widgets.HBox([num_p, drop_unit, num_fp])
    row_3 = widgets.HBox([num_eff, num_temp])
    row_4 = widgets.HBox([num_len, drop_inst])
    row_5 = widgets.HBox([drop_mat, drop_aisl, drop_temp_aisl])
    row_6 = widgets.HBox([drop_neutro])
    
    # Contenedor principal del formulario
    form_container = widgets.VBox([
        widgets.HTML(f"<h3 style='border-bottom:2px solid #ddd; padding-bottom:5px;'>📝 EDITANDO: <b style='color:#d35400'>{tbt.nombre}</b> ({tbt.voltaje}V - {tbt.fases}F)</h3>"),
        widgets.HTML("<b>1. Identificación y Potencia</b>"),
        row_1, row_2, row_3,
        widgets.HTML("<b>2. Configuración Física y Cable</b>"),
        row_4, row_5, row_6,
        widgets.HTML("<hr>"),
        btn_add, 
        out_log, # El log va ANTES del botón de finalizar para que se vea la confirmación
        widgets.HTML("<br>"),
        btn_fin
    ])

    with out_main:
        clear_output(wait=True) # IMPORTANTE: Borra lo anterior antes de pintar
        display(form_container)

def on_add(b):
    if num_p.value <= 0: return
    t = sesion["tbt_actual"]
    
    try:
        # Instanciación usando Backend
        nc = Circuito(
            tag=txt_tag.value, 
            descripcion=txt_desc.value,
            p_input=num_p.value, 
            unidad=drop_unit.value,
            tension=t.voltaje, 
            fases=t.fases,
            fp=num_fp.value,
            eff=num_eff.value,
            longitud=num_len.value,
            mat="CU" if drop_mat.value == "Cobre" else "AL",
            tipo_aislam=drop_aisl.value,
            t_aislamiento_cable=drop_temp_aisl.value,
            tipo_instalacion=drop_inst.value,
            req_neutro=drop_neutro.value,
            t_ambiente=num_temp.value
        )
        
        # Cálculo
        res = nc.ejecutar_calculo()
        
        # Guardar en memoria
        t.agregar_c(nc)
        
        # Feedback Visual (Sin recargar toda la página)
        color = "green" if res['Estado_Cumplimiento'] == "OK" else "red"
        msg = f"<div style='padding:5px; background-color:#f8f9fa; border-left: 4px solid {color}'>" \
              f"<b>✅ {nc.tag} Agregado:</b> {res['Config_Fase']} + {res['Calibre_Tierra']}(GND) | Reg: {res['Reg_Porc']:.2f}%</div>"
        
        with out_log:
            clear_output(wait=True) # Limpia el mensaje anterior
            display(widgets.HTML(msg))
            
        # Limpieza de campos clave para la siguiente carga
        txt_tag.value = ""
        txt_desc.value = ""

    except Exception as e:
        with out_log:
            display(widgets.HTML(f"❌ <b>Error:</b> {str(e)}"))

def on_fin(b):
    # Lógica de cierre y conexión Top-Down
    tbt_actual = sesion["tbt_actual"]
    
    if tbt_actual and tbt_actual.padre:
        padre_obj = next((t for t in backend.MEMORIA_TABLEROS if t.nombre == tbt_actual.padre), None)
        if padre_obj:
            try:
                carga_subtablero = tbt_actual.exportar_como_circuito()
                padre_obj.agregar_c(carga_subtablero)
                with out_log:
                     display(widgets.HTML(f"<div style='color:green'><b>🔄 VINCULADO AL PADRE:</b> {padre_obj.nombre}</div>"))
            except Exception as e:
                with out_log: display(widgets.HTML(f"Error vinculando: {e}"))
    
    mostrar_decision()

btn_add.on_click(on_add)
btn_fin.on_click(on_fin)

# === AGREGAR ESTO AL FINAL DE IngCargas.py ===

def iniciar_interfaz():
    display(out_main)
    mostrar_inicio()
