import backend
import IngCargas
import importlib

def main():
    # Recarga módulos para limpiar caché de Colab
    importlib.reload(backend)
    importlib.reload(IngCargas)
    
    # Lanza la UI y captura el objeto de datos
    proyecto = IngCargas.main()
    
    # El código de abajo se ejecutará después de que interactúes con la UI
    # pero para ver el reporte final, puedes imprimirlo cuando el usuario termine.
    if not proyecto['cargas']:
        print("Esperando ingreso de cargas en la interfaz...")
        return

    print("\n" + "="*50)
    print(f"REPORTE FINAL: {proyecto['nombre'].upper()}")
    print("="*50)

    for c in proyecto['cargas']:
        # Ejemplo de llamado al backend
        print(f"CARGA: {c['tag']} | POTENCIA: {c['potencia']} {c['unidad']}")
        # Aquí puedes llamar a: backend.tu_funcion_de_calculo(c)
        print("-" * 30)

if __name__ == "__main__":
    main()
