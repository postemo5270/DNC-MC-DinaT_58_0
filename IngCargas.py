import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import backend
from backend import Circuito, Tablero, TipoInstalacion, TipoOperacion

# =============================================================================
# INTERFAZ DE INGRESO DE CARGAS - FLUJO SECUENCIAL (WIZARD)
# =============================================================================

# --- ESTILOS Y VARIABLES ---
sesion = { "tbt_actual": None, "conteo_cargas": 0 }
style_full = widgets.Layout(width='98%', margin='5px 0')
style_half = widgets.Layout(width='48%', margin='5px')
style_btn = widgets.Layout(width='98%', margin='15px 0')

out_main = widgets.Output()

# =============================================================================
# 1. PANTALLA INICIO (PROYECTO)
# =============================================================================
txt_proy = widgets.Text(description="Proyecto:", placeholder="Nombre del Proyecto...", layout=style_full)
btn_start = widgets.Button(description="INICIAR PROYECTO", button_style='primary', icon='play', layout=style_btn)

def mostrar_inicio():
    with out_main:
        clear_output()
        display(HTML("<h3>📂 1. CONFIGURACIÓN DEL PROYECTO</h3>"))
        display(txt_proy)
        display(btn_start)

def on_start(b):
    if not txt_proy.value: return
    # Reiniciar Memoria Global
    backend.MEMORIA_TABLEROS = []
    # Crear un sistema base (dummy) o usar el nombre para el reporte
    backend.SISTEMA_PROYECTO = backend.Tablero(txt_proy.value, 480, 3)
    mostrar_crear_tbt("PRINCIPAL")

btn_start.on_click(on_start)

# =============================================================================
# 2. PANTALLA CREAR TABLERO
# =============================================================================
txt_tbt_nom = widgets.Text(description="Nombre TBT:", placeholder="Ej: TBT-Principal", layout=style_full)
drop_tbt_vol = widgets.Dropdown(options=[480, 440, 220, 208], description="Voltaje (V):", value=480, layout=style_full)
btn_tbt_save = widgets.Button(description="CREAR Y AGREGAR CARGAS", button_style='success', icon='arrow-right', layout=style_btn)

def mostrar_crear_tbt(tipo):
    sesion["tipo_tbt"] = tipo
    txt_tbt_nom.value = "" # Limpiar
    
    titulo = "⚡ 2. NUEVO TABLERO PRINCIPAL" if tipo == "PRINCIPAL" else "↳ 2. NUEVO SUB-TABLERO"
    color = "darkblue" if tipo == "PRINCIPAL" else "darkred"
    
    with out_main:
        clear_output()
        display(HTML(f"<h3 style='color:{color}'>{titulo}</h3>"))
        if tipo == "SUBORDINADO" and sesion["tbt_actual"]:
            display(HTML(f"<b>Alimentado desde:</b> {sesion['tbt_actual'].nombre}"))
            
        display(txt_tbt_nom)
        display(drop_tbt_vol)
        display(btn_tbt_save)

def on_tbt_save(b):
    if not txt_tbt_nom.value: return
    # Crear Objeto Tablero
    nuevo_tbt = Tablero(txt_tbt_nom.value, drop_tbt_vol.value, 3)
    
    # Guardar en sesión y memoria global
    sesion["tbt_actual"] = nuevo_tbt
    sesion["conteo_cargas"] = 0
    backend.MEMORIA_TABLEROS.append(nuevo_tbt)
    
    # Si es subtablero, enlazar lógica (pendiente implementar enlace físico en backend)
    # Por ahora solo lo creamos secuencialmente
    
    mostrar_loop_cargas()

btn_tbt_save.on_click(on_tbt_save)

# =============================================================================
# 3. PANTALLA LOOP DE CARGAS (LA FÁBRICA)
# =============================================================================
# Inputs vacíos o neutros para no confundir
txt_c_tag = widgets.Text(description="TAG:", placeholder="Ej: M-101", layout=widgets.Layout(width='30%'))
txt_c_desc = widgets.Text(description="Desc:", placeholder="Ej: Bomba de Agua", layout=widgets.Layout(width='68%'))

num_c_kw = widgets.FloatText(description="kW:", value=0.0, layout=widgets.Layout(width='32%')) # Inicia en 0
drop_c_fases = widgets.Dropdown(options=[3, 2, 1], description="Fases:", value=3, layout=widgets.Layout(width='32%'))
num_c_long = widgets.FloatText(description="Long(m):", value=0.0, layout=widgets.Layout(width='32%'))

# Factores
num_c_eff = widgets.BoundedFloatText(description="Eff (η):", value=0.90, min=0.1, max=1.0, step=0.01, layout=widgets.Layout(width='32%'))
num_c_temp = widgets.IntSlider(description="Temp(°C)", value=30, min=10, max=80, step=1, layout=widgets.Layout(width='32%'))
num_c_agrup = widgets.FloatSlider(description="F.Agrup", value=1.0, min=0.5, max=1.0, step=0.05, layout=widgets.Layout(width='32%'))

# Material
drop_c_cal = widgets.Dropdown(options=backend.ORDEN_CALIBRES, description="Sugerido:", value="12", layout=widgets.Layout(width='49%'))
drop_c_mat = widgets.Dropdown(options=["CU", "AL"], description="Material:", value="CU", layout=widgets.Layout(width='49%'))
drop_c_inst = widgets.Dropdown(
    options=[("Ducto (PVC/IMC)", backend.TipoInstalacion.DUCTO), ("Bandeja", backend.TipoInstalacion.BANDEJA), 
             ("Banco Ductos", backend.TipoInstalacion.BANCO_DUCTOS), ("Aire Libre", backend.TipoInstalacion.AIRE)],
    description="Instal:", value=backend.TipoInstalacion.DUCTO, layout=style_full
)

btn_add = widgets.Button(description="AGREGAR CARGA (+)", button_style='info', layout=style_half)
btn_end_tbt = widgets.Button(description="FINALIZAR TABLERO", button_style='warning', layout=style_half)
out_tabla = widgets.Output()

def mostrar_loop_cargas():
    tbt = sesion["tbt_actual"]
    with out_main:
        clear_output()
        display(HTML(f"<h3 style='background-color:#eee; padding:5px'>3. AGREGANDO CARGAS A: <span style='color:blue'>{tbt.nombre}</span></h3>"))
        
        # Formulario
        display(widgets.HBox([txt_c_tag, txt_c_desc], layout=style_full))
        display(widgets.HBox([num_c_kw, drop_c_fases, num_c_long], layout=style_full))
        display(HTML("<i>Factores de Corrección:</i>"))
        display(widgets.HBox([num_c_temp, num_c_agrup, num_c_eff], layout=style_full))
        display(HTML("<i>Conductor e Instalación:</i>"))
        display(widgets.HBox([drop_c_mat, drop_c_cal], layout=style_full))
        display(drop_c_inst)
        
        display(widgets.HBox([btn_add, btn_end_tbt], layout=style_full))
        display(HTML("<hr>"))
        display(out_tabla) # Aquí se verá la lista acumulada

def actualizar_tabla_visual():
    tbt = sesion["tbt_actual"]
    html = "<table style='width:100%; border-collapse:collapse; font-size:12px'>"
    html += "<tr style='background:#ccc'><th>Tag</th><th>Desc</th><th>kW</th><th>Cable</th></tr>"
    for c in tbt.circuitos:
        res = c._res_conductor if c._res_conductor else {"Config": "Pendiente"}
        html += f"<tr><td>{c.tag}</td><td>{c.descripcion}</td><td>{c.potencia_nominal_kw}</td><td>{res.get('Config','?')}</td></tr>"
    html += "</table>"
    with out_tabla:
        clear_output()
        display(HTML(f"<b>Cargas Agregadas: {len(tbt.circuitos)}</b>"))
        display(HTML(html))

def on_add_carga(b):
    if num_c_kw.value <= 0: return # Validación básica
    
    tbt = sesion["tbt_actual"]
    nc = Circuito(
        tag=txt_c_tag.value, descripcion=txt_c_desc.value,
        potencia_nominal_kw=num_c_kw.value, voltaje=tbt.voltaje, fases=drop_c_fases.value,
        factor_potencia=0.9, tipo_operacion=backend.TipoOperacion.CONTINUA,
        longitud_mts=num_c_long.value, calibre_usuario=drop_c_cal.value,
        material_conductor=drop_c_mat.value, tipo_instalacion=drop_c_inst.value,
        # Nuevos campos
        eficiencia=num_c_eff.value, temp_ambiente=num_c_temp.value, factor_agrupamiento=num_c_agrup.value
    )
    
    # Calcular antes de guardar para ver resultado rápido
    nc.ejecutar_seleccion_conductor()
    tbt.agregar_c(nc)
    
    # Limpiar campos para la siguiente
    txt_c_tag.value = ""; txt_c_desc.value = ""; num_c_kw.value = 0.0
    actualizar_tabla_visual()

def on_end_tbt(b):
    mostrar_decision()

btn_add.on_click(on_add_carga)
btn_end_tbt.on_click(on_end_tbt)

# =============================================================================
# 4. PANTALLA DECISIÓN
# =============================================================================
btn_dec_sub = widgets.Button(description="AGREGAR SUB-TABLERO", button_style='info', layout=style_btn)
btn_dec_new = widgets.Button(description="OTRO TABLERO PRINCIPAL", button_style='primary', layout=style_btn)
btn_dec_fin = widgets.Button(description="FINALIZAR TODO Y VER REPORTES", button_style='danger', layout=style_btn)

def mostrar_decision():
    with out_main:
        clear_output()
        display(HTML("<h3>✅ TABLERO COMPLETADO. ¿QUÉ SIGUE?</h3>"))
        display(btn_dec_sub)
        display(btn_dec_new)
        display(HTML("<hr>"))
        display(btn_dec_fin)

btn_dec_sub.on_click(lambda b: mostrar_crear_tbt("SUBORDINADO"))
btn_dec_new.on_click(lambda b: mostrar_crear_tbt("PRINCIPAL"))
btn_dec_fin.on_click(lambda b: display(HTML("<h3>🚀 PROCESO FINALIZADO. Ejecuta ModConds.</h3>")))

# =============================================================================
# INICIADOR
# =============================================================================
def iniciar_interfaz():
    display(out_main) # <--- ESTA LÍNEA ES LA QUE HACE QUE SE VEA
    mostrar_inicio()
