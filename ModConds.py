# ModConds.py - Orquestador y Reporte Final

import backend
import IngCargas

def generar_reporte_tablero():
    print("--- INICIANDO CÁLCULOS DEL TABLERO ---")
    
    # 1. Obtener los datos ingresados
    # Asumimos que IngCargas tiene una lista llamada 'lista_de_cargas'
    datos_cargas = IngCargas.lista_de_cargas
    
    resultados_reporte = []

    # 2. Procesar cada carga con el backend
    for carga in datos_cargas:
        # Supongamos que backend tiene una función llamada 'realizar_calculos'
        resultado = backend.realizar_calculos(carga)
        resultados_reporte.append(resultado)

    # 3. Visualizar el reporte consolidado
    print("\n========================================")
    print("REPORTE FINAL DE CARGAS DEL TABLERO")
    print("========================================")
    
    for indice, reporte in enumerate(resultados_reporte, 1):
        print(f"Carga {indice}: {reporte}")
    
    print("========================================\n")

if __name__ == "__main__":
    generar_reporte_tablero()
