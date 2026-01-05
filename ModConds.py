import backend
import IngCargas
import importlib

def main():
    importlib.reload(backend)
    importlib.reload(IngCargas)
    
    # Captura el estado del proyecto generado por la interfaz
    proyecto = IngCargas.main()
    
    # Validamos si ya hay cargas (esto se imprimirá en Colab)
    if not proyecto['cargas']:
        print("Esperando a que termines de ingresar los datos en la interfaz superior...")
        return

    print("\n" + "="*50)
    print(f"REPORTE DE TABLERO: {proyecto['nombre']}")
    print("="*50)

    for c in proyecto['cargas']:
        # Aquí usas el backend para cada carga ingresada
        # Ejemplo:
        seccion = backend.calcular_seccion(c) 
        print(f"Carga: {c['tag']} | Potencia: {c['potencia']} {c['unidad']}")
        print(f"Resultado Backend: {seccion}")
        print("-" * 30)

if __name__ == "__main__":
    main()
