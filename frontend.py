# =============================================================================
# MÓDULO FRONTEND: INTERFAZ GRÁFICA DE USUARIO (GUI)
# =============================================================================

import ipywidgets as widgets
from IPython.display import display, clear_output
import pandas as pd

# Importamos la lógica pura del backend
from backend import Circuito, Tablero, Transformador, TipoOperacion, TipoInstalacion, ORDEN_CALIBRES

# Variable Global para manejar el estado dentro de la interfaz
SISTEMA_GLOBAL = None
contenedor_principal = widgets.Output()

class GestorFlujo:
    def __init__(self):
        self.trafo = None
        self.tablero_actual = None
        self.parent_actual = None
        self.stack_parents = []
        self.voltaje_sys = 480.0
        
    def iniciar(self):
        """PANTALLA 1: DATOS DEL PROYECTO"""
        with contenedor_principal:
            clear_output()
            print("🏗️ PASO 1: DATOS GENERALES")
            print("="*60)
            
            w_nom = widgets.Text(description="Proyecto:", placeholder="Planta Ptar...")
            w_volt = widgets.Dropdown(options=[480.0, 440.0, 220.0, 208.0], value=480.0, description="Voltaje:")
            btn_start = widgets.Button(description="INICIAR DISEÑO >>", button_style='primary')
            
            def on_start(b):
                if not w_nom.value: return
                self.trafo = Transformador(w_nom.value)
                self.parent_actual = self.trafo 
                self.stack_parents = []
                self.voltaje_sys = w_volt.value
                self.pantalla_crear_tablero()
                
            w_nom.on_submit(on_start) 
            btn_start.on_click(on_start)
            display(widgets.VBox([w_nom, w_volt, btn_start]))

    def pantalla_crear_tablero(self):
        """PANTALLA 2: DEFINIR TABLERO"""
        with contenedor_principal:
            clear_output()
            origen = self.parent_actual.nombre if hasattr(self.parent_actual, 'nombre') else "TRAFO"
            print(f"📦 PASO 2: NUEVO TABLERO (Alimentado por {origen})")
            print("="*60)
            
            w_t_nom = widgets.Text(description="Nombre TBT:", placeholder="T-01")
            w_fd = widgets.BoundedFloatText(description="Factor Div:", value=1.0, min=0.1, max=1.0)
            btn_crear = widgets.Button(description="IR A CARGAS >>", button_style='success')
            
            def on_crear(b):
                if not w_t_nom.value: return
                nuevo_tablero = Tablero(w_t_nom.value, self.voltaje_sys, 3, w_fd.value)
                if isinstance(self.parent_actual, Transformador):
                    self.parent_actual.tableros.append(nuevo_tablero)
                else:
                    self.parent_actual.sub_tableros.append(nuevo_tablero)
                self.tablero_actual = nuevo_tablero
                self.pantalla_cargas()
                
            w_t_nom.on_submit(on_crear)
            btn_crear.on_click(on_crear)
            display(widgets.VBox([w_t_nom, w_fd, btn_crear]))

    def pantalla_cargas(self):
        """PANTALLA 3: DATA ENTRY (ORDEN INVERTIDO Y TABLA COMPLETA)"""
        with contenedor_principal:
            clear_output()
            print(f"⚡ AGREGANDO CARGAS A: {self.tablero_actual.nombre}")
            print("   (Llene datos y presione ENTER en Tag o Descripción para agregar)")
            print("="*80)
            
            style = {'description_width': 'initial'}
            layout_sm = widgets.Layout(width='140px')
            layout_md = widgets.Layout(width='220px')
            
            # --- ZONA 1: DATOS DE CARGA (ARRIBA) ---
            lbl_data = widgets.HTML("<b>1. DATOS DE CARGA (Variables):</b>")
            
            w_tag = widgets.Text(description="TAG:", placeholder="M-XX", style=style, layout=layout_sm)
            w_kw = widgets.FloatText(description="kW:", value=0, style=style, layout=layout_sm)
            w_desc = widgets.Text(description="Descripción:", placeholder="Motor...", style=style, layout=widgets.Layout(width='280px'))
            w_long = widgets.FloatText(description="Long (m):", value=30, style=style, layout=layout_sm)
            
            btn_add = widgets.Button(description="AGREGAR", button_style='info', icon='check', layout=widgets.Layout(width='100px'))
            
            box_entry = widgets.HBox([w_tag, w_kw, w_desc, w_long, btn_add])
            box_entry.layout.padding = '10px'
            box_entry.layout.border = '2px solid #2196F3' 
            
            # --- ZONA 2: CONFIGURACIÓN (ABAJO) ---
            lbl_conf = widgets.HTML("<b>2. CONFIGURACIÓN TÉCNICA:</b>")
            
            w_fases = widgets.Dropdown(options=[('3 Fases', 3), ('2 Fases', 2), ('1 Fase', 1)], value=3, description='Fases:', style=style, layout=layout_sm)
            w_tipo = widgets.Dropdown(options=[('Continua', TipoOperacion.CONTINUA), ('Respaldo', TipoOperacion.RESPALDO)], value=TipoOperacion.CONTINUA, description='Op:', style=style, layout=layout_sm)
            w_fp = widgets.FloatText(description="FP:", value=0.9, step=0.01, style=style, layout=layout_sm)
            
            w_tendido = widgets.Dropdown(
                options=[('Banco Ductos', 'DUCTO'), ('Bandeja', 'BANDEJA'), ('Red Aérea', 'TRENZADA')],
                value='DUCTO', description='Tendido:', style=style, layout=layout_md
            )
            w_mat = widgets.Dropdown(options=[('Aluminio', 'AL'), ('Cobre', 'CU')], value='AL', description='Mat:', style=style, layout=layout_sm)
            w_calibre = widgets.Dropdown(options=ORDEN_CALIBRES, value='4/0', description='Calibre:', style=style, layout=layout_sm)
            
            def on_tendido_change(change):
                if change['new'] == 'TRENZADA':
                    w_mat.value = 'AL'; w_mat.disabled = True
                else: w_mat.disabled = False
            w_tendido.observe(on_tendido_change, names='value')

            box_config = widgets.HBox([w_fases, w_tipo, w_fp, w_tendido, w_mat, w_calibre])
            box_config.layout.border = '1px solid #ddd'
            box_config.layout.padding = '8px'
            box_config.layout.margin = '5px 0px 10px 0px'
            
            # --- SALIDAS ---
            out_msg = widgets.Output() 
            out_tabla = widgets.Output()
            
            btn_finish = widgets.Button(description="TERMINAR ESTE TBT", button_style='warning', layout=widgets.Layout(width='100%'))

            # --- LÓGICA ---
            def actualizar_vista_tabla():
                with out_tabla:
                    clear_output()
                    if not self.tablero_actual.circuitos: return
                    
                    data = []
                    # Enumerar cargas (1, 2, 3...)
                    for i, c in enumerate(self.tablero_actual.circuitos): 
                        r = c._res_conductor
                        
                        # Datos Alternativos
                        alt_cfg = "-" if r['Prev_Desc'] == "N/A (Min)" else r['Prev_Desc']
                        alt_cap = "-" if alt_cfg == "-" else f"{r['Prev_Cap']:.1f}"
                        alt_reg = "-" if alt_cfg == "-" else f"{r['Prev_DV']:.2f}"
                        alt_mat = "-" if alt_cfg == "-" else r['Mat']
                        
                        tipo_txt = "CONT" if c.tipo_operacion == TipoOperacion.CONTINUA else "RESP"
                        
                        data.append({
                            "No.": i + 1,
                            "TAG": c.tag,
                            "DESCRIPCIÓN": c.descripcion,
                            "LONG (m)": c.longitud_mts,
                            "I_NOM (A)": f"{r['I_Nom']:.1f}",
                            # Configuración Seleccionada
                            "CONFIGURACIÓN": f"{r['N']}x{r['Calibre']}",
                            "MAT": r['Mat'],
                            "I_COND (A)": f"{r['Capacidad']:.1f}",
                            "TIPO": tipo_txt,
                            "TENDIDO": c.tipo_instalacion.value,
                            "REG %": f"{r['DV']:.2f}",
                            # Configuración Alternativa
                            "CFG_ALT": alt_cfg,
                            "MAT_ALT": alt_mat,
                            "REG_ALT %": alt_reg,
                            "I_COND_ALT": alt_cap
                        })
                    
                    df = pd.DataFrame(data)
                    cols = [
                        "No.", "TAG", "DESCRIPCIÓN", "LONG (m)", "I_NOM (A)", 
                        "CONFIGURACIÓN", "MAT", "I_COND (A)", "TIPO", "TENDIDO", "REG %",
                        "CFG_ALT", "MAT_ALT", "REG_ALT %", "I_COND_ALT"
                    ]
                    
                    pd.set_option('display.max_columns', None)
                    pd.set_option('display.width', 1000)
                    display(df[cols])

            def agregar_carga(b):
                if w_kw.value <= 0: return # Validación

                t_inst = TipoInstalacion.DUCTO
                if w_tendido.value == 'BANDEJA': t_inst = TipoInstalacion.AIRE
                elif w_tendido.value == 'TRENZADA': t_inst = TipoInstalacion.AIRE
                
                c = Circuito(w_tag.value, w_desc.value, w_kw.value, self.voltaje_sys,
                             w_fases.value, w_fp.value, w_tipo.value, w_long.value,
                             w_calibre.value, w_mat.value, t_inst)
                c.ejecutar_seleccion_conductor()
                self.tablero_actual.circuitos.append(c)
                
                actualizar_vista_tabla()
                with out_msg:
                    clear_output(wait=True)
                    print(f"✅ Carga {c.tag} agregada.")
                
                # Limpieza Variables
                w_tag.value = ""
                w_kw.value = 0
                w_desc.value = ""
                
            def terminar_tablero(b):
                self.pantalla_navegacion()

            w_tag.on_submit(agregar_carga)
            w_desc.on_submit(agregar_carga)
            btn_add.on_click(agregar_carga)
            btn_finish.on_click(terminar_tablero)
            
            display(widgets.VBox([
                lbl_data, box_entry,
                lbl_conf, box_config,
                out_msg,
                widgets.HTML("<hr>"),
                out_tabla,
                widgets.HTML("<br>"),
                btn_finish
            ]))

    def pantalla_navegacion(self):
        """PANTALLA 4: ÁRBOL DE DECISIÓN"""
        with contenedor_principal:
            clear_output()
            print(f"🤔 ¿QUÉ SIGUE TRAS '{self.tablero_actual.nombre}'?")
            print("="*60)
            
            btn_sub = widgets.Button(description=f"AGREGAR SUB-TABLERO (Hijo de {self.tablero_actual.nombre})", button_style='info')
            btn_main = widgets.Button(description="AGREGAR NUEVO TABLERO AL TRAFO", button_style='success')
            btn_end = widgets.Button(description="FINALIZAR PROYECTO", button_style='danger')
            
            def ir_sub(b):
                self.stack_parents.append(self.parent_actual)
                self.parent_actual = self.tablero_actual
                self.pantalla_crear_tablero()
                
            def ir_main(b):
                if self.stack_parents: self.parent_actual = self.stack_parents[0]
                else: self.parent_actual = self.trafo
                self.pantalla_crear_tablero()
                
            def finalizar(b):
                global SISTEMA_GLOBAL
                SISTEMA_GLOBAL = self.trafo
                clear_output()
                print("✅ PROYECTO GUARDADO EN MEMORIA.")
                print(f"   Nombre: {SISTEMA_GLOBAL.nombre}")
                print("   Puede proceder a los cálculos finales.")
                
            btn_sub.on_click(ir_sub)
            btn_main.on_click(ir_main)
            btn_end.on_click(finalizar)
            
            display(widgets.VBox([btn_sub, btn_main, btn_end]))

# Función pública para lanzar la GUI
def iniciar_interfaz():
    gestor = GestorFlujo()
    display(contenedor_principal)
    gestor.iniciar()
