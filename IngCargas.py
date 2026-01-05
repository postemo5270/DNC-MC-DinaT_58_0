import ipywidgets as widgets
from IPython.display import display, clear_output
import json
import backend

# Estado global
datos_proyecto = {
    "nombre": "",
    "tablero": {},
    "cargas": []
}

def crear_titulo(texto):
    return widgets.HTML(f"<h3><b style='color:#2c3e50'>{texto}</b></h3>")

def crear_fila(widgets_list):
    return widgets.HBox(widgets_list, layout=widgets.Layout(margin='5px 0px'))

def guardar_datos_json():
    """Función que asegura el almacenamiento físico de los datos"""
    with open('proyecto_actual.json', 'w', encoding='utf-8') as f:
        json.dump(datos_proyecto, f, indent=4, ensure_ascii=False)
    print("\n✅ DATOS GUARDADOS EN 'proyecto_actual.json'.")

def mostrar_formulario_cargas(out_principal):
    out_principal.clear_output()
    with out_principal:
        num_carga = len(datos_proyecto['cargas']) + 1
        display(crear_titulo(f"3. Ingreso de Carga #{num_carga}"))
        
        w_tag = widgets.Text(description="Tag:", placeholder="Ej: M-101")
        w_potencia = widgets.FloatText(description="Potencia:")
        w_unidad = widgets.Dropdown(options=backend.LISTA_UNIDADES_POT, description="Unidad:")
        
        btn_guardar = widgets.Button(description="Guardar Carga", button_style='success')
        btn_finalizar = widgets.Button(description="Finalizar y Guardar", button_style='warning')

        display(widgets.VBox([crear_fila([w_tag]), crear_fila([w_potencia, w_unidad]), crear_fila([btn_guardar, btn_finalizar])]))

        def on_guardar(b):
            nueva_carga = {
                "id": len(datos_proyecto['cargas']) + 1, 
                "tag": w_tag.value, 
                "potencia": w_potencia.value, 
                "unidad": w_unidad.value,
                "fp": 0.85, # Valores por defecto si no se capturan
                "eff": 0.90
            }
            datos_proyecto['cargas'].append(nueva_carga)
            mostrar_formulario_cargas(out_principal)

        def on_finalizar(b):
            out_principal.clear_output()
            with out_principal:
                guardar_datos_json()
                display(crear_titulo("SISTEMA LISTO PARA MODCONDS"))

        btn_guardar.on_click(on_guardar)
        btn_finalizar.on_click(on_finalizar)

def mostrar_config_tablero(out_principal):
    out_principal.clear_output()
    with out_principal:
        display(crear_titulo("2. Configuración Tablero"))
        w_tag = widgets.Text(description="Tag Tablero:", value="T-Gral")
        w_tension = widgets.Dropdown(options=backend.LISTA_TENSION, description="Tensión (V):")
        btn_siguiente = widgets.Button(description="Siguiente", button_style='primary')
        display(widgets.VBox([w_tag, w_tension, btn_siguiente]))

        def on_siguiente(b):
            datos_proyecto['tablero'] = {"tag": w_tag.value, "tension": w_tension.value}
            mostrar_formulario_cargas(out_principal)
        btn_siguiente.on_click(on_siguiente)

def main():
    out_principal = widgets.Output()
    display(out_principal)
    with out_principal:
        display(crear_titulo("1. Nuevo Proyecto"))
        w_nombre = widgets.Text(description="Proyecto:")
        btn_crear = widgets.Button(description="Crear Proyecto", button_style='info')
        display(widgets.HBox([w_nombre, btn_crear]))

        def on_crear(b):
            datos_proyecto['nombre'] = w_nombre.value
            mostrar_config_tablero(out_principal)
        btn_crear.on_click(on_crear)

if __name__ == "__main__":
    main()
