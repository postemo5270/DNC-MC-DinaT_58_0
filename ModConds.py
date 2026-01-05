import json
import os
import backend
import importlib

def main():
    # Aseguramos que los cálculos del backend estén actualizados
    importlib.reload(backend)
    
    archivo = 'proyecto_actual.json'
    
    if not os.path.exists(archivo):
        print(f"❌ Error: No se encuentra el archivo {archivo}. Ejecuta primero IngCargas.py")
        return

    with open(archivo, 'r', encoding='utf-8') as f:
        datos = json.load(f)

    print("\n" + "="*70)
    print(f"REPORTE TÉCNICO INDEPENDIENTE - PROYECTO: {datos['nombre'].upper()}")
    print(f"TABLERO: {datos['tablero'].get('tag')} | TENSIÓN: {datos['tablero'].get('tension')}V")
    print("="*70)

    if not datos['cargas']:
        print("No hay cargas registradas en el archivo.")
        return

    for carga in datos['cargas']:
        # Aquí se ejecutan las validaciones del backend
        # Supongamos que estas funciones ya existen en tu backend.py
        corriente = backend.calcular_corriente(carga, datos['tablero']['tension'])
        
        print(f"\nCARGA: {carga['tag']}")
        print(f" > Datos: {carga['potencia']} {carga['unidad']} | FP: {carga['fp']}")
        print(f" > Corriente Calculada: {corriente} A")
        print("-" * 40)

    print("\n=== VALIDACIÓN FINALIZADA ===")

if __name__ == "__main__":
    main()
