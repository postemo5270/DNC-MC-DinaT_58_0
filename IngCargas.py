import ipywidgets as widgets
from IPython.display import display, clear_output
import backend
import importlib
from functools import partial

# Recarga backend
importlib.reload(backend)

class AppGestorCargas:
    def __init__(self):
        # --- ESTADO INTERNO ---
        self.nombre_proyecto = ""
        self.tablero_actual = None
        self.indice_edicion = None # None = Modo Agregar, Número = Modo Editar
        
        # Limitante
        self.MAX_CARGAS = 50

        # =============================================================================
        # 1. DEFINICIÓN DE WIDGETS (ELEMENTOS VISUALES)
        # =============================================================================
        self.style_input = widgets.Layout(width='98%')
        self.style_btn_action = widgets.Layout(width='48%')

        # --- PASO 1: PROYECTO ---
        self.txt_proy_nombre = widgets.Text(description="Proyecto:", placeholder="Ej: Planta Tratamiento Aguas", layout=self.style_input)
        self.btn_crear_proy = widgets.Button(description="CREAR PROYECTO", button_style='primary', layout=self.style_input)

        # --- PASO 2: TABLERO ---
        self.txt_tbt_tag = widgets.Text(description="Tag Tbt:", placeholder="Ej: T-GRAL-01", layout=self.style_input)
        self.txt_tbt_desc = widgets.Text(description="Desc:", value="Tablero Principal de Baja Tensión", layout=self.style_input)
        self.dd_voltaje = widgets.Dropdown(options=[208, 220, 440, 460, 480], value=480, description="Voltaje (V):", layout=self.style_input)
        self.dd_fases = widgets.Dropdown(options=[1, 3], value=3, description="Fases:", layout=self.style_input)
        self.btn_crear_tbt = widgets.Button(description="CREAR TABLERO", button_style='info', layout=self.style_input)

        # --- PASO 3: CARGAS (INPUTS) ---
        self.txt_tag = widgets.Text(description="Tag Carga:", placeholder="Ej: M-01", layout=self.style_input)
        self.txt_desc = widgets.Text(description="Desc:", placeholder="Bomba...", layout=self.style_input)
        
        self.num_p = widgets.FloatText(description="Potencia:", layout=self.style_input)
        self.dd_unit = widgets.Dropdown(options=["kW", "hp", "kVA"], value="kW", layout=self.style_input)
        self.num_fp = widgets.FloatText(description="F.P.:", value=0.9, step=0.01, layout=self.style_input)
        self.num_eff = widgets.FloatText(description="Eff:", value=1.0, step=0.01, layout=self.style_input)
        
        self.num_len = widgets.FloatText(description="Long (m):", value=10.0, layout=self.style_input)
        self.num_temp = widgets.IntText(description="T.Amb (°C):", value=30, layout=self.style_input)
        self.dd_inst = widgets.Dropdown(options=["Bandeja", "Ducto", "Directamente Enterrado"], description="Inst.:", value="Bandeja", layout=self.style_input)
        
        self.dd_mat = widgets.Dropdown(options=["Cobre", "Aluminio"], description="Material:", value="Cobre", layout=self.style_input)
        self.dd_aisl = widgets.Dropdown(options=["THHN", "THWN-2", "XHHW-2"], description="Aisl.:", value="THHN", layout=self.style_input)
        self.dd_temp_cable = widgets.Dropdown(options=[60, 75, 90], description="T.Cable:", value=90, layout=self.style_input)
        self.dd_neutro = widgets.Dropdown(options=["NO", "SI"], description="Neutro:", value="NO", layout=self.style_input)

        # Botones de Cargas
        self.btn_add = widgets.Button(description="AGREGAR CARGA", button_style='success', layout=self.style_input)
        self.btn_cancel_edit = widgets.Button(description="CANCELAR EDICIÓN", button_style='warning', layout=self.style_input, disabled=True)
        self.btn_finish = widgets.Button(description="FINALIZAR Y GUARDAR TODO", button_style='danger', layout=self.style_input)

        # --- CONTENEDORES DE SALIDA (Zonas de Pantalla) ---
        self.out_step1 = widgets.Output() # Zona Proyecto
        self.out_step2 = widgets.Output() # Zona Tablero
        self.out_step3 = widgets.Output() # Zona Cargas (Formulario + Tabla)
        self.out_msg = widgets.Output()   # Mensajes de error/éxito

        # --- EVENTOS ---
        self.btn_crear_proy.on_click(self.paso_crear_proyecto)
        self.btn_crear_tbt.on_click(self.paso_crear_tablero)
        self.btn_add.on_click(self.gestionar_carga)
        self.btn_cancel_edit.on_click(self.cancelar_edicion)
        self.btn_finish.on_click(self.finalizar_todo)

    def iniciar_interfaz(self):
        """Arranca la aplicación mostrando solo el Paso 1."""
        backend.MEMORIA_TABLEROS = [] # Limpieza inicial
        
        display(self.out_msg)
        display(self.out_step1)
        display(self.out_step2)
        display(self.out_step3)

        with self.out_step1:
            clear_output()
            display(widgets.HTML("<h3>🚀 PASO 1: CREACIÓN DE PROYECTO</h3>"))
            display(self.txt_proy_nombre)
            display(widgets.HTML("<br>"))
            display(self.btn_crear_proy)

    def paso_crear_proyecto(self, b):
        """Valida nombre proyecto y pasa al Paso 2."""
        if not self.txt_proy_nombre.value:
            self.mostrar_alerta("⚠️ Debes ingresar un nombre para el proyecto.", error=True)
            return
        
        self.nombre_proyecto = self.txt_proy_nombre.value
        self.out_step1.clear_output() # Limpia pantalla anterior
        
        # Muestra Paso 2
        with self.out_step2:
            clear_output()
            display(widgets.HTML(f"<h3>🏢 PASO 2: DATOS DEL TABLERO (Proyecto: {self.nombre_proyecto})</h3>"))
            display(self.txt_tbt_tag)
            display(self.txt_tbt_desc)
            display(widgets.HBox([self.dd_voltaje, self.dd_fases]))
            display(widgets.HTML("<br>"))
            display(self.btn_crear_tbt)

    def paso_crear_tablero(self, b):
        """Instancia el Tablero y pasa al Paso 3."""
        if not self.txt_tbt_tag.value:
            self.mostrar_alerta("⚠️ El tablero debe tener un TAG.", error=True)
            return

        # Crear objeto en Backend
        self.tablero_actual = backend.Tablero(
            nombre=self.txt_tbt_tag.value, # Usamos el TAG como nombre interno
            voltaje=self.dd_voltaje.value,
            fases=self.dd_fases.value
        )
        # Nota: Podríamos guardar la descripción en el objeto Tablero si modificamos backend.py, 
        # por ahora se queda visual.
        
        backend.MEMORIA_TABLEROS.append(self.tablero_actual)
        
        self.out_step2.clear_output() # Limpia pantalla anterior
        self.renderizar_paso_3()

    def renderizar_paso_3(self):
        """Muestra el formulario de cargas y la tabla vacía."""
        with self.out_step3:
            clear_output()
            # Encabezado fijo
            display(widgets.HTML(f"""
            <div style='background:#ecf0f1; padding:10px; border-left:5px solid #27ae60;'>
                <b>PROYECTO:</b> {self.nombre_proyecto}<br>
                <b>TABLERO:</b> {self.tablero_actual.nombre} ({self.tablero_actual.voltaje}V)
            </div>
            <h3>⚡ PASO 3: INGRESO DE CARGAS</h3>
            """))
            
            # Formulario
            row1 = widgets.HBox([self.txt_tag, self.txt_desc])
            row2 = widgets.HBox([self.num_p, self.dd_unit, self.num_fp, self.num_eff])
            row3 = widgets.HBox([self.num_len, self.dd_inst, self.num_temp])
            row4 = widgets.HBox([self.dd_mat, self.dd_aisl, self.dd_temp_cable, self.dd_neutro])

            form = widgets.VBox([
                widgets.HTML("<b>Datos Eléctricos:</b>"), row1, row2,
                widgets.HTML("<b>Datos Físicos:</b>"), row3, row4,
                widgets.HTML("<hr>"),
                widgets.HBox([self.btn_add, self.btn_cancel_edit])
            ])
            display(form)
            
            # Espacio para la tabla
            self.out_tabla = widgets.Output()
            display(self.out_tabla)
            self.actualizar_tabla()

    def gestionar_carga(self, b):
        """Agrega o Edita una carga."""
        # Validación básica
        if self.num_p.value <= 0:
            self.mostrar_alerta("⚠️ La potencia debe ser mayor a 0.", error=True)
            return
        
        # Validación Límite
        if self.indice_edicion is None and len(self.tablero_actual.circuitos) >= self.MAX_CARGAS:
            self.mostrar_alerta(f"⛔ Has llegado al límite de {self.MAX_CARGAS} cargas.", error=True)
            return

        # Recopilar Datos
        datos = {
            'tag': self.txt_tag.value, 'descripcion': self.txt_desc.value,
            'p_input': self.num_p.value, 'unidad': self.dd_unit.value,
            'tension': self.tablero_actual.voltaje, 'fases': self.tablero_actual.fases,
            'fp': self.num_fp.value, 'eff': self.num_eff.value,
            'longitud': self.num_len.value,
            'mat': "CU" if self.dd_mat.value == "Cobre" else "AL",
            'tipo_aislam': self.dd_aisl.value, 't_aislamiento_cable': self.dd_temp_cable.value,
            'tipo_instalacion': self.dd_inst.value, 'req_neutro': self.dd_neutro.value,
            't_ambiente': self.num_temp.value
        }
        
        nueva_carga = backend.Circuito(**datos)

        if self.indice_edicion is None:
            # AGREGAR
            self.tablero_actual.agregar_c(nueva_carga)
            self.mostrar_alerta(f"✅ Carga {datos['tag']} agregada.")
        else:
            # EDITAR
            self.tablero_actual.circuitos[self.indice_edicion] = nueva_carga
            self.mostrar_alerta(f"🔄 Carga {datos['tag']} actualizada.")
            self.cancelar_edicion(None)

        self.limpiar_form()
        self.actualizar_tabla()

    def cargar_edicion(self, indice, b):
        """Sube los datos de la tabla al formulario."""
        c = self.tablero_actual.circuitos[indice]
        
        # Llenar inputs
        self.txt_tag.value = c.tag
        self.txt_desc.value = c.descripcion
        self.num_p.value = c.p_input
        self.dd_unit.value = c.unidad
        self.num_fp.value = c.fp
        self.num_eff.value = c.eff
        self.num_len.value = c.l_m
        self.num_temp.value = c.t_ambiente
        self.dd_inst.value = c.tipo_instalacion
        self.dd_mat.value = "Cobre" if c.mat == "CU" else "Aluminio"
        self.dd_aisl.value = c.tipo_aislam
        self.dd_temp_cable.value = c.t_aislamiento_cable
        self.dd_neutro.value = c.req_neutro
        
        # Cambiar estado botones
        self.indice_edicion = indice
        self.btn_add.description = "ACTUALIZAR CARGA"
        self.btn_add.button_style = 'warning'
        self.btn_cancel_edit.disabled = False
        
        self.mostrar_alerta(f"✏️ Editando carga #{indice + 1}")

    def cancelar_edicion(self, b):
        """Sale del modo edición."""
        self.indice_edicion = None
        self.btn_add.description = "AGREGAR CARGA"
        self.btn_add.button_style = 'success'
        self.btn_cancel_edit.disabled = True
        self.limpiar_form()
        self.mostrar_alerta("Edición cancelada.")

    def eliminar_fila(self, indice, b):
        """Borra carga."""
        del self.tablero_actual.circuitos[indice]
        self.actualizar_tabla()
        self.mostrar_alerta("🗑️ Carga eliminada.")

    def actualizar_tabla(self):
        """Redibuja la tabla con botones de texto claros."""
        with self.out_tabla:
            clear_output(wait=True)
            if not self.tablero_actual.circuitos:
                display(widgets.HTML("<br><i>No hay cargas registradas. Ingresa la primera arriba.</i>"))
                return

            # Cabecera Tabla
            display(widgets.HTML(f"<h4>📋 LISTA DE CARGAS ({len(self.tablero_actual.circuitos)}/{self.MAX_CARGAS})</h4>"))
            
            items = []
            for i, c in enumerate(self.tablero_actual.circuitos):
                # Botones con TEXTO explícito (no solo iconos)
                btn_edit = widgets.Button(description="✏️ EDITAR", layout=widgets.Layout(width='100px'))
                btn_del = widgets.Button(description="🗑️ BORRAR", button_style='danger', layout=widgets.Layout(width='100px'))
                
                # Callbacks
                btn_edit.on_click(partial(self.cargar_edicion, i))
                btn_del.on_click(partial(self.eliminar_fila, i))
                
                # Fila visual
                fila = widgets.HBox([
                    widgets.Label(f"#{i+1}", layout=widgets.Layout(width='30px')),
                    widgets.Label(f"{c.tag}", layout=widgets.Layout(width='80px', font_weight='bold')),
                    widgets.Label(f"{c.p_input} {c.unidad}", layout=widgets.Layout(width='80px')),
                    widgets.Label(f"L={c.l_m}m", layout=widgets.Layout(width='60px')),
                    btn_edit,
                    btn_del
                ], layout=widgets.Layout(border_bottom='1px solid #ddd', padding='5px'))
                items.append(fila)
            
            items.append(widgets.HTML("<br>"))
            items.append(self.btn_finish)
            display(widgets.VBox(items))

    def limpiar_form(self):
        self.txt_tag.value = ""
        self.txt_desc.value = ""
        self.num_p.value = 0.0

    def mostrar_alerta(self, msg, error=False):
        color = '#c0392b' if error else '#27ae60' # Rojo o Verde
        with self.out_msg:
            clear_output(wait=True)
            display(widgets.HTML(f"<div style='background:{color}; color:white; padding:5px; border-radius:3px;'>{msg}</div>"))

    def finalizar_todo(self, b):
        self.out_step3.clear_output()
        self.out_msg.clear_output()
        display(widgets.HTML(f"""
        <h2 style='color:green'>✅ PROCESO COMPLETADO</h2>
        <p>El tablero <b>{self.tablero_actual.nombre}</b> está listo en memoria.</p>
        <p>Ahora ejecuta <b>ModConds.py</b> para ver los cálculos.</p>
        """))

# --- EJECUCIÓN ---
app = AppGestorCargas()
def iniciar_interfaz():
    app.iniciar_interfaz()
