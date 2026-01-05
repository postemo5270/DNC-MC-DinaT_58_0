def agregar_carga(b):
    """Calcula, guarda y agrega la fila al historial visual."""
    if num_p.value <= 0:
        # Mostramos error temporalmente sin borrar el historial si fuera posible,
        # pero para simplificar, lo mostramos al final del log.
        with out_msg: 
            display(widgets.HTML("<b style='color:red'>⚠️ Error: La potencia debe ser mayor a 0</b>"))
        return

    # Recuperamos el tablero actual
    t = backend.MEMORIA_TABLEROS[0]
    
    try:
        # 1. Crear el objeto Circuito
        c = backend.Circuito(
            tag=txt_tag.value, descripcion=txt_desc.value,
            p_input=num_p.value, unidad=dd_unit.value,
            tension=t.voltaje, fases=t.fases,
            fp=num_fp.value, eff=num_eff.value,
            longitud=num_len.value,
            mat="CU" if dd_mat.value == "Cobre" else "AL",
            tipo_aislam=dd_aisl.value, t_aislamiento_cable=dd_temp_cable.value,
            tipo_instalacion=dd_inst.value, req_neutro=dd_neutro.value,
            t_ambiente=num_temp.value
        )
        
        # 2. Ejecutar cálculos
        res = c.ejecutar_calculo()
        
        # 3. Guardar en la lista del tablero
        t.agregar_c(c)
        
        # 4. === NUEVO VISUALIZADOR DE LISTA ===
        # Obtenemos el número de item (consecutivo)
        item_id = len(t.circuitos)
        
        # Creamos una fila HTML con los datos solicitados
        fila_html = f"""
        <div style='border-bottom:1px solid #eee; padding:5px; font-family:sans-serif; font-size:13px; color:#2c3e50;'>
            <b style='color:#7f8c8d'>#{item_id}</b> | 
            <b style='color:#2980b9'>{c.tag}</b> | 
            {c.descripcion} | 
            <b>{c.p_input} {c.unidad}</b> | 
            L: {c.longitud}m 
            <span style='float:right; color:green; font-size:0.9em'>✅ Ok</span>
        </div>
        """
        
        with out_msg:
            # Si es la primera carga, ponemos un encabezado bonito
            if item_id == 1:
                clear_output(wait=True) # Borramos mensajes viejos o errores previos
                display(widgets.HTML("<div style='background:#ecf0f1; padding:5px; font-weight:bold; border-bottom:2px solid #bdc3c7; color:#2c3e50'>HISTORIAL DE CARGAS INGRESADAS:</div>"))
            
            # AGREGAMOS la nueva fila (Sin borrar lo anterior)
            display(widgets.HTML(fila_html))
            
        # 5. Limpiar campos para la siguiente
        txt_tag.value = ""
        txt_desc.value = ""
        num_p.value = 0.0
        # Ponemos el foco visualmente en Tag
        
    except Exception as e:
        with out_msg:
            display(widgets.HTML(f"<b style='color:red'>Error: {str(e)}</b>"))
