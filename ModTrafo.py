import ipywidgets as widgets
from IPython.display import display, clear_output, Markdown
import backend

# --- WIDGETS ---
style = widgets.Layout(width='98%')
drop_tableros = widgets.Dropdown(description="TABLERO:", layout=style, style={'description_width': 'initial'})
drop_tipo = widgets.Dropdown(options=[("Aceite Mineral", "ACEITE_MINERAL"), ("Seco", "SECO")], description="Tipo:", value="ACEITE_MINERAL", layout=style)
drop_refrig = widgets.Dropdown(options=["ONAN", "ONAF", "AN", "AF"], description="Refrig:", value="ONAN", layout=style)
num_v_pri = widgets.FloatText(description="V Pri:", value=13200, layout=widgets.Layout(width='48%'))
num_v_sec = widgets.FloatText(description="V Sec:", value=480, disabled=True, layout=widgets.Layout(width='48%'))
slide_res = widgets.FloatSlider(value=20, min=0, max=50, description='Reserva %:', layout=style)
btn_calc = widgets.Button(description="CALCULAR", button_style='danger', icon='bolt', layout=style)
out = widgets.Output()

def al_cambiar_tablero(change):
    if change['type'] == 'change' and change['name'] == 'value':
        backend.SISTEMA_PROYECTO = backend.MEMORIA_TABLEROS[change['new']]
        num_v_sec.value = backend.SISTEMA_PROYECTO.voltaje
        with out: clear_output()

drop_tableros.observe(al_cambiar_tablero, names='value')

def ejecutar(b):
    out.clear_output()
    tbt = backend.SISTEMA_PROYECTO
    kva, kw = tbt.calcular_carga_total()
    if kva <= 0:
        with out: print("⚠️ Tablero sin carga.")
        return
    tr = backend.Transformador(drop_tipo.value, drop_refrig.value, slide_res.value, num_v_pri.value, tbt.voltaje)
    res = tr.calcular(kva, kw)
    
    with out:
        display(Markdown(f"### Result: {tbt.nombre}"))
        print(f"Carga: {round(kva,1)} kVA | Req: {round(tr.kva_requerido,1)}")
        display(widgets.HTML(f"<h4 style='color:blue'>TRAFO: {res['kVA_Com']} kVA (Eff: {res['Eff']}%)</h4>"))
        print(f"I_Pri: {round(res['I_Pri'],1)}A | I_Sec: {round(res['I_Sec'],1)}A")

btn_calc.on_click(ejecutar)

def iniciar_modulo_trafo():
    if not backend.MEMORIA_TABLEROS: backend.MEMORIA_TABLEROS = [backend.SISTEMA_PROYECTO]
    drop_tableros.options = [(t.nombre, i) for i, t in enumerate(backend.MEMORIA_TABLEROS)]
    drop_tableros.value = 0
    display(widgets.HTML("<h3>🔌 SELECCIÓN DE TRANSFORMADOR</h3>"))
    display(drop_tableros)
    display(widgets.VBox([widgets.HBox([num_v_pri, num_v_sec]), drop_tipo, drop_refrig, slide_res, btn_calc, out]))
