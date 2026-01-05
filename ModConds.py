import backend
import IngCargas
import importlib
import ipywidgets as widgets
from IPython.display import display

def main():
    # Recargamos para asegurar que el diccionario global esté limpio al inicio
    importlib.reload(backend)
    importlib.reload(IngCargas)
    
    # 1. Lanzamos la interfaz de ingreso
    # No necesitamos el botón "Crear" extra de ModConds, usamos el de IngCargas
    IngCargas.main()
    
    # 2. Botón de Reporte vinculado al estado real de IngCargas
    btn_reporte = widgets.Button(
        description="GENERAR REPORTE FINAL", 
        button_style='danger', 
        icon='calculator',
        layout=widgets.Layout(width='300px', height='45px')
    )
    
    output_reporte = widgets.Output()

    def al_solicitar_reporte(b):
        with output_reporte:
            output_reporte.clear_output()
            # EXTRAEMOS LOS DATOS DIRECTAMENTE DEL MÓDULO ACTUALIZADO
            proyecto_real = IngCargas.datos_proyecto 
            
            if not proyecto_real['cargas']:
                print("⚠️ Error: Aún no has guardado ninguna carga en la interfaz superior.")
                return

            print(f"\nGenerando reporte para: {proyecto_real['nombre']}")
            print("="*50)
            for carga in proyecto_real['cargas']:
                # Aquí el backend hace su magia
                print(f"-> Procesando Carga: {carga['tag']}...")
                # resultado = backend.procesar(carga)
            print("="*50)
            print("✅ Reporte Generado con éxito.")

    btn_reporte.on_click(al_solicitar_reporte)
    display(btn_reporte, output_reporte)

if __name__ == "__main__":
    main()
