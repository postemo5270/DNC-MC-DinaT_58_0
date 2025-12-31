import ipywidgets as widgets
from IPython.display import display, clear_output
import backend

# =============================================================================
# INTERFAZ DE INGRESO DE CARGAS (V-FINAL: ANCHO COMPLETO + OPCIONES)
# =============================================================================

# --- VARIABLES ---
sesion = { "proyecto": "", "tbt_actual": None }

# --- ESTILOS DE ANCHO COMPLETO (FULL WIDTH) ---
# Usamos '98%' para que ocupe casi todo el ancho de la celda de Colab
style_full = widgets.Layout(width='98%', margin='5px 0')
style_half = widgets.Layout(width='48%', margin='5px')
style_btn = widgets.Layout(width='98%', margin='10px 0')

out_main = widgets.Output()

# =============================================================================
# PANTALLA 1: INICIO
# =============================================================================
txt_proy = widgets.Text(description="Proyecto:", placeholder="Nombre del Proyecto...", layout=style_full)
btn_proy = widgets.Button(description="INICIAR PROYECTO", button_style='primary', layout=style_btn)

def ir_a_crear_tbt(tipo="PRINCIPAL"):
    txt_tbt_nom.value = ""
    sesion["tipo_tbt"] = tipo
    
    titulo = "2️⃣ CREAR TABLERO PRINCIPAL" if tipo == "PRINCIPAL" else "4️⃣ CREAR SUB-TABLERO"
    color = "darkblue" if tipo == "PRINCIPAL" else "darkred"
    
    with out_main:
        clear_output()
        display(widgets.HTML(f"<h3 style='color:{color}'>{titulo}</h3>"))
        if tipo == "SUBORDINADO":
            padre = sesion["tbt_actual"].nombre
            display(widgets.HTML(f"<b>Depende de:</b> {padre}"))
        
        display(widgets.VBox([
            txt_tbt_nom,
            drop_tbt_vol,
            btn_tbt_ok
        ]))

def on_inicio(b):
    if not txt_proy.value: return
    # Reset
    backend.SISTEMA_PROYECTO.circuitos = []
    backend.SISTEMA_PROYECTO.sub_tableros = []
    backend.SISTEMA_PROYECTO.nombre = txt_proy.value
    ir_a_crear_tbt("PRINCIPAL")

btn_proy.on_click(on_inicio)

# =============================================================================
# PANTALLA 2: CREAR TBT
# =============================================================================
txt_tbt_nom = widgets.Text(description="Nombre TBT:", placeholder="Ej: TBT-Proceso-01", layout=style_full)
drop_tbt_vol = widgets.Dropdown(options=[480, 440, 220, 208], description="Voltaje (V):", value=480, layout=style_full)
btn_tbt_ok = widgets.Button(description="GUARDAR Y CONTINUAR A CARGAS", button_style='success', layout=style_btn)

def ir_a_cargas():
    tbt = sesion["tbt_actual"]
    with out_main:
        clear_output()
        display(widgets.HTML(f"<h3>3️⃣ CARGAS PARA: <span style='color:blue'>{tbt.nombre}</span></h3>"))
        
        # Formulario ancho
        display(widgets.HBox([txt_c_tag, txt_c_desc], layout=widgets.Layout(width='100%')))
        display(widgets.HBox([num_c_kw, drop_c_fases, num_c_long], layout=widgets.Layout(width='100%')))
        display(widgets.HBox([drop_c_cal, drop_c_mat], layout=widgets.Layout(width='100%')))
        display(drop_c_inst) # Fila propia porque es larga la lista
        
        display(widgets.HBox([btn_c_add, btn_c_fin], layout=widgets.Layout(width='100%')))
        display(widgets.HTML("<hr>"))
        display(out_lista)

def on_crear_tbt(b):
    if not txt_tbt_nom.value: return
    nuevo_tbt = backend.Tablero(txt_tbt_nom.value, drop_tbt_vol.value, 3)
    sesion["tbt_actual"] = nuevo_tbt
    ir_a_cargas()

btn_tbt_ok.on_click(on_crear_tbt)

# =============================================================================
# PANTALLA 3: CARGAS
# =============================================================================
# Inputs configurados para ocupar espacio (flex)
txt_c_tag = widgets.Text(description="TAG:", layout=widgets.Layout(width='30%'))
txt_c_desc = widgets.Text(description="Desc:", layout=widgets.Layout(width='68%'))

num_c_kw = widgets.FloatText(description="kW:", layout=widgets.Layout(width='32%'))
drop_c_fases = widgets.Dropdown(options=[3, 2, 1], description="Fases:", value=3, layout=widgets.Layout(width='32%'))
num_c_long = widgets.FloatText(description="m:", value=10, layout=widgets.Layout(width='32%'))

drop_c_cal = widgets.Dropdown(options=backend.ORDEN_CALIBRES, description="Calibre:", value="12", layout=widgets.Layout(width='49%'))
drop_c_mat = widgets.Dropdown(options=["CU", "AL"], description="Material:", value="CU", layout=widgets.Layout(width='49%'))

# LISTA COMPLETA DE INSTALACIONES
drop_c_inst = widgets.Dropdown(
    options=[
        ("Ducto (PVC/IMC)", backend.TipoInstalacion.DUCTO), 
        ("Aire Libre", backend.TipoInstalacion.AIRE), 
        ("Bandeja Portacables", backend.TipoInstalacion.BANDEJA),
        ("Banco de Ductos", backend.TipoInstalacion.BANCO_DUCTOS),
        ("Red Trenzada", backend.TipoInstalacion.TRENZADA),
        ("Agrupado", backend.TipoInstalacion.AGRUP)
    ],
    description="Instalación:", 
    value=backend.TipoInstalacion.DUCTO,
    layout=style_full
)

btn_c_add = widgets.Button(description="AGREGAR OTRA", button_style='info', icon='plus', layout=style_half)
btn_c_fin = widgets.Button(description="TERMINAR ESTE TBT", button_style='warning', icon='check', layout=style_half)
out_lista = widgets.Output()

def guardar_carga():
    if num_c_kw.value <= 0: return False
    tbt = sesion["tbt_actual"]
    
    nc = backend.Circuito(
        tag=txt_c_tag.value, descripcion=f"[{tbt.nombre}] {txt_c_desc.value}",
        potencia_nominal_kw=num_c_kw.value, voltaje=tbt.voltaje, fases=drop_c_fases.value, 
        factor_potencia=0.9, tipo_operacion=backend.TipoOperacion.CONTINUA, longitud_mts=num_c_long.value,
        calibre_usuario=drop_c_cal.value, material_conductor=drop_c_mat.value,
        tipo_instalacion=drop_c_inst.value
    )
    backend.SISTEMA_PROYECTO.agregar_c(nc)
    res = nc.ejecutar_seleccion_conductor()
    
    with out_lista:
        print(f"✅ {nc.tag} ({num_c_kw.value}kW) -> {res['N']}x{res['Calibre']} ({res['Nota']})")
    
    # Reset
    txt_c_tag.value = ""; txt_c_desc.value = ""; num_c_kw.value = 0.0
    return True

def on_add(b): guardar_carga()
def on_fin(b):
    if num_c_kw.value > 0: guardar_carga()
    out_lista.clear_output()
    ir_a_decision()

btn_c_add.on_click(on_add)
btn_c_fin.on_click(on_fin)

# =============================================================================
# PANTALLA 4: DECISIÓN
# =============================================================================
btn_d_sub = widgets.Button(description="AGREGAR SUB-TABLERO", button_style='info', layout=style_btn)
btn_d_new = widgets.Button(description="OTRO TBT PRINCIPAL", button_style='primary', layout=style_btn)
btn_d_end = widgets.Button(description="FINALIZAR TODO", button_style='danger', layout=style_btn)

def ir_a_decision():
    with out_main:
        clear_output()
        display(widgets.HTML("<h3>¿QUÉ SIGUE?</h3>"))
        display(btn_d_sub)
        display(btn_d_new)
        display(btn_d_end)

btn_d_sub.on_click(lambda b: ir_a_crear_tbt("SUBORDINADO"))
btn_d_new.on_click(lambda b: ir_a_crear_tbt("PRINCIPAL"))

def fin_total(b):
    with out_main:
        clear_output()
        display(widgets.HTML("<h3>✅ FIN. Ejecuta ModConds para ver resultados.</h3>"))

btn_d_end.on_click(fin_total)

def iniciar_interfaz():
    with out_main:
        clear_output()
        display(widgets.HTML("<h3>1️⃣ PROYECTO</h3>"))
        display(widgets.HBox([txt_proy], layout=widgets.Layout(width='100%')))
        display(btn_proy)
    display(out_main)
