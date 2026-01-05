import ipywidgets as widgets
from IPython.display import display, clear_output
import backend
import importlib
from functools import partial

# Recargamos backend para asegurar consistencia
importlib.reload(backend)

class AppGestorCargas:
    def __init__(self):
        # --- ESTADO DE LA APLICACIÓN ---
        self.tablero_actual = None
        self.indice_edicion = None # Si no es None, estamos editando esta fila
        
        # =============================================================================
        # 1. DEFINICIÓN DE WIDGETS
        # =============================================================================
        self.style_input = widgets.Layout(width='98%')
        self.style_btn_small = widgets.Layout(width='35px', padding='0px')

        # --- TABLERO ---
        self.dd_voltaje = widgets.Dropdown(options=[208, 220, 440, 460, 480], value=480, description="Voltaje (V):", layout=self.style_input)
        self.dd_fases = widgets.Dropdown(options=[1, 3], value=3, description="Fases:", layout=self.style_input)
        self.txt_nombre_tablero = widgets.Text(description="Nombre:", value="Tablero Principal", layout=self.style_input)
        self.btn_crear_tbt = widgets.Button(description="INICIAR PROYECTO", button_style='primary', layout=self.style_input, icon='bolt')

        # --- CARGAS (INPUTS) ---
        self.txt_tag = widgets.Text(description="Tag:", placeholder="Ej: M-01", layout=self.style_input)
        self.txt_desc = widgets.Text(description="Desc:", placeholder="Bomba Agua", layout=self.style_input)
        
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

        # --- BOTONES DE CONTROL ---
        self.btn_accion = widgets.Button(description="AGREGAR CARGA", button_style='success', layout=self.style_input, icon='plus')
        self.btn_cancelar_edicion = widgets.Button(description="Cancelar Edición", button_style='warning', layout=self.style_input, disabled=True)
        self.btn_finish = widgets.Button(description="GUARDAR Y SALIR", button_style='danger', layout=self.style_input, icon='save')

        # --- CONTENEDORES ---
        self.out_header = widgets.Output() # Zona superior (Config Tablero)
        self.out_form = widgets.Output()   # Zona formulario
        self.out_list = widgets.Output()   # Zona tabla de datos
        self.out_msgs = widgets.Output()   # Zona de notificaciones

        # --- VINCULACIÓN EVENTOS ---
        self.btn_crear_tbt.on_click(self.crear_tablero)
        self.btn_accion.on_click(self.gestionar_carga)
        self.btn_cancelar_edicion.on_click(self.cancelar_edicion)
        self.btn_finish.on_click(self.finalizar)

    def iniciar_interfaz(self):
        """Punto de entrada principal."""
        backend.MEMORIA_TABLEROS = [] # Limpieza inicial
        display(self.out_header)
        display(self.out_form)
        display(self.out_list)
        display(self.out_msgs)
        
        with self.out_header:
            clear_output()
            display(widgets.HTML("<h3 style='color:#2980b9; border-bottom:2px solid #2980b9'>⚡ Configuración Inicial del Proyecto</h3>"))
            display(widgets.VBox([
                self.txt_nombre_tablero,
                widgets.HBox([self.dd_voltaje, self.dd_fases]),
                widgets.HTML("<br>"),
                self.btn_crear_tbt
            ]))

    def crear_tablero(self, b):
        """Inicializa el objeto Tablero y muestra el formulario."""
        self.tablero_actual = backend.Tablero(self.txt_nombre_tablero.value, self.dd_voltaje.value, self.dd_fases.value)
        backend.MEMORIA_TABLEROS.append(self.tablero_actual)
        
        # Ocultamos la config inicial y mostramos el formulario
        self.out_header.clear_output()
        with self.out_header:
            display(widgets.HTML(f"""
            <div style='background-color:#eaf2f8; padding:10px; border-left: 5px solid #2980b9;'>
                <h4 style='margin:0; color:#1a5276'>📂 Proyecto: {self.tablero_actual.nombre}</h4>
                <small>Sistema: {self.tablero_actual.voltaje}V - {self.tablero_actual.fases} Fases</small>
            </div>
            """))
            
        self.mostrar_formulario()
        self.actualizar_lista_visual()

    def mostrar_formulario(self):
        """Renderiza los inputs."""
        with self.out_form:
            clear_output()
            row1 = widgets.HBox([self.txt_tag, self.txt_desc])
            row2 = widgets.HBox([self.num_p, self.dd_unit, self.num_fp, self.num_eff])
            row3 = widgets.HBox([self.num_len, self.dd_inst, self.num_temp])
            row4 = widgets.HBox([self.dd_mat, self.dd_aisl, self.dd_temp_cable, self.dd_neutro])
            
            form = widgets.VBox([
                widgets.HTML("<br><b>1. Datos de Carga</b>"), row1, row2,
                widgets.HTML("<b>2. Configuración Física y Cableado</b>"), row3, row4,
                widgets.HTML("<hr>"),
                widgets.HBox([self.btn_accion, self.btn_cancelar_edicion])
            ])
            display(form)

    def gestionar_carga(self, b):
        """Decide si agrega una nueva o actualiza una existente."""
        if self.num_p.value <= 0:
            self.mostrar_mensaje("⚠️ La potencia debe ser mayor a 0", error=True)
            return

        # Recopilar datos del formulario
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

        # Crear Objeto (Sin Calcular)
        nueva_carga = backend.Circuito(**datos)

        if self.indice_edicion is None:
            # MODO AGREGAR
            self.tablero_actual.agregar_c(nueva_carga)
            self.mostrar_mensaje(f"✅ Carga {datos['tag']} agregada.")
        else:
            # MODO EDICIÓN
            self.tablero_actual.circuitos[self.indice_edicion] = nueva_carga
            self.mostrar_mensaje(f"🔄 Carga {datos['tag']} actualizada.")
            self.cancelar_edicion(None) # Resetear modo edición

        # Limpiar Formulario y Actualizar Tabla
        self.limpiar_inputs()
        self.actualizar_lista_visual()

    def cargar_para_edicion(self, indice, b):
        """Carga los datos de un objeto Circuito en los inputs."""
        c = self.tablero_actual.circuitos[indice]
        
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

        # Cambiar estado UI
        self.indice_edicion = indice
        self.btn_accion.description = "ACTUALIZAR CARGA"
        self.btn_accion.button_style = 'warning'
        self.btn_accion.icon = 'refresh'
        self.btn_cancelar_edicion.disabled = False
        
        self.mostrar_mensaje(f"✏️ Editando ítem #{indice+1}...")

    def cancelar_edicion(self, b):
        """Sale del modo edición."""
        self.indice_edicion = None
        self.btn_accion.description = "AGREGAR CARGA"
        self.btn_accion.button_style = 'success'
        self.btn_accion.icon = 'plus'
        self.btn_cancelar_edicion.disabled = True
        self.limpiar_inputs()

    def eliminar_carga(self, indice, b):
        """Elimina una fila."""
        del self.tablero_actual.circuitos[indice]
        self.actualizar_lista_visual()
        self.mostrar_mensaje("🗑️ Carga eliminada.")

    def actualizar_lista_visual(self):
        """Redibuja la tabla de cargas acumuladas."""
        with self.out_list:
            clear_output(wait=True)
            
            if not self.tablero_actual.circuitos:
                display(widgets.HTML("<i>No hay cargas ingresadas aún.</i>"))
                return

            # Cabecera
            header = widgets.HBox([
                widgets.HTML("<b>#</b>", layout=widgets.Layout(width='30px')),
                widgets.HTML("<b>Tag</b>", layout=widgets.Layout(width='80px')),
                widgets.HTML("<b>Descripción</b>", layout=widgets.Layout(width='150px')),
                widgets.HTML("<b>Potencia</b>", layout=widgets.Layout(width='80px')),
                widgets.HTML("<b>Acciones</b>", layout=widgets.Layout(width='100px')),
            ], layout=widgets.Layout(border='1px solid #ccc', background_color='#f0f0f0'))
            
            filas = [header]
            
            for i, c in enumerate(self.tablero_actual.circuitos):
                # Botones de acción con callbacks parciales
                btn_edit = widgets.Button(icon='pencil', layout=self.style_btn_small, tooltip="Editar")
                btn_del = widgets.Button(icon='trash', button_style='danger', layout=self.style_btn_small, tooltip="Eliminar")
                
                # Usamos partial para "congelar" el indice i
                btn_edit.on_click(partial(self.cargar_para_edicion, i))
                btn_del.on_click(partial(self.eliminar_carga, i))
                
                row = widgets.HBox([
                    widgets.Label(str(i+1), layout=widgets.Layout(width='30px')),
                    widgets.Label(c.tag, layout=widgets.Layout(width='80px')),
                    widgets.Label(c.descripcion[:20], layout=widgets.Layout(width='150px')),
                    widgets.Label(f"{c.p_input} {c.unidad}", layout=widgets.Layout(width='80px')),
                    widgets.HBox([btn_edit, btn_del])
                ], layout=widgets.Layout(border_bottom='1px solid #eee'))
                filas.append(row)
            
            filas.append(widgets.HTML("<br>"))
            filas.append(self.btn_finish)
            
            display(widgets.VBox(filas))

    def limpiar_inputs(self):
        self.txt_tag.value = ""
        self.txt_desc.value = ""
        self.num_p.value = 0.0

    def mostrar_mensaje(self, msg, error=False):
        color = 'red' if error else 'green'
        with self.out_msgs:
            clear_output(wait=True)
            display(widgets.HTML(f"<span style='color:{color}; font-weight:bold'>{msg}</span>"))

    def finalizar(self, b):
        self.out_form.clear_output()
        self.out_list.clear_output()
        self.out_msgs.clear_output()
        display(widgets.HTML(f"""
        <h3 style='color:green'>✅ Datos guardados correctamente</h3>
        <p>Total Cargas: {len(self.tablero_actual.circuitos)}</p>
        <p>⚠️ <b>Importante:</b> Los cálculos de ingeniería se realizarán al ejecutar <code>ModConds.py</code>.</p>
        """))

# Instancia global para ser llamada desde Colab
app = AppGestorCargas()

def iniciar_interfaz():
    app.iniciar_interfaz()
