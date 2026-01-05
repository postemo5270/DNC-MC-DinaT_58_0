import ipywidgets as widgets
from IPython.display import display, clear_output
import backend

# --- ESTADO GLOBAL DEL PROYECTO ---
datos_proyecto = {
    "nombre": "",
    "tablero": {},
    "cargas": []
}

# --- UTILIDADES DE UI ---
def crear_titulo(texto):
    return widgets.HTML(f"<h3><b style='color:#2c3e50'>{texto}</b></h3>")

def crear_fila(widgets_list):
    """Organiza widgets en una fila horizontal para ahorrar espacio"""
    return widgets.HBox(widgets_list, layout=widgets.Layout(margin='5px 0px'))

# --- PANTALLA 3: INGRESO DE CARGAS (RECURSIVA) ---
def mostrar_formulario_cargas(out_principal):
    out_principal.clear_output()
    
    with out_principal:
        num_carga = len(datos_proyecto['cargas']) + 1
        display(crear_titulo(f"3. Ingreso de Carga #{num_carga}"))
        
        # --- SECCIÓN A: IDENTIFICACIÓN ---
        w_tag = widgets.Text(description="Tag:", placeholder="Ej: M-101", layout=widgets.Layout(width='30%'))
        w_desc = widgets.Text(description="Desc:", placeholder="Descripción funcional", layout=widgets.Layout(width='65%'))
        
        # --- SECCIÓN B: POTENCIA ---
        w_potencia = widgets.FloatText(description="Potencia:", layout=widgets.Layout(width='200px'))
        w_unidad = widgets.Dropdown(options=backend.LISTA_UNIDADES_POT, description="Unidad:", layout=widgets.Layout(width='180px'))
        w_fp = widgets.BoundedFloatText(value=0.85, min=0.1, max=1.0, step=0.01, description="F.P.:", layout=widgets.Layout(width='150px'))
        w_eff = widgets.BoundedFloatText(value=0.90, min=0.1, max=1.0, step=0.01, description="Eficiencia:", layout=widgets.Layout(width='150px'))
        
        # --- SECCIÓN C: INSTALACIÓN ---
        w_instalacion = widgets.Dropdown(options=backend.LISTA_INSTALACION, description="Tipo Inst.:", layout=widgets.Layout(width='300px'))
        w_mat_ducto = widgets.Dropdown(options=backend.LISTA_MAT_CANALIZACION, description="Mat. Ducto:", layout=widgets.Layout(width='300px'), disabled=True)
        w_temp = widgets.IntSlider(value=30, min=10, max=60, description="T. Amb (°C):")

        def on_change_instalacion(change):
            if backend.validar_requerimiento_magnetico(change['new']):
                w_mat_ducto.disabled = False
            else:
                w_mat_ducto.disabled = True
                w_mat_ducto.value = None
        
        w_instalacion.observe(on_change_instalacion, names='value')

        # --- SECCIÓN D: CONDUCTOR ---
        w_mat_cond = widgets.Dropdown(options=backend.LISTA_MAT_CONDUCTOR, description="Material:", layout=widgets.Layout(width='220px'))
        w_aislam = widgets.Dropdown(options=backend.LISTA_AISLAMIENTO, description="Aislam.:", layout=widgets.Layout(width='200px'))
        w_temp_aisl = widgets.Dropdown(options=backend.LISTA_TEMP_AISLAMIENTO, description="T. Cable:", layout=widgets.Layout(width='180px'))
        w_long = widgets.FloatText(description="Longitud (m):", layout=widgets.Layout(width='200px'))

        # --- BOTONES DE ACCIÓN ---
        btn_guardar = widgets.Button(description="Guardar Carga", button_style='success', icon='check')
        btn_finalizar = widgets.Button(description="Finalizar Ingreso", button_style='warning', icon='stop')

        form_ui = widgets.VBox([
            crear_fila([w_tag, w_desc]),
            widgets.HTML("<b>Datos Eléctricos:</b>"),
            crear_fila([w_potencia, w_unidad, w_fp, w_eff]),
            widgets.HTML("<b>Instalación:</b>"),
            crear_fila([w_instalacion, w_mat_ducto]),
            crear_fila([w_temp, w_long]),
            widgets.HTML("<b>Especificación Conductor:</b>"),
            crear_fila([w_mat_cond, w_aislam, w_temp_aisl]),
            widgets.HTML("<hr>"),
            crear_fila([btn_guardar, btn_finalizar])
        ])
        
        display(form_ui)

        def on_guardar(b):
            nueva_carga = {
                "id": len(datos_proyecto['cargas']) + 1,
                "tag": w_tag.value,
                "descripcion": w_desc.value,
                "potencia": w_potencia.value,
                "unidad": w_unidad.value,
                "fp": w_fp.value,
                "eff": w_eff.value,
                "tipo_inst": w_instalacion.value,
                "mat_ducto": w_mat_ducto.value if not w_mat_ducto.disabled else "N/A",
                "temp_amb": w_temp.value,
                "longitud": w_long.value,
                "mat_cond": w_mat_cond.value,
                "tipo_aisl": w_aislam.value,
                "temp_cable": w_temp_aisl.value
            }
            datos_proyecto['cargas'].append(nueva_carga)
            print(f"✅ Carga {w_tag.value} guardada.")
            mostrar_formulario_cargas(out_principal)

        def on_finalizar(b):
            out_principal.clear_output()
            with out_principal:
                display(crear_titulo("DATOS LISTOS"))
                print(f"Cargas procesadas: {len(datos_proyecto['cargas'])}")

        btn_guardar.on_click(on_guardar)
        btn_finalizar.on_click(on_finalizar)

# --- PANTALLA 2 Y 1 --- (Omitidas por espacio, pero mantenlas igual)
# ... [TUS FUNCIONES mostrar_config_tablero() y el resto del archivo] ...

def main():
    out_principal = widgets.Output()
    display(out_principal)
    with out_principal:
        # Aquí inicia tu secuencia de pantallas original
        w_nombre_proy = widgets.Text(description="Proyecto:")
        btn_inicio = widgets.Button(description="Crear Proyecto", button_style='info')
        display(widgets.HBox([w_nombre_proy, btn_inicio]))
        def on_inicio(b):
            datos_proyecto['nombre'] = w_nombre_proy.value
            mostrar_config_tablero(out_principal)
        btn_inicio.on_click(on_inicio)
    
    # EL PUENTE: Retorna el objeto para que ModConds pueda usarlo
    return datos_proyecto
