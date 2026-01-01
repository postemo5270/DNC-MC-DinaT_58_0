import ipywidgets as widgets
from IPython.display import display, clear_output
import backend
from backend import Circuito, Tablero, TipoInstalacion

# =============================================================================
# INTERFAZ AJUSTADA A COLUMNAS ModConds.xlsx
# =============================================================================

sesion = { "tbt_actual": None, "padres_disponibles": [] }
style_full = widgets.Layout(width='98%', margin='5px 0')
style_half = widgets.Layout(width='48%', margin='5px')
out_main = widgets.Output()

# 1. PANTALLA INICIO
txt_proy = widgets.Text(description="Proyecto:", layout=style_full)
btn_start = widgets.Button(description="INICIAR PROYECTO", button_style='primary', layout=style_full)

def mostrar_inicio():
    with out_main:
        clear_output()
        display(widgets.VBox([widgets.HTML("<h3>📂 PROYECTO NUEVO</h3>"), txt_proy, btn_start]))

def on_start(b):
    if not txt_proy.value: return
    backend.MEMORIA_TABLEROS = []
    sesion["padres_disponibles"] = [] # Lista de nombres de tableros creados
    mostrar_crear_tbt()

btn_start.on_click(on_start)

# 2. PANTALLA CREAR TABLERO (Jerarquía Primero)
txt_tbt_nom = widgets.Text(description="Nombre TBT:", placeholder="Ej: Tablero Principal 1", layout=style_full)
drop_padre = widgets.Dropdown(options=["NINGUNO (PRINCIPAL)"], description="Se alimenta de:", layout=style_full)
btn_tbt_ok = widgets.Button(description="CREAR Y AGREGAR CARGAS", button_style='success', layout=style_full)

def mostrar_crear_tbt():
    # Actualizar lista de padres posibles
    opciones = ["NINGUNO (PRINCIPAL)"] + sesion["padres_disponibles"]
    drop_padre.options = opciones
    txt_tbt_nom.value = ""
    
    with out_main:
        clear_output()
        display(widgets.VBox([
            widgets.HTML("<h3>⚡ DEFINIR ESTRUCTURA DE TABLERO</h3>"),
            widgets.HTML("<i>Ingrese primero Subtableros si desea calcular Alimentadores auto.</i>"),
            txt_tbt_nom, drop_padre, btn_tbt_ok
        ]))

def on_tbt_save(b):
    if not txt_tbt_nom.value: return
    nuevo = Tablero(txt_tbt_nom.value, 480, 3)
    
    padre_sel = drop_padre.value
    if padre_sel != "NINGUNO (PRINCIPAL)":
        # Buscar objeto padre (Simplificado por nombre)
        for t in backend.MEMORIA_TABLEROS:
            if t.nombre == padre_sel:
                t.agregar_sub(nuevo)
                break
    
    backend.MEMORIA_TABLEROS.append(nuevo)
    sesion["padres_disponibles"].append(nuevo.nombre)
    sesion["tbt_actual"] = nuevo
    mostrar_cargas()

btn_tbt_ok.on_click(on_tbt_save)

# 3. PANTALLA CARGAS (Campos ModConds)
# Campos inputs según tu Excel
txt_tag = widgets.Text(description="Tag:", placeholder="Ej: Carga sub 11", layout=widgets.Layout(width='30%'))
txt_desc = widgets.Text(description="Desc:", layout=widgets.Layout(width='68%'))
num_kw = widgets.FloatText(description="kW:", layout=widgets.Layout(width='30%'))
num_fp = widgets.FloatText(description="F.P.:", value=0.79, step=0.01, layout=widgets.Layout(width='30%')) # CAMPO NUEVO
num_eff = widgets.FloatText(description="Eff:", value=0.90, step=0.01, layout=widgets.Layout(width='30%'))
num_len = widgets.FloatText(description="Long(m):", value=100.0, layout=widgets.Layout(width='30%'))

drop_mat = widgets.Dropdown(options=["CU", "AL"], description="Material:", value="AL", layout=widgets.Layout(width='30%'))
drop_aisl = widgets.Dropdown(options=["THHN", "XHHW-2"], description="Aisl:", value="THHN", layout=widgets.Layout(width='30%')) # CAMPO NUEVO
drop_inst = widgets.Dropdown(options=[
    ("Banco Ductos", TipoInstalacion.BANCO_DUCTOS),
    ("Bandeja", TipoInstalacion.BANDEJA),
    ("Ducto", TipoInstalacion.DUCTO)
], description="Inst:", value=TipoInstalacion.BANCO_DUCTOS, layout=style_full)

btn_add = widgets.Button(description="AGREGAR CARGA", button_style='info', layout=style_half)
btn_fin = widgets.Button(description="TERMINAR TABLERO", button_style='warning', layout=style_half)
out_list = widgets.Output()

def mostrar_cargas():
    tbt = sesion["tbt_actual"]
    with out_main:
        clear_output()
        display(widgets.HTML(f"<h3>📝 INGRESANDO CARGAS A: <b style='color:blue'>{tbt.nombre}</b></h3>"))
        
        # Fila 1: Identificación
        display(widgets.HBox([txt_tag, txt_desc], layout=style_full))
        # Fila 2: Eléctricos (kW, FP, Eff)
        display(widgets.HBox([num_kw, num_fp, num_eff], layout=style_full))
        # Fila 3: Físicos
        display(widgets.HBox([num_len, drop_mat, drop_aisl], layout=style_full))
        # Fila 4: Instalación
        display(drop_inst)
        
        display(widgets.HBox([btn_add, btn_fin], layout=style_full))
        display(out_list)

def on_add(b):
    if num_kw.value <= 0: return
    t = sesion["tbt_actual"]
    nc = Circuito(
        tag=txt_tag.value, descripcion=txt_desc.value,
        potencia_nominal_kw=num_kw.value, voltaje=t.voltaje, fases=3,
        factor_potencia=num_fp.value,  # Usar input usuario
        eficiencia=num_eff.value,
        longitud_mts=num_len.value,
        material_conductor=drop_mat.value,
        aislamiento=drop_aisl.value,
        tipo_instalacion=drop_inst.value,
        tipo_operacion=backend.TipoOperacion.CONTINUA
    )
    t.agregar_c(nc)
    res = nc.ejecutar_seleccion_conductor()
    
    with out_list:
        print(f"✅ {nc.tag} ({nc.potencia_nominal_kw}kW) -> {res['Config']}")
    
    # Reset basico
    txt_tag.value = ""; num_kw.value = 0.0

def on_fin(b):
    mostrar_decision()

btn_add.on_click(on_add)
btn_fin.on_click(on_fin)

# 4. DECISIÓN
btn_new_tbt = widgets.Button(description="CREAR OTRO TABLERO", button_style='primary', layout=style_full)
btn_end_all = widgets.Button(description="FINALIZAR PROYECTO", button_style='danger', layout=style_full)

def mostrar_decision():
    with out_main:
        clear_output()
        display(widgets.VBox([
            widgets.HTML("<h3>¿Qué sigue?</h3>"),
            btn_new_tbt, btn_end_all
        ]))

btn_new_tbt.on_click(lambda b: mostrar_crear_tbt())
btn_end_all.on_click(lambda b: display(widgets.HTML("<h3>✅ FIN. Ejecute ModConds para ver reporte.</h3>")))

def iniciar_interfaz():
    display(out_main)
    mostrar_inicio()
