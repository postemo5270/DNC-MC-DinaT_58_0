import backend
import IngCargas
import importlib

def main():
    # Recargamos dependencias internas para asegurar datos frescos
    importlib.reload(backend)
    importlib.reload(IngCargas)
    
    # Supongamos que tus datos están en IngCargas.datos
    datos = IngCargas.datos 
    
    print("--- Generando Reporte del Tablero ---")
    # Aquí va tu lógica de backend.py
    for carga in datos:
        resultado = backend.calcular(carga)
        print(f"Resultado: {resultado}")

if __name__ == "__main__":
    main()
