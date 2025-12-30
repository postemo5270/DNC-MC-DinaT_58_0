import ipywidgets as widgets
from IPython.display import display, HTML
import backend

# =============================================================================
# MÓDULO DE REPORTE DE CONDUCTORES (FORMATO INGENIERÍA DETALLADA)
# =============================================================================

ESTILO_ANCHO = """
<style>
    .wide-table-container {
        overflow-x: auto; /* Scroll horizontal */
        width: 100%;
        margin-bottom: 30px;
        border: 1px solid #ccc;
    }
    .wide-table {
        font-family: 'Arial', sans-serif;
        font-size: 11px; /* Letra pequeña para que quepa todo */
        border-collapse: collapse;
        width: 100%;
        white-space: nowrap; /* Evita que rompa líneas en celdas */
    }
    .wide-table th {
        background-color: #2c3e50;
        color: white;
        padding: 8px 5px;
        text-align: center;
        border: 1px solid #999;
    }
    .wide-table td {
        padding: 5px;
        border: 1px solid #ddd;
        text-align: center;
        color: #333;
    }
    .wide-table tr:nth-child(even) { background-color: #f9f9f9; }
    .wide-table tr:hover { background-color: #eafaf1; }
    .header-row { font-weight: bold; background-color: #eee; text-align: left !important; padding: 10px; }
</style>
"""

def mostrar_reporte_conductores():
    lista_tbt = backend.MEMORIA_TABLEROS if backend.MEMORIA_TABLEROS else [backend.SISTEMA_PROYECTO]
    
    html = ESTILO_ANCHO
    html += "<h2>📊 CUADRO DE CARGAS Y CÁLCULO DE CONDUCTORES</h2>"
    
    for i_tbt, tbt in enumerate(lista_tbt):
        if not tbt.circuitos: continue
        
        html += f"<div class='header-row'>TABLERO: {tbt.nombre} ({tbt.voltaje}V - {tbt.fases}F)</div>"
        html += "<div class='wide-table-container'><table class='wide-table'>"
        
        # CABECERAS EXACTAS SEGÚN TU SOLICITUD
        html += """
        <thead>
            <tr>
                <th>Ítem</th>
                <th>Tag</th>
                <th>Descripción</th>
                <th>Tensión<br>[V]</th>
                <th>Sist.</th>
                <th>Pot.<br>[kW]</th>
                <th>Eff</th>
                <th>FP</th>
                <th>I_nom<br>[A]</th>
                <th>I_cond<br>(Ix1.25)</th>
                <th>Mat.</th>
                <th>Calibre</th>
                <th>Cap.<br>Base</th>
                <th>Canalización</th>
                <th>Derr.<br>Temp</th>
                <th>Derr.<br>BD</th>
                <th>Derr.<br>Total</th>
                <th>Configuración Cable</th>
                <th>Reg<br>%</th>
                <th>Cap.<br>Real</th>
            </tr>
        </thead>
        <tbody>
        """
        
        for idx, c in enumerate(tbt.circuitos):
            res = c._res_conductor if c._res_conductor else c.ejecutar_seleccion_conductor()
            
            # Formateo de datos
            sistema_str = f"{c.fases}F"
            pot_str = f"{c.potencia_nominal_kw}"
            i_nom_str = f"{round(res['I_Nom'], 1)}"
            i_req_str = f"{round(res['I_Req'], 1)}"
            cap_base_str = f"{res['Cap_Base']}"
            cap_real_str = f"{round(res['Cap_Real'], 1)}"
            
            html += f"""
            <tr>
                <td>{idx+1}</td>
                <td>{c.tag}</td>
                <td style='text-align:left'>{c.descripcion}</td>
                <td>{c.voltaje}</td>
                <td>{sistema_str}</td>
                <td>{pot_str}</td>
                <td>{c.eficiencia}</td>
                <td>{c.factor_potencia}</td>
                <td><b>{i_nom_str}</b></td>
                <td>{i_req_str}</td>
                <td>{c.material_conductor}</td>
                <td>{res['Calibre']}</td>
                <td>{cap_base_str}</td>
                <td>{c.tipo_instalacion.value}</td>
                <td>{res['F_Temp']}</td>
                <td>{res['F_Agrup']}</td>
                <td>{round(res['F_Total'], 2)}</td>
                <td style='text-align:left; font-family:monospace'>{res['Config']}</td>
                <td>{round(res['DV'], 2)}%</td>
                <td style='font-weight:bold; color:green'>{cap_real_str}</td>
            </tr>
            """
            
        html += "</tbody></table></div>"
    
    display(HTML(html))
