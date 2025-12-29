CONTEXTO MAESTRO: HERRAMIENTA DE DISEÑO ELÉCTRICO MODULAR
Objetivo: Desarrollar una aplicación en Python (Google Colab + GitHub) para cálculos de ingeniería eléctrica (Conductores y Transformadores).

Arquitectura:

Repositorio GitHub: DNC-MC-DinaT_58_0 (Público).

Modularidad:

lanzador.ipynb: Notebook de Colab que clona el repo y conecta librerías.

backend.py: Lógica matemática, base de datos de cables y clases (Tablero, Circuito, Transformador).

IngCargas.py: Interfaz gráfica (Frontend) tipo "Wizard" (paso a paso) para ingreso de datos.

ModConds.py: Módulo de reporte que genera tabla de resultados de conductores.

Especificaciones Técnicas (Logradas hasta ahora):

A. Backend (backend.py):

Base de Datos: Tablas de ampacidad para Cobre y Aluminio (75°C) desde calibre 12 AWG hasta 1000 kcmil.

Instalaciones Soportadas: Ducto, Aire Libre, Agrupado, Bandeja, Banco de Ductos, Red Trenzada.

Clase Circuito: Calcula corriente nominal, caída de tensión (ley de ohm AC) y selecciona calibre automáticamente (criterio de ampacidad + regulación < 3%).

Lógica de Optimización: Si el usuario elige un cable muy grueso, lo respeta. Si elige uno muy delgado, el sistema lo corrige al óptimo.

B. Interfaz de Ingreso (IngCargas.py):

Estilo: Diseño horizontal "Full Width" (ancho completo) para evitar inputs pequeños.

Flujo (Wizard):

Nombre Proyecto -> Limpieza de memoria.

Creación de Tablero (Nombre, Tensión).

Ingreso de Cargas (Loop: Tag, Desc, kW, Fases, Longitud, Tipo Instalación).

Decisión Final: ¿Crear Sub-Tablero (aguas abajo)?, ¿Crear otro Tablero Principal?, ¿Finalizar?

C. Reportes (ModConds.py):

Usa Pandas para mostrar una tabla limpia con: TAG, Descripción, kW, I_Nom, Calibre seleccionado, Hilos, %Regulación y Notas.

Instrucción para la IA: Si pego este contexto, asume que tengo estos archivos y ayúdame a modificar o agregar nuevas funcionalidades manteniendo esta estructura modular y respetando la lógica de "Wizard" secuencial.

[FIN DE COPIA]
