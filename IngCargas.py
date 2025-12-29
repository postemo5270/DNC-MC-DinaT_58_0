import ipywidgets as widgets
from IPython.display import display, clear_output
import backend

# =============================================================================
# INTERFAZ DE INGRESO DE CARGAS (V5 - FLUJO SECUENCIAL / WIZARD)
# =============================================================================

# --- VARIABLES DE ESTADO (MEMORIA TEMPORAL DE LA SESIÓN) ---
sesion_actual = {
    "proyecto": "",
    "tbt_actual": None,  # Objeto Tablero actual
    "tipo_tbt_actual": "PRINCIPAL" # PRINCIPAL o SUBORDINADO
}

# --- WIDGETS COMUNES (REUTILIZABLES) ---
estilo_btn = widgets.Layout(width='200px', margin='5px')
estilo_input = widgets.Layout(width='auto', flex='1 1 auto')

out_main = widgets.Output() # Aquí se renderizará cada "Pantalla"

# =============================================================================
# PANTALLA 1: INICIO PROYECTO
# =============================================================================
txt_proy_nombre = widgets.Text(description="Proyecto:", placeholder="Nombre del Proyecto", layout=estilo_input)
btn_proy_iniciar = widgets.Button(description="INICIAR PROYECTO", button_style='primary', layout=estilo_btn)

def mostrar_inicio():
    with out_main:
        clear_output()
        display(widgets.HTML("<h3>1️⃣ CONFIGURACIÓN DE PROYECTO</h3>"))
        display(widgets.HBox([txt_proy_nombre, btn_proy_iniciar]))

def on_click_iniciar_proy(b):
    if not txt_proy_nombre.value: return
    # Reset del Backend
    backend.SISTEMA_PROYECTO.circuitos = []
    backend.SISTEMA_PROYECTO.sub_tableros = []
    backend.SISTEMA_PROYECTO.nombre = txt_proy_nombre.value
    
    sesion_actual["proyecto"] = txt_proy_nombre.value
    # Pasamos a crear el primer TBT Principal
    mostrar_crear_tbt(tipo="PRINCIPAL")

btn_proy_iniciar.on_click(on_click_iniciar_proy)

# =============================================================================
# PANTALLA 2: CREAR TABLERO (TBT)
# =============================================================================
txt_tbt_nombre = widgets.Text(description="Nombre TBT:", placeholder="Ej: TBT-Principal", layout=estilo_input)
drop_tbt_volt = widgets.Dropdown(options=[480, 440, 220, 208], description="Tensión (V):", value=480, layout=widgets.Layout(width='150px'))
btn_crear_tbt = widgets.Button(description="CREAR TBT E IR A CARGAS", button_style='success', layout=widgets.Layout(width='250px'))

def mostrar_crear_tbt(tipo="PRINCIPAL"):
    # Limpiamos inputs previos
    txt_tbt_nombre.value = ""
    sesion_actual["tipo_tbt_actual"] = tipo
    
    titulo = "2️⃣ CREAR TABLERO PRINCIPAL" if tipo == "PRINCIPAL" else "4️⃣ CREAR TABLERO SUBORDINADO (AGUAS ABAJO)"
    estilo_titulo = "color: darkblue;" if tipo == "PRINCIPAL" else "color: darkred;"
    
    with out_main:
        clear_output()
        display(widgets.HTML(f"<h3 style='{estilo_titulo}'>{titulo}</h3>"))
        if tipo == "SUBORDINADO":
            display(widgets.HTML(f"<i>Dependerá de: {sesion_actual['tbt_actual'].nombre if sesion_actual['tbt_actual'] else 'N/A'}</i>"))
            
        display(widgets.HBox([txt_tbt_nombre, drop_tbt_volt]))
        display(btn_crear_tbt)

def on_click_crear_tbt(b):
    if not txt_tbt_nombre.value: return
    
    # Creamos objeto Tablero (aunque el backend actual centraliza todo, simulamos la estructura)
    nuevo_tbt = backend.Tablero(txt_tbt_nombre.value, drop_tbt_volt.value, 3)
    sesion_actual["tbt_actual"] = nuevo_tbt
    
    # Nota: En esta versión simplificada, guardamos las cargas en la lista global
    # pero les pondremos un prefijo o nota para saber de qué TBT son.
    
    mostrar_ingreso_cargas()

btn_crear_tbt.on_click(on_click_crear_tbt)

# =============================================================================
# PANTALLA 3: INGRESO DE CARGAS (BUCLE)
# =============================================================================
# Widgets de Carga
txt_c_tag = widgets.Text(description="TAG:", layout=widgets.Layout(width='120px'))
txt_c_desc = widgets.Text(description="Desc:", layout=estilo_input)
num_c_kw = widgets.FloatText(description="Pot (kW):", layout=widgets.Layout(width='150px'))
drop_c_fases = widgets.Dropdown(options=[3, 2, 1], description="Fases:", value=3, layout=widgets.Layout(width='100px'))
num_c_long = widgets.FloatText(description="Long (m):", value=10, layout=widgets.Layout(width='120px'))
drop_c_cal = widgets.Dropdown(options=backend.ORDEN_CALIBRES, description="Calibre:", value="12", layout=widgets.Layout(width='100px'))
drop_c_mat = widgets.Dropdown(options=["CU", "AL"], description="Mat:", value="CU", layout=widgets.Layout(width='80px'))
drop_c_inst = widgets.Dropdown(options=[("Ducto", backend.TipoInstalacion.DUCTO), ("Aire", backend.TipoInstalacion.AIRE)], value=backend.TipoInstalacion.DUCTO, layout=widgets.Layout(width='100px'))

btn_add_otra = widgets.Button(description="GUARDAR Y AGREGAR OTRA", button_style='info', icon='plus')
btn_terminar_tbt = widgets.Button(description="TERMINAR ESTE TBT", button_style='warning', icon='check')
out_lista_cargas = widgets.Output()

def mostrar_ingreso_cargas():
    tbt = sesion_actual["tbt_actual"]
    
    with out_main:
        clear_output()
        display(widgets.HTML(f"<h3>3️⃣ INGRESANDO CARGAS A: <span style='color:blue'>{tbt.nombre} ({tbt.voltaje}V)</span></h3>"))
        
        # Fila 1
        display(widgets.HBox([txt_c_tag, txt_c_desc, num_c_kw]))
        # Fila 2
        display(widgets.HBox([drop_c_fases, num_c_long, drop_c_cal, drop_c_mat, drop_c_inst]))
        # Botones de Acción
        display(widgets.HBox([btn_add_otra, btn_terminar_tbt]))
        
        display(widgets.HTML("<hr><b>Cargas agregadas en esta sesión:</b>"))
        display(out_lista_cargas)

def procesar_carga():
    # Lógica de guardado
    if num_c_kw.value <= 0: return False
    
    tbt = sesion_actual["tbt_actual"]
    
    nueva_c = backend.Circuito(
        tag=txt_c_tag.value,
        descripcion=f"[{tbt.nombre}] {txt_c_desc.value}", # Identificamos el TBT en la descripción
        potencia_nominal_kw=num_c_kw.value,
        voltaje=tbt.voltaje,
        fases=drop_c_fases.value,
        factor_potencia=0.9,
        tipo_operacion=backend.TipoOperacion.CONTINUA,
        longitud_mts=num_c_long.value,
        calibre_usuario=drop_c_cal.value,
        material_conductor=drop_c_mat.value,
        tipo_instalacion=drop_c_inst.value
    )
    
    backend.SISTEMA_PROYECTO.agregar_c(nueva_c)
    res = nueva_c.ejecutar_seleccion_conductor()
    
    with out_lista_cargas:
        print(f"✅ {nueva_c.tag} ({num_c_kw.value}kW) -> {res['N']}x{res['Calibre']} {res['Mat']}")
    
    # Limpiar campos clave
    txt_c_tag.value = ""
    txt_c_desc.value = ""
    num_c_kw.value = 0.0
    return True

def on_click_otra(b):
    if procesar_carga():
        pass # Se queda en la misma pantalla

def on_click_terminar(b):
    # Procesar la última si hay datos escritos, si no, solo avanzar
    if num_c_kw.value > 0:
        procesar_carga()
    
    # Limpiar output de lista para la proxima
    out_lista_cargas.clear_output()
    mostrar_decisiones()

btn_add_otra.on_click(on_click_otra)
btn_terminar_tbt.on_click(on_click_terminar)

# =============================================================================
# PANTALLA 4: DECISIONES DE FLUJO
# =============================================================================
btn_dec_sub = widgets.Button(description="AGREGAR SUB-TABLERO", button_style='info', layout=estilo_btn)
btn_dec_new = widgets.Button(description="OTRO TBT PRINCIPAL", button_style='primary', layout=estilo_btn)
btn_dec_fin = widgets.Button(description="FINALIZAR TODO", button_style='danger', layout=estilo_btn)

def mostrar_decisiones():
    tbt = sesion_actual["tbt_actual"]
    with out_main:
        clear_output()
        display(widgets.HTML(f"<h3>🤔 ¿QUÉ DESEAS HACER AHORA?</h3>"))
        display(widgets.HTML(f"Acabas de terminar con el tablero: <b>{tbt.nombre}</b>"))
        
        display(widgets.VBox([
            widgets.Label(f"Opción A: Crear un tablero alimentado desde {tbt.nombre} (Aguas abajo)"),
            btn_dec_sub,
            widgets.HTML("<br>"),
            widgets.Label(f"Opción B: Crear un tablero totalmente nuevo e independiente"),
            btn_dec_new,
            widgets.HTML("<br>"),
            widgets.Label(f"Opción C: Terminar y ver reportes"),
            btn_dec_fin
        ]))

def ir_a_sub(b): mostrar_crear_tbt(tipo="SUBORDINADO")
def ir_a_new(b): mostrar_crear_tbt(tipo="PRINCIPAL")
def ir_a_fin(b):
    with out_main:
        clear_output()
        display(widgets.HTML("<h3>✅ INGRESO DE DATOS FINALIZADO</h3>"))
        display(widgets.HTML("Ahora puedes ejecutar el módulo <b>ModConds</b> para ver los cálculos."))

btn_dec_sub.on_click(ir_a_sub)
btn_dec_new.on_click(ir_a_new)
btn_dec_fin.on_click(ir_a_fin)

# =============================================================================
# FUNCIÓN DE LANZAMIENTO
# =============================================================================
def iniciar_interfaz():
    mostrar_inicio()
    display(out_main)
    
    display(widgets.HTML("<hr><b>Historial:</b>"))
    display(out_tabla)
