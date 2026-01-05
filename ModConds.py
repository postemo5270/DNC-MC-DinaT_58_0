import backend
import IngCargas
import importlib

def main():
    # Actualiza los módulos para tomar cambios recientes
    importlib.reload(backend)
    importlib.reload(IngCargas)
    
    # 1. Obtiene los datos ejecutando el ingreso de cargas
    datos = IngCargas.main()
    
    # 2. Validación de seguridad
    if datos is None:
        print("Aviso: No se retornaron datos desde IngCargas.")
        return

    # 3. Procesamiento y Reporte
    print(f"\n--- REPORTE DEL TABLERO ({len(datos)} cargas) ---")
    for carga in datos:
        # Aquí llamas a la función de búsqueda/cálculo de tu backend
        resultado = backend.realizar_busqueda(carga) 
        print(f"Carga: {carga} -> Resultado Backend: {resultado}")

if __name__ == "__main__":
    main()
