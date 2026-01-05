import ipywidgets as widgets
from IPython.display import display, clear_output
import backend

# 1. ESTADO GLOBAL (Al principio para que todos lo vean)
datos_proyecto = {
    "nombre": "",
    "tablero": {},
    "cargas": []
}

# 2. UTILIDADES DE UI
def crear_titulo(texto):
    return widgets.HTML(f"<h3><b style='color:#2c3e50'>{texto}</b></h3>")

def crear_fila(widgets_list):
    return widgets.HBox(widgets_list, layout=widgets.Layout(margin='5px 0px'))

# 3. PANTALLA DE CARGAS
def mostrar_formulario_cargas(out_principal):
    out_principal.clear_output()
    with out_principal:
        num_carga = len(datos_proyecto['cargas']) + 1
        display(crear_titulo(f"3. Ingreso de Carga #{num_carga}"))
        
        w_tag = widgets.Text(description="Tag:", placeholder="Ej: M-101", layout=widgets.Layout(width='30%'))
        w_desc = widgets.Text(description="Desc:", placeholder="Descripción funcional", layout=widgets.Layout(width='65%'))
        w_potencia = widgets.FloatText(description="Potencia:", layout=widgets.Layout(width='200px'))
        w_unidad = widgets.Dropdown(options=backend.LISTA_UNIDADES_POT, description="Unidad:", layout=widgets.Layout(width='180px'))
        w_fp = widgets.BoundedFloatText(value=0.85, min=0.1, max=1.0, step=0.01, description="F.P.:", layout=widgets.Layout(width='150px'))
        w_eff = widgets.BoundedFloatText(value=0.90, min=0.1, max=1.0, step=0.01, description="Eficiencia:", layout=widgets.Layout(width='150px'))
        w_instalacion = widgets.Dropdown(options=backend.LISTA_INSTALACION, description="Tipo Inst.:", layout=widgets.Layout(width='300px'))
        w_mat_ducto = widgets.Dropdown(options=backend.LISTA_MAT_CANALIZACION, description="Mat. Ducto:", layout=widgets.Layout(width='300px'), disabled=True)
        w_temp = widgets.IntSlider(value=30, min=10, max=60, description="T. Amb (°C):")
        w_mat_cond = widgets.Dropdown(options=backend.LISTA_MAT_CONDUCTOR, description="Material:", layout=widgets.Layout(width='220px'))
        w_aislam = widgets.Dropdown(options=backend.LISTA_AISLAMIENTO, description="Aislam.:", layout=widgets.Layout(width='200px'))
        w_temp_aisl = widgets.Dropdown(options=backend.LISTA_TEMP_AISLAMIENTO, description="T. Cable:", layout=widgets.Layout(width='180px'))
        w_long = widgets.FloatText(description="Longitud (m):", layout=widgets.Layout(width='200px'))

        def on_change_instalacion(change):
            w_mat_ducto.disabled = not backend.validar_requerimiento_magnetico(change['new'])
        w_instalacion.observe(on_change_instalacion, names='value')

        btn_guardar = widgets.Button(description="Guardar Carga", button_style='success', icon='check')
        btn_finalizar = widgets.Button(description="Finalizar Ingreso", button_style='warning', icon='stop')

        display(widgets.VBox([
            crear_fila([w_tag, w_desc]),
            crear_fila([w_potencia, w_unidad, w_fp, w_eff]),
            crear_fila([w_instalacion, w_mat_ducto]),
            crear_fila([w_temp, w_long]),
            crear_fila([w_mat_cond, w_aislam, w_temp_aisl]),
            crear_fila([btn_guardar, btn_finalizar])
        ]))

        def on_guardar(b):
            nueva_carga = {
                "id": len(datos_proyecto['cargas']) + 1,
                "tag": w_tag.value,
                "potencia": w_potencia.value,
                "unidad": w_unidad.value,
                "tipo_inst": w_instalacion.value,
                "mat_ducto": w_mat_ducto.value if not w_mat_ducto.disabled else "N/A",
                "longitud": w_long.value
            }
            datos_proyecto['cargas'].append(nueva_carga)
            mostrar_formulario_cargas(out_principal)

        def on_finalizar(b):
            out_principal.clear_output()
            with out_principal:
                display(crear_titulo("✅ INGRESO COMPLETADO"))
                print(f"Cargas en memoria: {len(datos_proyecto['cargas'])}")

        btn_guardar.on_click(on_guardar)
        btn_finalizar.on_click(on_finalizar)

# 4. PANTALLA DE TABLERO
def mostrar_config_tablero(out_principal):
    out_principal.clear_output()
    with out_principal:
        display(crear_titulo("2. Configuración Tablero"))
        w_tag = widgets.Text(description="Tag Tablero:", value="T-Gral")
        w_tension = widgets.Dropdown(options=backend.LISTA_TENSION, description="Tensión (V):")
        btn_crear = widgets.Button(description="Siguiente", button_style='primary')
        display(widgets.VBox([w_tag, w_tension, btn_crear]))

        def on_crear(b):
            datos_proyecto['tablero'] = {"tag": w_tag.value, "tension": w_tension.value}
            mostrar_formulario_cargas(out_principal)
        btn_crear.on_click(on_crear)

# 5. FUNCIÓN PRINCIPAL
def main():
    out_principal = widgets.Output()
    display(out_principal)
    with out_principal:
        display(crear_titulo("1. Nuevo Proyecto"))
        w_nombre = widgets.Text(description="Proyecto:")
        btn_inicio = widgets.Button(description="Crear", button_style='info')
        display(widgets.HBox([w_nombre, btn_inicio]))

        def on_inicio(b):
            if w_nombre.value:
                datos_proyecto['nombre'] = w_nombre.value
                mostrar_config_tablero(out_principal)
        btn_inicio.on_click(on_inicio)
    return datos_proyecto
    
    # EL PUENTE: Retorna el objeto para que ModConds pueda usarlo
    return datos_proyecto
