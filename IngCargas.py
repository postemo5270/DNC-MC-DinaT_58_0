import ipywidgets as widgets
from IPython.display import display, clear_output, Markdown
import backend
from backend import Circuito, Tablero, TipoInstalacion, TipoOperacion

# =============================================================================
# MÓDULO DE INGRESO MANUAL DE CARGAS (ACTUALIZADO CON TEMP Y DERATEOS)
# =============================================================================

# --- WIDGETS DE ENTRADA ---
style = {'description_width': 'initial'}
layout_half = widgets.Layout(width='48%')
layout_full = widgets.Layout(width='98%')

# 1. Datos del Tablero
txt_nombre_tbt = widgets.Text(description="Nombre Tablero:", value="TBT-NUEVO", style=style, layout=layout_half)
num_voltaje_tbt = widgets.FloatText(description="Voltaje (V):", value=480, style=style, layout=layout_half)
btn_crear_tbt = widgets.Button(description="1. CREAR TABLERO", button_style='info', icon='plus-square', layout=layout_full)

# 2. Datos del Circuito
txt_tag = widgets.Text(description="TAG:", placeholder="Ej: M-101", style=style, layout=layout_half)
txt_desc = widgets.Text(description="Descripción:", placeholder="Ej: Bomba Principal", style=style, layout=layout_half)
num_kw = widgets.FloatText(description="Potencia (kW):", value=10.0, style=style, layout=layout_half)
num_fp = widgets.FloatText(description="F. Potencia:", value=0.85, step=0.01, style=style, layout=layout_half)
num_eff = widgets.FloatText(description="Eficiencia (η):", value=0.95, step=0.01, style=style, layout=layout_half) # <--- NUEVO

drop_fases = widgets.Dropdown(options=[3, 1], description="Fases:", value=3, style=style, layout=layout_half)
drop_tipo_op = widgets.Dropdown(options=[("Continua", TipoOperacion.CONTINUA), ("Respaldo", TipoOperacion.RESPALDO)], description="Operación:", style=style, layout=layout_half)
num_long = widgets.FloatText(description="Longitud (m):", value=50, style=style, layout=layout_half)

# 3. Factores y Materiales
num_temp = widgets.IntSlider(description="Temp. Amb (°C):", value=30, min=10, max=80, step=1, style=style, layout=layout_full) # <--- NUEVO (SLIDER)
num_agrup = widgets.FloatSlider(description="F. Agrupamiento:", value=1.0, min=0.5, max=1.0, step=0.05, style=style, layout=layout_full) # <--- NUEVO

drop_mat = widgets.Dropdown(options=["CU", "AL"], description="Material:", value="AL", style=style, layout=layout_half)
drop_inst = widgets.Dropdown(options=[(t.value, t) for t in TipoInstalacion], description="Instalación:", value=TipoInstalacion.BANCO_DUCTOS, style=style, layout=layout_half)
txt_cal_user = widgets.Text(description="Calibre Sugerido:", value="12", style=style, layout=layout_full)

btn_agregar_c = widgets.Button(description="2. AGREGAR CIRCUITO", button_style='success', icon='plus', layout=layout_full)
btn_finalizar = widgets.Button(description="3. FINALIZAR Y GUARDAR", button_style='warning', icon='save', layout=layout_full)

out_log = widgets.Output()

# --- LÓGICA ---
tbt_actual = None

def crear_tablero(b):
    global tbt_actual
    tbt_actual = Tablero(txt_nombre_tbt.value, num_voltaje_tbt.value, 3)
    # Limpiar backend anterior para empezar de cero (opcional, depende flujo)
    # backend.MEMORIA_TABLEROS = [] 
    with out_log:
        clear_output()
        print(f"✅ Tablero '{tbt_actual.nombre}' iniciado. Agregue circuitos.")

def agregar_circuito(b):
    if tbt_actual is None:
        with out_log: print("⚠️ Primero cree el tablero.")
        return
    
    # Crear Circuito con TODOS los nuevos campos
    c = Circuito(
        tag=txt_tag.value,
        descripcion=txt_desc.value,
        potencia_nominal_kw=num_kw.value,
        voltaje=tbt_actual.voltaje,
        fases=drop_fases.value,
        factor_potencia=num_fp.value,
        tipo_operacion=drop_tipo_op.value,
        longitud_mts=num_long.value,
        calibre_usuario=txt_cal_user.value,
        material_conductor=drop_mat.value,
        tipo_instalacion=drop_inst.value,
        # --- NUEVOS CAMPOS CONECTADOS ---
        eficiencia=num_eff.value,
        temp_ambiente=num_temp.value,         # Se envía al backend para buscar en Tabla
        factor_agrupamiento=num_agrup.value   # Se envía al backend
    )
    
    tbt_actual.agregar_c(c)
    
    with out_log:
        print(f"   -> Circuito '{c.tag}' agregado. (Amb: {c.temp_ambiente}°C)")

def finalizar(b):
    if tbt_actual:
        if tbt_actual not in backend.MEMORIA_TABLEROS:
            backend.MEMORIA_TABLEROS.append(tbt_actual)
            backend.SISTEMA_PROYECTO = tbt_actual # Foco
        with out_log:
            print("💾 ¡Guardado en Memoria! Ahora ejecute ModConds o ModTrafo.")
    else:
        with out_log: print("⚠️ Nada que guardar.")

# Eventos
btn_crear_tbt.on_click(crear_tablero)
btn_agregar_c.on_click(agregar_circuito)
btn_finalizar.on_click(finalizar)

def iniciar_ingreso_manual():
    display(Markdown("### 📝 INGRESO MANUAL DE DATOS"))
    display(widgets.HBox([txt_nombre_tbt, num_voltaje_tbt]))
    display(btn_crear_tbt)
    display(Markdown("---"))
    display(widgets.HBox([txt_tag, txt_desc]))
    display(widgets.HBox([num_kw, num_fp]))
    display(widgets.HBox([num_eff, drop_fases])) # Eficiencia aquí
    display(widgets.HBox([drop_tipo_op, num_long]))
    
    display(Markdown("**Factores de Corrección:**"))
    display(num_temp)  # Slider Temp
    display(num_agrup) # Slider Agrupamiento
    
    display(widgets.HBox([drop_mat, drop_inst]))
    display(txt_cal_user)
    display(btn_agregar_c)
    display(Markdown("---"))
    display(btn_finalizar)
    display(out_log)
