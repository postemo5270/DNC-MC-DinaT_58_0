from fpdf import FPDF
import backend
import datetime

class PDFReport(FPDF):
    def header(self):
        # Marco del encabezado
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'MEMORIA DE CÁLCULO - REPORTE DE CONDUCTORES', 1, 1, 'C')
        
        # Subtítulo con fecha
        self.set_font('Arial', '', 9)
        fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        self.cell(0, 6, f'Proyecto: {backend.SISTEMA_PROYECTO.nombre} | Fecha: {fecha}', 'LRB', 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'C')

def generar_pdf_conductores():
    # Instanciar PDF (Horizontal, milímetros, A4)
    pdf = PDFReport('L', 'mm', 'A4')
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Lista de tableros a imprimir
    lista_tableros = backend.MEMORIA_TABLEROS if backend.MEMORIA_TABLEROS else [backend.SISTEMA_PROYECTO]

    # --- CONFIGURACIÓN DE COLUMNAS (Anchos en mm) ---
    # Ajustado para caber en A4 Horizontal (aprox 280mm útiles)
    # Total ancho sumado: ~275mm
    cols = [
        ("Item", 10), ("Tag", 20), ("Desc", 35), ("V", 10), ("Sys", 8),
        ("kW", 12), ("Inom", 12), ("Icond", 12), ("Mat", 8), ("Cal", 15),
        ("Cap", 12), ("Canal", 25), ("DerT", 10), ("DerB", 10), ("DerTot", 12),
        ("Configuración", 45), ("Reg%", 10), ("CapReal", 12)
    ]

    for tbt in lista_tableros:
        pdf.add_page()
        
        # Título del Tablero
        pdf.set_font('Arial', 'B', 10)
        pdf.set_fill_color(220, 220, 220) # Gris claro
        pdf.cell(0, 8, f"TABLERO: {tbt.nombre} ({tbt.voltaje}V)", 1, 1, 'L', fill=True)
        
        # --- ENCABEZADOS DE TABLA ---
        pdf.set_font('Arial', 'B', 7) # Letra pequeña para caber
        pdf.set_fill_color(44, 62, 80) # Azul oscuro
        pdf.set_text_color(255, 255, 255) # Blanco
        
        for header, width in cols:
            pdf.cell(width, 8, header, 1, 0, 'C', fill=True)
        pdf.ln()
        
        # --- FILAS DE DATOS ---
        pdf.set_text_color(0, 0, 0) # Negro
        pdf.set_font('Arial', '', 7)
        
        if not tbt.circuitos:
            pdf.cell(0, 10, "Sin circuitos registrados.", 1, 1, 'C')
            continue

        for idx, c in enumerate(tbt.circuitos):
            # Asegurar cálculo
            res = c._res_conductor if c._res_conductor else c.ejecutar_seleccion_conductor()
            
            # Preparar datos (Convertir a string y limpiar acentos básicos para evitar errores simples)
            row_data = [
                str(idx + 1),
                c.tag,
                c.descripcion[:20], # Truncar si es muy largo
                str(c.voltaje),
                f"{c.fases}F",
                str(c.potencia_nominal_kw),
                str(round(res['I_Nom'], 1)),
                str(round(res['I_Req'], 1)),
                c.material_conductor,
                res['Calibre'],
                str(res['Cap_Base']),
                c.tipo_instalacion.value[:15], # Truncar
                str(res['F_Temp']),
                str(res['F_Agrup']),
                str(round(res['F_Total'], 2)),
                res['Config'], # Configuración
                f"{round(res['DV'], 2)}%",
                str(round(res['Cap_Real'], 1))
            ]
            
            # Dibujar Fila
            alt_fila = 6
            for i, data in enumerate(row_data):
                ancho = cols[i][1]
                # Try/Except para caracteres raros
                try:
                    txt = str(data).encode('latin-1', 'replace').decode('latin-1')
                except:
                    txt = str(data)
                pdf.cell(ancho, alt_fila, txt, 1, 0, 'C')
            pdf.ln()

    # Guardar archivo en Colab
    nombre_archivo = "Reporte_Conductores_DT58.pdf"
    pdf.output(nombre_archivo)
    print(f"✅ PDF Generado exitosamente: {nombre_archivo}")
    print("📂 Busca en la carpeta de archivos a la izquierda para descargarlo.")
