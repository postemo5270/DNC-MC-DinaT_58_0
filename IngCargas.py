import backend
import os

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_titulo(texto):
    print("\n" + "="*50)
    print(f" {texto}")
    print("="*50)

def obtener_opcion_lista(mensaje, lista_opciones):
    """Ayuda para seleccionar de las listas definidas en backend"""
    print(f"\n{mensaje}")
    for i, opcion in enumerate(lista_opciones, 1):
        print(f"{i}. {opcion}")
    
    while True:
        try:
            seleccion = int(input("Seleccione una opción (#): "))
            if 1 <= seleccion <= len(lista_opciones):
                return lista_opciones[seleccion - 1]
            print("Opción inválida.")
        except ValueError:
            print("Por favor ingrese un número.")

def input_float(mensaje, min_val=0.0, max_val=float('inf')):
    while True:
        try:
            val = float(input(mensaje))
            if min_val <= val <= max_val:
                return val
            print(f"Valor fuera de rango ({min_val}-{max_val})")
        except ValueError:
            print("Dato numérico requerido.")

# --- FLUJO PRINCIPAL ---

def main():
    limpiar_pantalla()
    datos_proyecto = {}
    
    # 1. FORMULARIO DE PROYECTO [cite: 1, 2]
    mostrar_titulo("1. NUEVO PROYECTO MC-ELE")
    nombre_proyecto = input("Ingrese Nombre del Proyecto: ")
    input("\n[ Presione ENTER para CREAR PROYECTO ]") # Botón simulado
    
    datos_proyecto['nombre'] = nombre_proyecto
    datos_proyecto['cargas'] = []

    # 2. FORMULARIO TABLERO PRINCIPAL [cite: 35, 36]
    limpiar_pantalla()
    mostrar_titulo(f"2. CONFIGURACIÓN TABLERO PRINCIPAL - {nombre_proyecto}")
    
    tablero = {}
    tablero['tag'] = input("Tag del Tablero (Ej: T-Gral): ")
    tablero['descripcion'] = input("Descripción: ")
    
    # Selecciones usando listas del backend [cite: 37]
    tablero['tension'] = obtener_opcion_lista("Nivel de Tensión (V):", backend.LISTA_TENSION)
    tablero['fases'] = obtener_opcion_lista("Configuración de Fases:", backend.LISTA_FASES)
    
    # Neutro (Lógica Sí/No)
    req_neutro = obtener_opcion_lista("¿Requiere Neutro?", ["SI", "NO"])
    tablero['neutro'] = req_neutro
    
    datos_proyecto['tablero_principal'] = tablero
    print("\n>>> Tablero Configurado Exitosamente.")
    
    # 3. INGRESO DE CARGAS (Loop 1 a n) [cite: 3]
    contador_cargas = 1
    limpiar_pantalla()
    
    while contador_cargas <= 50:
        mostrar_titulo(f"3. INGRESO DE CARGA #{contador_cargas} (Máx 50)")
        print(f"Tablero Padre: {tablero['tag']} ({tablero['tension']}V)")
        
        carga = {}
        # Datos Básicos
        carga['id'] = contador_cargas
        carga['tag'] = input("\nTag de Carga (Ej: M-101): ")
        if carga['tag'].lower() == 'salir': break # Salida de emergencia
        
        carga['descripcion'] = input("Descripción Funcional: ")
        
        # Datos de Potencia [cite: 38, 39]
        carga['potencia_input'] = input_float("Potencia (Valor numérico): ")
        carga['unidad'] = obtener_opcion_lista("Unidad:", backend.LISTA_UNIDADES_POT)
        carga['fp'] = input_float("Factor de Potencia (0.0 - 1.0): ", 0.0, 1.0)
        carga['eficiencia'] = input_float("Eficiencia (0.0 - 1.0): ", 0.0, 1.0)
        
        # Cálculo inmediato para feedback visual (Backend logic)
        kva = backend.calcular_kva_entrada(carga['potencia_input'], carga['unidad'], carga['eficiencia'], carga['fp'])
        amp = backend.calcular_corriente_nominal(kva, tablero['tension'], tablero['fases'])
        print(f"\n--- Pre-cálculo: {kva:.2f} kVA | {amp:.2f} A ---")
        
        # Datos de Instalación [cite: 41, 43]
        carga['t_ambiente'] = input_float("Temperatura Ambiente (°C): ")
        carga['tipo_instalacion'] = obtener_opcion_lista("Tipo de Instalación:", backend.LISTA_INSTALACION)
        
        # Condicional Material Canalización 
        if backend.validar_requerimiento_magnetico(carga['tipo_instalacion']):
            carga['mat_ducto'] = obtener_opcion_lista("Material Ducto:", backend.LISTA_MAT_CANALIZACION)
        else:
            carga['mat_ducto'] = "N/A"
            
        # Datos Conductor [cite: 46, 47]
        carga['mat_conductor'] = obtener_opcion_lista("Material Conductor:", backend.LISTA_MAT_CONDUCTOR)
        carga['tipo_aislamiento'] = obtener_opcion_lista("Tipo Aislamiento:", backend.LISTA_AISLAMIENTO)
        carga['temp_aisl_cable'] = obtener_opcion_lista("Temp. Aislamiento Cable (°C):", backend.LISTA_TEMP_AISLAMIENTO)
        
        # Longitud para caída de tensión [cite: 59]
        carga['longitud'] = input_float("Longitud del circuito (m): ")
        
        # Guardar
        datos_proyecto['cargas'].append(carga)
        print(f"\n>>> Carga {carga['tag']} guardada.")
        
        continuar = input("\n¿Ingresar otra carga? (S/N): ").upper()
        if continuar != "S":
            break
            
        contador_cargas += 1
        limpiar_pantalla()

    # Resumen Final
    limpiar_pantalla()
    mostrar_titulo("RESUMEN DE INGENIERÍA")
    print(f"Proyecto: {datos_proyecto['nombre']}")
    print(f"Tablero: {datos_proyecto['tablero_principal']['tag']} - {datos_proyecto['tablero_principal']['tension']}V")
    print(f"Total Cargas Ingresadas: {len(datos_proyecto['cargas'])}")
    
    # Aquí se podría exportar a JSON/Excel
    print("\nDatos listos para procesamiento en Motor de Cálculo.")

if __name__ == "__main__":
    main()
