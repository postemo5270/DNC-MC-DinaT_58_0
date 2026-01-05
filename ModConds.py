import backend
import IngCargas
import importlib

def main():
    # Recargamos para asegurar que lean los últimos cambios
    importlib.reload(backend)
    importlib.reload(IngCargas)
    
    # Ejecutamos IngCargas y guardamos lo que retorna
    # Asumiendo que IngCargas.main() devuelve la lista/diccionario de datos
    datos_obtenidos = IngCargas.main()
    
    print("--- GENERANDO REPORTE DEL TABLERO ---")
    
    # Aquí es donde ModConds procesa los datos con el backend
    # Ajusta esta parte según lo que necesites visualizar
    print(f"Procesando {len(datos_obtenidos)} elementos...")
    
    # Ejemplo de salida
    for item in datos_obtenidos:
        # Aquí llamarías a tus funciones de backend.py
        print(f"Reporte para: {item}")

if __name__ == "__main__":
    main()
