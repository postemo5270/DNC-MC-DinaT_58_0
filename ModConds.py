import backend
import IngCargas
import importlib
import ipywidgets as widgets
from IPython.display import display

def generar_reporte_final(proyecto):
    """Esta función es la que hace los cálculos y muestra el reporte"""
    if not proyecto['cargas']:
        print("\n⚠️ No hay cargas para procesar.")
        return

    print("\n" + "="*60)
    print(f"REPORTE TÉCNICO DE INGENIERÍA: {proyecto['nombre'].upper()}")
    print(f"TABLERO: {proyecto['tablero'].get('tag')} | {proyecto['tablero'].get('tension')}V")
    print("="*60)

    for c in proyecto['cargas']:
        # Aquí llamas a tu backend real
        # Ejemplo: corriente = backend.calcular_corriente(c)
        print(f"\n[TAG: {c['tag']}]")
        print(f"Potencia: {c['potencia']} {c['unidad']} | Inst: {c['tipo_inst']}")
        print(f"Longitud: {c['longitud']}m | Ducto: {c['mat_ducto']}")
        print("-" * 40)
    
    print("\n>>> FIN DEL REPORTE <<<")

def main():
    importlib.reload(backend)
    importlib.reload(IngCargas)
    
    # 1. Lanza la interfaz y captura los datos
    proyecto = IngCargas.main()
    
    # 2. Creamos un botón exclusivo en ModConds para generar el reporte
    # Esto evita que el código siga de largo sin esperar a que llenes los datos
    btn_reporte = widgets.Button(
        description="GENERAR REPORTE", 
        button_style='danger', 
        icon='file-text',
        layout=widgets.Layout(width='300px', height='50px', margin='20px 0px')
    )
    
    output_reporte = widgets.Output()

    def on_click_reporte(b):
        with output_reporte:
            output_reporte.clear_output()
            generar_reporte_final(proyecto)

    btn_reporte.on_click(on_click_reporte)
    
    # Mostramos el botón debajo de la interfaz de IngCargas
    display(btn_reporte, output_reporte)

if __name__ == "__main__":
    main()
