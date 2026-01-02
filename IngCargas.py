import ipywidgets as widgets
from IPython.display import display, clear_output
import backend
from backend import Circuito, Tablero, TipoInstalacion, TipoOperacion, EngineeringError

# =============================================================================
# GESTIÓN DE ESTADO DE SESIÓN (STATE MANAGEMENT)
# =============================================================================
sesion = { 
    "tbt_actual": None, 
    "padres_disponibles": [] 
}

# Estilos de Layout
style_full = widgets.Layout(width='98%', margin='5px 0')
style_half = widgets.Layout(width='48%', margin='5px')
out_main = widgets.Output()

# =============================================================================
# 1. PANTALLA INICIO
# =============================================================================
txt_proy = widgets.Text(description="Proyecto:", placeholder="Nombre del Proyecto", layout=style_full)
btn_start = widgets.Button(description="INICIAR / REINICIAR PROYECTO", button_style='primary', layout=style_full)

def mostrar_inicio():
    with out_main:
        clear_output()
        display(widgets.VBox([
            widgets.HTML("<h3 style='color:#2980b9'>📂 GESTIÓN DE PROYECTO ELÉCTRICO</h3>"),
            widgets.HTML("<i>Este módulo permite la creación manual de tableros y cargas.</i>"),
            txt_proy, 
            btn_start
        ]))

def on_start(b):
    if not txt_proy.value: return
    # ATENCIÓN: Reiniciamos la memoria al empezar un proyecto manual nuevo
    backend.MEMORIA_TABLEROS = []
    sesion["padres_disponibles"] = []
    mostrar_crear_tbt()

btn_start.on_click(on_start)

# =============================================================================
# 2. PANTALLA CREAR TABLERO (Jerarquía)
# =============================================================================
txt_tbt_nom = widgets.Text(description="Nombre TBT:", placeholder="Ej: Tablero Principal 1", layout=style_full)
drop_padre = widgets.Dropdown(options=["NINGUNO (PRINCIPAL)"], description="Alimentador:", layout=style_full)
btn_tbt_ok = widgets.Button(description="CREAR TABLERO", button_style='success', layout=style_full)

def mostrar_crear_tbt():
    # Actualizar lista de tableros existentes para posibles padres
    nombres_tableros = [t.nombre for t in backend.MEMORIA_TABLEROS]
    opciones = ["NINGUNO (PRINCIPAL)"] + nombres_tableros
    drop_padre.options = opciones
    txt_tbt_nom.value = ""
    
    with out_main:
        clear_output()
        display(widgets.VBox([
            widgets.HTML("<h3>⚡ DEFINICIÓN DE TABLERO</h3>"),
            widgets.HTML("<i>Configure la jerarquía antes de agregar cargas.</i>"),
            txt_tbt_nom, 
            drop_padre, 
            btn_tbt_ok
        ]))

def on_tbt_save(b):
    if not txt_tbt_nom.value: return
    
    # Instancia usando el Backend Senior
    nuevo_tbt = Tablero(nombre=txt_tbt_nom.value, voltaje=480, fases=3)
    
    padre_sel = drop_padre.value
    if padre_sel != "NINGUNO (PRINCIPAL)":
        # Búsqueda del objeto padre en memoria
        for t in backend.MEMORIA_TABLEROS:
            if t.nombre == padre_sel:
                t.agregar_sub(nuevo_tbt)
                break
    
    backend.MEMORIA_TABLEROS.append(nuevo_tbt)
    sesion["tbt_actual"] = nuevo_tbt
    mostrar_cargas()

btn_tbt_ok.on_click(on_tbt_save)

# =============================================================================
# 3. PANTALLA INGRESO DE CARGAS
# =============================================================================
# Widgets de Entrada
txt_tag = widgets.Text(description="Tag:", placeholder="C-101", layout=widgets.Layout(width='30%'))
txt_desc = widgets.Text(description="Desc:", placeholder="Motor Bomba", layout=widgets.Layout(width='68%'))
num_kw = widgets.FloatText(description="kW:", layout=widgets.Layout(width='30%'))
num_fp = widgets.FloatText(description="F.P.:", value=0.9, step=0.01, layout=widgets.Layout(width='30%'))
num_eff = widgets.FloatText(description="Eff:", value=1.0, step=0.01, layout=widgets.Layout(width='30%'))
num_len = widgets.FloatText(description="Long(m):", value=10.0, layout=widgets.Layout(width='30%'))

drop_mat = widgets.Dropdown(options=["CU", "AL"], description="Material:", value="CU", layout=widgets.Layout(width='30%'))
drop_aisl = widgets.Dropdown(options=["THHN", "XHHW-2"], description="Aisl:", value="THHN", layout=widgets.Layout(width='30%'))
drop_inst = widgets.Dropdown(options=[
    ("Banco Ductos", TipoInstalacion.BANCO_DUCTOS),
    ("Bandeja", TipoInstalacion.BANDEJA),
    ("Ducto PVC", TipoInstalacion.DUCTO),
    ("Aire Libre", TipoInstalacion.AIRE)
], description="Inst:", value=TipoInstalacion.DUCTO, layout=style_full)

btn_add = widgets.Button(description="CALCULAR Y AGREGAR", button_style='info', layout=style_half)
btn_fin = widgets.Button(description="FINALIZAR TABLERO", button_style='warning', layout=style_half)
out_log = widgets.Output()

def mostrar_cargas():
    tbt = sesion["tbt_actual"]
    with out_main:
        clear_output()
        display(widgets.HTML(f"<h3>📝 EDITANDO: <b style='color:#d35400'>{tbt.nombre}</b></h3>"))
        
        # Grid de Inputs
        display(widgets.HBox([txt_tag, txt_desc], layout=style_full))
        display(widgets.HBox([num_kw, num_fp, num_eff], layout=style_full))
        display(widgets.HBox([num_len, drop_mat, drop_aisl], layout=style_full))
        display(drop_inst)
        
        display(widgets.HBox([btn_add, btn_fin], layout=style_full))
        display(out_log)

def on_add(b):
    if num_kw.value <= 0: return
    t = sesion["tbt_actual"]
    
    try:
        # 1. Instanciación Segura
        nc = Circuito(
            tag=txt_tag.value, 
            descripcion=txt_desc.value,
            potencia_nominal_kw=num_kw.value, 
            voltaje=t.voltaje, 
            fases=3,
            factor_potencia=num_fp.value,
            eficiencia=num_eff.value,
            longitud_mts=num_len.value,
            material_conductor=drop_mat.value,
            aislamiento=drop_aisl.value,
            tipo_instalacion=drop_inst.value,
            tipo_operacion=TipoOperacion.CONTINUA
        )
        
        # 2. Ejecución del Cálculo (Puede lanzar EngineeringError)
        res = nc.ejecutar_seleccion_conductor()
        
        # 3. Persistencia si todo sale bien
        t.agregar_c(nc)
        
        # Feedback Visual
        msg = f"✅ <b>{nc.tag}</b>: {res['Config']} | Reg: {res['Reg_Pct']:.2f}%"
        if res['Nota']: msg += f" <span style='color:red'>({res['Nota']})</span>"
        
        with out_log:
            display(widgets.HTML(msg))
            
        # Limpieza parcial
        txt_tag.value = ""
        # Mantener otros valores por comodidad del usuario

    except EngineeringError as e:
        with out_log:
            display(widgets.HTML(f"⛔ <b>ERROR DE INGENIERÍA:</b> {str(e)}"))
    except Exception as e:
        with out_log:
            display(widgets.HTML(f"❌ <b>ERROR DE SISTEMA:</b> {str(e)}"))

def on_fin(b):
    mostrar_decision()

btn_add.on_click(on_add)
btn_fin.on_click(on_fin)

# =============================================================================
# 4. FLUJO FINAL
# =============================================================================
btn_new_tbt = widgets.Button(description="CREAR OTRO TABLERO", button_style='primary', layout=style_full)
btn_end_all = widgets.Button(description="VER REPORTE FINAL", button_style='danger', layout=style_full)

def mostrar_decision():
    with out_main:
        clear_output()
        display(widgets.VBox([
            widgets.HTML("<h3>¿Desea continuar configurando el sistema?</h3>"),
            btn_new_tbt, 
            btn_end_all
        ]))

btn_new_tbt.on_click(lambda b: mostrar_crear_tbt())
btn_end_all.on_click(lambda b: display(widgets.HTML("<h3>✅ SISTEMA CONFIGURADO. Ejecute ModConds para el reporte.</h3>")))

def iniciar_interfaz():
    """Punto de entrada principal"""
    display(out_main)
    mostrar_inicio()
