import ipywidgets as widgets
from IPython.display import display, clear_output
import backend
import importlib
from functools import partial

# Recarga segura para desarrollo
importlib.reload(backend)

class ValidadorInputs:
    """Clase estática para centralizar reglas de negocio de los inputs."""
    
    @staticmethod
    def validar_carga(datos: dict) -> tuple[bool, str]:
        # 1. Validaciones Físicas Básicas
        if datos['p_input'] <= 0:
            return False, "⛔ La potencia debe ser mayor a 0."
        if datos['longitud'] <= 0:
            return False, "⛔ La longitud debe ser positiva."
        
        # 2. Validaciones Eléctricas
        if not (0 < datos['fp'] <= 1.0):
            return False, "⛔ El Factor de Potencia debe estar entre 0.01 y 1.0."
        if not (0 < datos['eff'] <= 1.0):
            return False, "⛔ La Eficiencia debe estar entre 0.01 y 1.0."
            
        # 3. Validaciones de Texto
        if not datos['tag'].strip():
            return False, "⚠️ La carga requiere un TAG identificador."
            
        return True, "OK"

class AppGestorCargas:
    def __init__(self):
        # --- ESTADO Y CONFIG ---
        self.nombre_proyecto = ""
        self.tablero_actual = None
        self.indice_edicion = None 
        self.MAX_CARGAS = 50

        # --- ESTILOS ---
        self.layout_full = widgets.Layout(width='98%')
        self.layout_half = widgets.Layout(width='48%')
        self.style_header = {'description_width': 'initial'}

        # =============================================================================
        # 1. WIDGETS DE PROYECTO Y TABLERO
        # =============================================================================
        self.w_proy_nombre = widgets.Text(description="Nombre Proyecto:", placeholder="Ej: Planta Tratamiento", layout=self.layout_full, style=self.style_header)
        self.btn_init_proy = widgets.Button(description="INICIAR PROYECTO", button_style='primary', layout=self.layout_full)

        self.w_tbt_tag = widgets.Text(description="Tag Tablero:", placeholder="T-01", layout=self.layout_half)
        self.w_tbt_volt = widgets.Dropdown(options=[208, 220, 440, 460, 480], value=480, description="Voltaje (V):", layout=self.layout_half)
        self.w_tbt_fases = widgets.Dropdown(options=[1, 3], value=3, description="Fases:", layout=self.layout_half)
        self.btn_crear_tbt = widgets.Button(description="CONFIGURAR TABLERO", button_style='info', layout=self.layout_full)

        # =============================================================================
        # 2. WIDGETS DE CARGAS (Separados por dominio)
        # =============================================================================
        
        # Grupo A: Datos de Placa (La Carga en sí)
        self.w_tag = widgets.Text(description="Tag:", placeholder="M-101", layout=widgets.Layout(width='30%'))
        self.w_desc = widgets.Text(description="Desc:", placeholder="Bomba Recirculación", layout=widgets.Layout(width='68%'))
        self.w_pot = widgets.FloatText(description="Potencia:", layout=widgets.Layout(width='32%'))
        self.w_unit = widgets.Dropdown(options=["kW", "hp", "kVA"], value="kW", layout=widgets.Layout(width='20%'))
        self.w_fp = widgets.BoundedFloatText(value=0.9, min=0.1, max=1.0, step=0.01, description="F.P.:", layout=widgets.Layout(width='23%'))
        self.w_eff = widgets.BoundedFloatText(value=1.0, min=0.1, max=1.0, step=0.01, description="Eff:", layout=widgets.Layout(width='23%'))
        
        # Grupo B: Infraestructura y Medio (El Cable y Canalización)
        self.w_len = widgets.FloatText(value=10.0, description="Long (m):", layout=widgets.Layout(width='32%'))
        self.w_inst = widgets.Dropdown(options=["Bandeja", "Ducto", "Directamente Enterrado"], value="Bandeja", layout=widgets.Layout(width='32%'))
        self.w_mat = widgets.Dropdown(options=["CU", "AL"], description="Material:", value="CU", layout=widgets.Layout(width='32%'))
        
        self.w_temp = widgets.IntSlider(value=30, min=10, max=60, description="T.Amb (°C):", layout=self.layout_full)
        self.w_aisl = widgets.Dropdown(options=["THHN", "THWN-2", "XHHW-2"], value="THHN", layout=widgets.Layout(width='32%'))
        self.w_tcable = widgets.Dropdown(options=[60, 75, 90], description="T.Cable:", value=90, layout=widgets.Layout(width='32%'))
        self.w_neutro = widgets.Dropdown(options=["NO", "SI"], description="Neutro:", value="NO", layout=widgets.Layout(width='32%'))

        # Botones de Acción
        self.btn_guardar = widgets.Button(description="AGREGAR CARGA", button_style='success', layout=self.layout_full)
        self.btn_cancelar = widgets.Button(description="CANCELAR", button_style='warning', layout=self.layout_full, disabled=True)
        self.btn_finalizar = widgets.Button(description="FINALIZAR & IR A CÁLCULOS", button_style='danger', layout=self.layout_full)

        # --- OUTPUTS ---
        self.out_main = widgets.Output()
        self.out_msgs = widgets.Output()

        # --- BINDINGS ---
        self.btn_init_proy.on_click(self.accion_iniciar_proyecto)
        self.btn_crear_tbt.on_click(self.accion_crear_tablero)
        self.btn_guardar.on_click(self.accion_gestionar_carga)
        self.btn_cancelar.on_click(self.accion_cancelar_edicion)
        self.btn_finalizar.on_click(self.accion_finalizar)

    def iniciar(self):
        backend.MEMORIA_TABLEROS = []
        display(self.out_msgs)
        display(self.out_main)
        self.render_paso_1()

    # =============================================================================
    # LÓGICA DE INTERFAZ (VISTAS)
    # =============================================================================
    def render_paso_1(self):
        with self.out_main:
            clear_output()
            display(widgets.HTML("<h3>1. Definición del Proyecto</h3>"))
            display(self.w_proy_nombre, self.btn_init_proy)

    def render_paso_2(self):
        with self.out_main:
            clear_output()
            display(widgets.HTML(f"<h3>2. Configuración del Tablero ({self.nombre_proyecto})</h3>"))
            display(widgets.HBox([self.w_tbt_tag, self.w_tbt_volt, self.w_tbt_fases]))
            display(widgets.HTML("<br>"))
            display(self.btn_crear_tbt)

    def render_paso_3(self):
        with self.out_main:
            clear_output()
            # Header Visual
            display(widgets.HTML(f"""
            <div style='background:#f4f6f7; padding:10px; border-left:4px solid #3498db;'>
                <b>PROYECTO:</b> {self.nombre_proyecto} | 
                <b>TABLERO:</b> {self.tablero_actual.nombre} ({self.tablero_actual.voltaje}V - {self.tablero_actual.fases}Ø)
            </div>
            """))
            
            # Formulario Compacto
            display(widgets.HTML("<b>A. Datos de Carga (Placa):</b>"))
            display(widgets.HBox([self.w_tag, self.w_desc]))
            display(widgets.HBox([self.w_pot, self.w_unit, self.w_fp, self.w_eff]))
            
            display(widgets.HTML("<b>B. Infraestructura y Cableado:</b>"))
            display(widgets.HBox([self.w_len, self.w_inst, self.w_mat]))
            display(widgets.HBox([self.w_aisl, self.w_tcable, self.w_neutro]))
            display(self.w_temp)
            
            display(widgets.HTML("<hr>"))
            display(widgets.HBox([self.btn_guardar, self.btn_cancelar]))
            
            # Tabla Dinámica
            self.out_tabla = widgets.Output()
            display(self.out_tabla)
            self.actualizar_tabla()

    # =============================================================================
    # CONTROLADORES (ACCIONES)
    # =============================================================================
    def accion_iniciar_proyecto(self, b):
        if not self.w_proy_nombre.value:
            self.msg("⚠️ Falta nombre del proyecto.", error=True)
            return
        self.nombre_proyecto = self.w_proy_nombre.value
        self.msg(f"Proyecto '{self.nombre_proyecto}' iniciado.")
        self.render_paso_2()

    def accion_crear_tablero(self, b):
        if not self.w_tbt_tag.value:
            self.msg("⚠️ Falta TAG del tablero.", error=True)
            return
        
        self.tablero_actual = backend.Tablero(
            nombre=self.w_tbt_tag.value,
            voltaje=self.w_tbt_volt.value,
            fases=self.w_tbt_fases.value
        )
        backend.MEMORIA_TABLEROS.append(self.tablero_actual)
        self.msg(f"Tablero {self.tablero_actual.nombre} configurado.")
        self.render_paso_3()

    def accion_gestionar_carga(self, b):
        # 1. Extracción de Datos (Desacoplado de la lógica de guardado)
        datos_raw = self._extraer_datos_formulario()
        
        # 2. Validación
        es_valido, mensaje = ValidadorInputs.validar_carga(datos_raw)
        if not es_valido:
            self.msg(mensaje, error=True)
            return

        # 3. Creación/Edición de Objeto (Solo Datos Crudos)
        nueva_carga = backend.Circuito(**datos_raw)

        if self.indice_edicion is None:
            # Modo Agregar
            if len(self.tablero_actual.circuitos) >= self.MAX_CARGAS:
                self.msg("⛔ Límite de cargas alcanzado.", error=True)
                return
            self.tablero_actual.agregar_c(nueva_carga)
            self.msg(f"✅ Carga {datos_raw['tag']} agregada.")
        else:
            # Modo Editar
            self.tablero_actual.circuitos[self.indice_edicion] = nueva_carga
            self.msg(f"🔄 Carga {datos_raw['tag']} actualizada.")
            self.accion_cancelar_edicion(None)

        self._limpiar_form()
        self.actualizar_tabla()

    def accion_editar(self, idx, b):
        """Carga datos del modelo a la vista."""
        c = self.tablero_actual.circuitos[idx]
        
        self.w_tag.value = c.tag
        self.w_desc.value = c.descripcion
        self.w_pot.value = c.p_input
        self.w_unit.value = c.unidad
        self.w_fp.value = c.fp
        self.w_eff.value = c.eff
        self.w_len.value = c.l_m
        self.w_inst.value = c.tipo_instalacion
        self.w_mat.value = c.mat
        self.w_temp.value = c.t_ambiente
        self.w_aisl.value = c.tipo_aislam
        self.w_tcable.value = c.t_aislamiento_cable
        self.w_neutro.value = c.req_neutro

        self.indice_edicion = idx
        self.btn_guardar.description = "ACTUALIZAR"
        self.btn_guardar.button_style = 'warning'
        self.btn_cancelar.disabled = False
        self.msg(f"✏️ Editando item #{idx+1}")

    def accion_borrar(self, idx, b):
        del self.tablero_actual.circuitos[idx]
        self.actualizar_tabla()
        self.msg("🗑️ Item eliminado.")

    def accion_cancelar_edicion(self, b):
        self.indice_edicion = None
        self.btn_guardar.description = "AGREGAR CARGA"
        self.btn_guardar.button_style = 'success'
        self.btn_cancelar.disabled = True
        self._limpiar_form()
        self.msg("Edición cancelada.")

    def accion_finalizar(self, b):
        self.out_main.clear_output()
        self.msg("✅ Cargas guardadas. Ejecuta ModConds.py para calcular.")

    # =============================================================================
    # UTILIDADES (INTERNAS)
    # =============================================================================
    def _extraer_datos_formulario(self) -> dict:
        """Extrae valores puros de los widgets. Independiente de Backend."""
        return {
            'tag': self.w_tag.value,
            'descripcion': self.w_desc.value,
            'p_input': self.w_pot.value,
            'unidad': self.w_unit.value,
            'tension': self.tablero_actual.voltaje,
            'fases': self.tablero_actual.fases,
            'fp': self.w_fp.value,
            'eff': self.w_eff.value,
            'longitud': self.w_len.value,
            'mat': self.w_mat.value, # Ya viene como CU/AL del dropdown
            'tipo_aislam': self.w_aisl.value,
            't_aislamiento_cable': self.w_tcable.value,
            'tipo_instalacion': self.w_inst.value,
            'req_neutro': self.w_neutro.value,
            't_ambiente': self.w_temp.value
        }

    def _limpiar_form(self):
        self.w_tag.value = ""
        self.w_desc.value = ""
        self.w_pot.value = 0.0
        # Restablecemos valores por defecto seguros
        self.w_fp.value = 0.9
        self.w_len.value = 10.0

    def actualizar_tabla(self):
        with self.out_tabla:
            clear_output(wait=True)
            if not self.tablero_actual.circuitos:
                return

            items = []
            # Cabecera Simple
            header = widgets.HBox([
                widgets.Label("TAG", layout=widgets.Layout(width='20%', font_weight='bold')),
                widgets.Label("POTENCIA", layout=widgets.Layout(width='20%', font_weight='bold')),
                widgets.Label("LONGITUD", layout=widgets.Layout(width='20%', font_weight='bold')),
                widgets.Label("ACCIONES", layout=widgets.Layout(width='40%', font_weight='bold')),
            ])
            items.append(header)

            for i, c in enumerate(self.tablero_actual.circuitos):
                btn_edit = widgets.Button(description="✏️", layout=widgets.Layout(width='40px'))
                btn_del = widgets.Button(description="🗑️", button_style='danger', layout=widgets.Layout(width='40px'))
                
                btn_edit.on_click(partial(self.accion_editar, i))
                btn_del.on_click(partial(self.accion_borrar, i))

                fila = widgets.HBox([
                    widgets.Label(c.tag, layout=widgets.Layout(width='20%')),
                    widgets.Label(f"{c.p_input} {c.unidad}", layout=widgets.Layout(width='20%')),
                    widgets.Label(f"{c.l_m} m", layout=widgets.Layout(width='20%')),
                    widgets.HBox([btn_edit, btn_del], layout=widgets.Layout(width='40%'))
                ], layout=widgets.Layout(border_bottom='1px solid #eee'))
                items.append(fila)
            
            items.append(widgets.HTML("<br>"))
            items.append(self.btn_finalizar)
            display(widgets.VBox(items))

    def msg(self, txt, error=False):
        color = '#e74c3c' if error else '#27ae60'
        with self.out_msgs:
            clear_output(wait=True)
            display(widgets.HTML(f"<div style='color:{color}; font-weight:bold;'>{txt}</div>"))

# Ejecución
app = AppGestorCargas()
def iniciar_interfaz():
    app.iniciar()
