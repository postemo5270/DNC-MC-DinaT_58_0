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
    nombres = [t.nombre for t in backend.MEMORIA_TABLEROS]
    drop_padre.options = ["NINGUNO (PRINCIPAL)"] + nombres
    txt_tbt_nom.value = ""
    
    with out_main:
        clear_output()
        display(widgets.HTML("<h3>⚡ DEFINICIÓN DE TABLERO</h3>"))
        display(widgets.HBox([num_voltaje, num_fases]))
        display(widgets.VBox([txt_tbt_nom, drop_padre, btn_tbt_ok]))

def on_tbt_save(b):
    if not txt_tbt_nom.value: return
    
    nuevo_tbt = Tablero(nombre=txt_tbt_nom.value, voltaje=num_voltaje.value, fases=num_fases.value)
    
    padre_sel = drop_padre.value
    if padre_sel != "NINGUNO (PRINCIPAL)":
        for t in backend.MEMORIA_TABLEROS:
            if t.nombre == padre_sel:
                t.agregar_sub(nuevo_tbt)
                break
    
    backend.MEMORIA_TABLEROS.append(nuevo_tbt)
    sesion["tbt_actual"] = nuevo_tbt
    mostrar_cargas()

btn_tbt_ok.on_click(on_tbt_save)

# =============================================================================
# 3. PANTALLA INGRESO DE CARGAS (VARIABLES.XLSX)
# =============================================================================
# Identificación
txt_tag = widgets.Text(description="Tag:", placeholder="C-101", layout=style_half)
txt_desc = widgets.Text(description="Desc:", placeholder="Motor Bomba", layout=style_half)

# Potencia y Eficiencia
num_p = widgets.FloatText(description="Potencia:", layout=style_third)
drop_unit = widgets.Dropdown(options=["kW", "hp", "kVA"], value="kW", layout=style_third)
num_fp = widgets.FloatText(description="F.P.:", value=0.9, step=0.01, layout=style_third)
num_eff = widgets.FloatText(description="Eff:", value=1.0, step=0.01, layout=style_third)

# Instalación y Ambiente
num_len = widgets.FloatText(description="Long (m):", value=10.0, layout=style_third)
num_temp = widgets.IntText(description="T.Amb (°C):", value=30, layout=style_third)
drop_inst = widgets.Dropdown(options=["BD-Sub", "BD-Vista", "Bandeja", "Red aérea"], description="Instalación:", value="BD-Sub", layout=style_full)

# Configuración Cable
drop_mat = widgets.Dropdown(options=["Cobre", "Aluminio"], description="Material:", value="Cobre", layout=style_third)
drop_aisl = widgets.Dropdown(options=["THHN", "THWN-2", "XHHW-2", "TW", "THW"], description="Aisl:", value="THHN", layout=style_third)
drop_temp_aisl = widgets.Dropdown(options=[60, 75, 90], description="T.Cable(°C):", value=90, layout=style_third)
drop_neutro = widgets.Dropdown(options=["NO", "SI"], description="Req. Neutro:", value="NO", layout=style_third)

btn_add = widgets.Button(description="CALCULAR Y AGREGAR CARGA", button_style='info', layout=style_full)
btn_fin = widgets.Button(description="FINALIZAR EDICIÓN TABLERO", button_style='warning', layout=style_full)
out_log = widgets.Output()

def mostrar_cargas():
    tbt = sesion["tbt_actual"]
    with out_main:
        clear_output()
        display(widgets.HTML(f"<h3>📝 EDITANDO: <b style='color:#d35400'>{tbt.nombre}</b> ({tbt.voltaje}V - {tbt.fases}F)</h3>"))
        
        # Layout Gráfico
        display(widgets.HTML("<b>1. Identificación y Potencia</b>"))
        display(widgets.HBox([txt_tag, txt_desc]))
        display(widgets.HBox([num_p, drop_unit, num_fp]))
        display(widgets.HBox([num_eff, num_temp]))
        
        display(widgets.HTML("<b>2. Configuración Física</b>"))
        display(widgets.HBox([num_len, drop_inst]))
        display(widgets.HBox([drop_mat, drop_aisl, drop_temp_aisl]))
        display(widgets.HBox([drop_neutro]))

        display(widgets.HTML("<hr>"))
        display(widgets.VBox([btn_add, btn_fin]))
        display(out_log)

def on_add(b):
    if num_p.value <= 0: return
    t = sesion["tbt_actual"]
    
    try:
        # Instanciación usando Variables de MC-ELE-Variables.xlsx
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
        
        # Cálculo inmediato para feedback
        res = nc.ejecutar_calculo()
        
        # Guardar solo si no explota
        t.agregar_c(nc)
        
        # Feedback Visual
        color = "green" if res['Estado_Cumplimiento'] == "OK" else "red"
        msg = f"<b style='color:{color}'>✅ {nc.tag} Agregado:</b> {res['Config_Fase']} + {res['Calibre_Tierra']}(GND) | Reg: {res['Reg_Porc']:.2f}%"
        
        with out_log:
            display(widgets.HTML(msg))
            
        # Limpieza de campos clave
        txt_tag.value = ""
        txt_desc.value = ""

    except Exception as e:
        with out_log:
            display(widgets.HTML(f"❌ <b>Error:</b> {str(e)}"))

def on_fin(b):
    mostrar_decision()

btn_add.on_click(on_add)
btn_fin.on_click(on_fin)

# =============================================================================
# 4. FLUJO FINAL
# =============================================================================
btn_new_tbt = widgets.Button(description="CREAR OTRO TABLERO", button_style='primary')
btn_end_all = widgets.Button(description="VER REPORTE FINAL", button_style='danger')

def mostrar_decision():
    with out_main:
        clear_output()
        display(widgets.VBox([
            widgets.HTML("<h3>¿Desea continuar configurando el sistema?</h3>"),
            btn_new_tbt, 
            btn_end_all
        ]))

btn_new_tbt.on_click(lambda b: mostrar_crear_tbt())
btn_end_all.on_click(lambda b: display(widgets.HTML("<h3>✅ SISTEMA CONFIGURADO. Ejecute la celda de Reporte (ModConds).</h3>")))

def iniciar_interfaz():
    display(out_main)
    mostrar_inicio()
